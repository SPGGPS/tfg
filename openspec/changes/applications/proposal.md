id: applications

schema: spec-driven
created: 2026-03-15

# Contexto: Gestión de Aplicaciones, Servicios y Mapa de Dependencias
context: |
  Feature: Application & Service Dependency Map
  Domain: Relación jerárquica entre URLs públicas, servicios, aplicaciones y activos de infraestructura.
  
  Motivation: El CMDB conoce los activos físicos/virtuales pero no la capa lógica que corre sobre
  ellos. Este módulo añade esa capa: permite modelar qué servicios ofrece el Ayuntamiento, qué
  aplicaciones los componen, sobre qué infraestructura corren, y cómo se conectan entre sí.
  
  El resultado es un grafo de dependencias navegable que responde preguntas como:
    - "Si cae srv-db-01, ¿qué servicios ciudadanos se ven afectados?"
    - "¿Qué pasa en producción si el cluster de Oracle tiene un fallo?"
    - "¿Cuál es la ruta completa desde la URL pública hasta la base de datos?"
    - "¿Qué aplicaciones dependen de Keycloak?"
  
  Stack: FastAPI, React, PostgreSQL. Visualización del grafo: React Flow (o D3.js).

# Definición del Cambio
proposal: |
  Implementar un módulo de gestión de aplicaciones y servicios con las siguientes entidades y vistas:

  1. ENTIDADES DEL MODELO:
     a. Application — una unidad de software desplegable con un rol dentro de un servicio
        (frontend, backend, auth, gateway, worker, scheduler, cache, cdn, other)
     b. Service — agrupación de aplicaciones que juntas ofrecen una capacidad al ciudadano
        (ej: "Sede Electrónica", "Portal de Empleo", "Wi-Fi Municipal")
     c. ServiceComponent — relación entre Service y Application con el rol que cumple
     d. AppInfraBinding — relación entre Application y Asset (los assets que la soportan)
     e. AppDependency — arista del grafo: una aplicación depende de otra aplicación o asset
     f. ServiceEndpoint — URLs o IPs públicas de entrada al servicio

  2. VISTAS DEL MÓDULO (entrada "Aplicaciones" en sidebar):
     a. Gestión de Aplicaciones — CRUD de aplicaciones
     b. Gestión de Servicios — CRUD de servicios y sus componentes
     c. Mapa de Dependencias — visualización del grafo completo o filtrado por servicio

  3. GRAFO DE DEPENDENCIAS:
     - Nodos: Service, Application, Asset (infra)
     - Aristas tipadas: COMPOSED_OF, HOSTED_ON, DEPENDS_ON, ROUTES_TO, SERVED_BY
     - Dirección: de nivel alto (URL) hacia nivel bajo (hardware)
     - Visualización interactiva: zoom, pan, click en nodo para ver detalle

# Modelo de datos
data_model: |
  certificates
  ────────────
  id            UUID PK
  common_name   VARCHAR(255) NOT NULL
  san_domains   JSON DEFAULT []
  issuer        VARCHAR(255)
  issued_at     DATE
  expires_at    DATE NOT NULL INDEX          -- crítico: alertas de caducidad
  serial_number VARCHAR(100)
  key_type      ENUM(rsa_2048, rsa_4096, ecdsa_256, ecdsa_384, ed25519, other)
  wildcard      BOOLEAN DEFAULT false
  auto_renew    BOOLEAN DEFAULT false
  managed_by    VARCHAR(100)               -- cert-manager, manual, keycloak...
  environment   ENUM(production, staging, development, dr)
  notes         TEXT
  created_at    TIMESTAMPTZ
  updated_at    TIMESTAMPTZ
  status [calculado] ENUM(valid, expiring, critical, expired)  -- no almacenado
  days_remaining [calculado] INTEGER                           -- no almacenado

  applications
  ─────────────
  id            UUID PK
  name          VARCHAR(200) NOT NULL UNIQUE
  description   TEXT
  version       VARCHAR(50)
  repo_url      VARCHAR(500)
  docs_url      VARCHAR(500)
  tech_stack    JSON DEFAULT []
  owner_team    VARCHAR(100)
  environment   ENUM(production, staging, development, dr)
  status        ENUM(active, inactive, deprecated, maintenance)
  created_at    TIMESTAMPTZ
  updated_at    TIMESTAMPTZ

  services
  ─────────
  id            UUID PK
  name          VARCHAR(200) NOT NULL UNIQUE
  description   TEXT
  category      ENUM(citizen_portal, internal_tool, infrastructure, integration, other)
  status        ENUM(active, degraded, maintenance, inactive)
  owner_team    VARCHAR(100)
  criticality   ENUM(critical, high, medium, low)
  created_at    TIMESTAMPTZ
  updated_at    TIMESTAMPTZ

  service_endpoints
  ─────────────────
  id            UUID PK
  service_id    FK → services.id ON DELETE CASCADE
  url           VARCHAR(500)
  type          ENUM(public, internal, vpn, api, webhook)
  description   VARCHAR(200)
  is_primary    BOOLEAN DEFAULT false

  service_components
  ──────────────────
  id              UUID PK
  service_id      FK → services.id ON DELETE CASCADE
  application_id  FK → applications.id ON DELETE CASCADE
  role            ENUM(frontend, backend, api_gateway, auth, worker, scheduler,
                       cache, cdn, database_proxy, message_broker, monitoring,
                       ingress, load_balancer, other)
  role_notes      VARCHAR(200)
  order_index     INTEGER DEFAULT 0
  UNIQUE(service_id, application_id)

  app_infra_bindings                   -- ACTUALIZADO con tier y SPF
  ──────────────────
  id                        UUID PK
  application_id            FK → applications.id ON DELETE CASCADE
  asset_id                  FK → assets.id ON DELETE SET NULL    -- nullable
  certificate_id            FK → certificates.id ON DELETE SET NULL -- nullable
  binding_tier              ENUM(entry_point, gateway, certificate, application,
                                 auth, cache, data, compute, storage, network) NOT NULL
  tier_order_override       INTEGER NULL  -- sobrescribe el orden canónico del tier
  is_critical               BOOLEAN DEFAULT true
  is_single_point_of_failure BOOLEAN DEFAULT false
  redundancy_group          VARCHAR(100) NULL INDEX  -- agrupa assets redundantes
  notes                     VARCHAR(300)
  CHECK: (asset_id IS NOT NULL AND certificate_id IS NULL)
      OR (asset_id IS NULL AND certificate_id IS NOT NULL)
  UNIQUE(application_id, asset_id, binding_tier)  -- cuando asset_id no es null
  UNIQUE(application_id, certificate_id)           -- cuando certificate_id no es null

  app_dependencies
  ────────────────
  id                UUID PK
  source_app_id     FK → applications.id ON DELETE CASCADE
  target_app_id     FK → applications.id ON DELETE CASCADE
  dep_type          ENUM(calls_api, authenticates_via, reads_from, writes_to,
                         publishes_to, subscribes_to, proxied_through, other)
  is_critical       BOOLEAN DEFAULT true
  notes             VARCHAR(200)
  CHECK(source_app_id != target_app_id)
  UNIQUE(source_app_id, target_app_id, dep_type)

# Reglas de implementación
rules:
  openapi_spec:
    - CRUD completo para /v1/applications, /v1/services bajo rol editor+.
    - Gestión de componentes: POST/DELETE /v1/services/{id}/components
    - Gestión de bindings infra: POST/DELETE /v1/applications/{id}/infra-bindings
    - Gestión de dependencias: POST/DELETE /v1/applications/{id}/dependencies
    - Endpoint de grafo: GET /v1/services/{id}/dependency-graph devuelve nodos + aristas
      para renderizar en React Flow. También GET /v1/dependency-graph global.
    - Todos los endpoints requieren JWT. Rol viewer para lectura, editor para escritura.

  backend_code:
    - Validar que no se crean ciclos en app_dependencies (grafo acíclico dirigido — DAG).
    - El endpoint /dependency-graph construye el grafo completo en memoria:
        nodos: {id, type: "service"|"application"|"asset", label, status, ...}
        aristas: {id, source, target, label, type, is_critical}
    - Registrar en audit_logs creación/eliminación de servicios, aplicaciones y bindings.
    - El campo 'criticality' de servicio y 'is_critical' de dependencia se usan para
      colorear el grafo (rojo = crítico, naranja = high, etc.).

  frontend_code:
    - Nueva entrada "Aplicaciones" en el sidebar, visible para viewer+.
      Icono: cubo o nodo de red. Posición: entre Inventario y Etiquetas.
    - Tres sub-páginas accesibles desde tabs dentro de /applications:
        1. "Aplicaciones" — tabla CRUD
        2. "Servicios" — tabla CRUD + gestión de componentes
        3. "Mapa de Dependencias" — visualización del grafo
    - El mapa usa React Flow para renderizar el grafo interactivo.
    - Colores de nodos por tipo: Service (azul corporativo), Application (verde),
      Asset infra (gris), con borde rojo si criticality=critical o status=degraded.
    - Click en nodo abre panel lateral con detalle del nodo sin abandonar el mapa.

# Dependencias
dependencies:
  - inventory-master   # necesita el modelo Asset para los bindings infra
  - login              # requiere JWT con roles
  - audit-logs         # registra cambios en audit_logs

# Desglose de tareas
tasks:
  - name: "DB: Modelos applications, services, service_endpoints, service_components"
    hours: 3
  - name: "DB: Modelos app_infra_bindings, app_dependencies con validación DAG"
    hours: 2
  - name: "Backend: CRUD /v1/applications y /v1/services con audit trail"
    hours: 4
  - name: "Backend: Endpoints de componentes, bindings y dependencias"
    hours: 3
  - name: "Backend: Endpoint /dependency-graph con construcción del grafo"
    hours: 3
  - name: "Frontend: Página Gestión de Aplicaciones (tabla CRUD)"
    hours: 3
  - name: "Frontend: Página Gestión de Servicios con componentes y endpoints"
    hours: 4
  - name: "Frontend: Mapa de Dependencias con React Flow"
    hours: 6
