# API - Applications, Services & Infrastructure Topology

## ADDED Requirements

---

### Requirement: Enum BindingTier — capas de infraestructura con orden canónico

El sistema SHALL definir el enum `BindingTier` con las siguientes capas, cada una con un `tier_order` por defecto. Este orden determina la posición vertical en el mapa de topología (1 = más arriba = más cercano al usuario).

| Valor enum | tier_order | Descripción | Assets típicos |
|------------|-----------|-------------|----------------|
| `entry_point` | 1 | Punto de entrada público — URL, IP, dominio | ServiceEndpoint, DNS, CDN |
| `gateway` | 2 | Proxy, ingress, load balancer, API gateway | Traefik, Nginx, HAProxy, F5 |
| `certificate` | 3 | Certificados TLS/SSL — gestión y terminación | Cert-manager, Let's Encrypt, HSM |
| `application` | 4 | Aplicaciones, frontends, backends, workers | VMs, contenedores con apps |
| `auth` | 4 | Proveedor de identidad, SSO, gestión de tokens | Keycloak, LDAP, SAML IdP |
| `cache` | 5 | Caché de datos en memoria | Redis, Memcached, Varnish |
| `data` | 5 | Bases de datos, brokers de mensajes, object storage | PostgreSQL, Kafka, MinIO |
| `compute` | 6 | Servidores físicos o virtuales que alojan las capas superiores | server_physical, server_virtual |
| `storage` | 7 | Almacenamiento en red, SANs, NAS, backups | NAS, SAN, Veeam target |
| `network` | 8 | Infraestructura de red — switching, routing, firewall, wireless | switch, router, firewall, ap |

Notas:
- `application` y `auth` comparten `tier_order=4` intencionalmente — son el mismo nivel lógico.
- `cache` y `data` comparten `tier_order=5` — almacenamiento activo del mismo nivel.
- El campo `tier_order_override` en `AppInfraBinding` permite sobrescribir el valor por defecto para casos especiales.

---

### Requirement: Modelo Certificate — certificados TLS/SSL

Los certificados son activos de primera clase en la topología. El sistema SHALL exponer un CRUD completo bajo `/v1/certificates`.

**Tabla `certificates` — modelo completo:**

*Identificación del certificado:*
- `id` (UUID PK)
- `common_name` (string, max 255) — CN del certificado, ej: `sede.ssreyes.es`
- `san_domains` (JSON array) — Subject Alternative Names, ej: `["sede.ssreyes.es", "api.ssreyes.es"]`
- `serial_number` (string, max 100) — número de serie en formato hexadecimal, ej: `03:A1:4F:...`
- `fingerprint_sha256` (string, max 100) — huella SHA-256, ej: `AA:BB:CC:...` — identifica de forma única el cert
- `fingerprint_sha1` (string, max 60) — huella SHA-1 (legacy, para compatibilidad)

*Vigencia:*
- `issued_at` (date, nullable) — fecha de emisión
- `expires_at` (date, **obligatorio, INDEX**) — fecha de caducidad — **campo crítico para alertas**
- `not_before` (date, nullable) — fecha desde la que el cert es válido (suele coincidir con issued_at)

*Entidad certificadora (CA):*
- `issuer` (string, max 255) — nombre del emisor tal como aparece en el cert, ej: `R11`, `FNMT Clase 2 CA`, `DigiCert TLS RSA SHA256 2020 CA1`
- `issuer_common_name` (string, max 255) — CN del emisor, ej: `Let's Encrypt`, `FNMT`, `DigiCert`
- `issuer_organization` (string, max 255) — O del emisor, ej: `Let's Encrypt`, `FNMT-RCM`, `DigiCert Inc`
- `issuer_country` (string(2), nullable) — país del emisor, ej: `US`, `ES`
- `ca_type` (enum) — tipo de CA:
  - `public_trusted` — CA pública reconocida por navegadores (Let's Encrypt, DigiCert, Sectigo…)
  - `fnmt` — FNMT española (Fábrica Nacional de Moneda y Timbre)
  - `internal_ca` — CA interna del Ayuntamiento
  - `self_signed` — autofirmado
  - `unknown`

*Sujeto del certificado (Subject):*
- `subject_organization` (string, max 255, nullable) — O del sujeto, ej: `Ayuntamiento de San Sebastián de los Reyes`
- `subject_organizational_unit` (string, max 255, nullable) — OU del sujeto, ej: `Sistemas TIC`
- `subject_country` (string(2), nullable) — país del sujeto, ej: `ES`
- `subject_state` (string, max 100, nullable) — comunidad autónoma, ej: `Madrid`
- `subject_locality` (string, max 100, nullable) — municipio, ej: `San Sebastián de los Reyes`

*Criptografía:*
- `key_type` (enum: `rsa_2048` | `rsa_4096` | `ecdsa_256` | `ecdsa_384` | `ed25519` | `other`)
- `signature_algorithm` (string, max 100, nullable) — ej: `sha256WithRSAEncryption`, `ecdsa-with-SHA384`
- `wildcard` (bool, default false) — es wildcard `*.dominio.es`

*Extensiones X.509:*
- `key_usages` (JSON array, nullable) — usos de la clave: `["digitalSignature", "keyEncipherment"]`
- `extended_key_usages` (JSON array, nullable) — usos extendidos: `["serverAuth", "clientAuth"]`
- `ocsp_url` (string, max 500, nullable) — URL del respondedor OCSP para validación en línea
- `crl_url` (string, max 500, nullable) — URL de la lista de revocación (CRL)
- `ca_issuers_url` (string, max 500, nullable) — URL para descargar el certificado de la CA intermedia
- `is_ca` (bool, default false) — este certificado es él mismo una CA (Basic Constraints: CA:TRUE)
- `chain_valid` (bool, nullable) — la cadena de confianza hasta la CA raíz fue verificada en la última sync

*Gestión:*
- `auto_renew` (bool, default false) — renovación automática activa (cert-manager, ACME)
- `managed_by` (string, max 100) — sistema que lo gestiona: `cert-manager`, `manual`, `keycloak`, `fnmt-portal`, etc.
- `acme_account` (string, max 255, nullable) — cuenta ACME asociada (si se usa Let's Encrypt / cert-manager)
- `environment` (enum: production | staging | development | dr)
- `notes` (text, nullable) — notas libres del administrador

*Metadatos:*
- `source` (string, max 100, nullable) — origen del dato: `apache-flow`, `manual`, `cert-manager-api`, etc.
- `last_verified_at` (datetime, nullable) — última vez que se verificó el estado real del certificado (via Apache Flow u otro proceso)
- `created_at`, `updated_at` (TIMESTAMPTZ)

**Estado calculado (no almacenado, calculado en respuesta):**
```
cert_status:
  valid     → expires_at > today + 30 días
  expiring  → expires_at entre today y today + 30 días  ← ALERTA NARANJA
  critical  → expires_at entre today y today + 7 días   ← ALERTA ROJA
  expired   → expires_at <= today                        ← CRÍTICO
```

**`days_remaining`** (calculado): entero, puede ser negativo si expirado.

**Endpoints:**
- `GET    /v1/certificates` — listar con filtros: `status`, `environment`, `ca_type`, `search` (common_name, issuer, san_domains, subject_organization), `expiring_days`
- `GET    /v1/certificates/{id}` — detalle completo con estado calculado, servicios y endpoints que lo usan
- `POST   /v1/certificates` — crear certificado (entrada manual inicial; Apache Flow lo enriquecerá)
- `PUT    /v1/certificates/{id}` — actualizar certificado
- `DELETE /v1/certificates/{id}` — eliminar (409 si está vinculado a endpoints de servicio activos)
- `GET    /v1/certificates/expiry-summary` — resumen de estados

**Respuesta de GET /v1/certificates/{id} incluye adicionalmente:**
- `cert_status` y `days_remaining` calculados
- `services_using`: lista de servicios cuyos endpoints usan este certificado, con el endpoint concreto
- `applications_using`: lista de aplicaciones vinculadas vía AppInfraBinding con binding_tier=certificate

#### Scenario: Certificado FNMT con datos de sujeto completos
- **GIVEN** un certificado con ca_type="fnmt", subject_organization="Ayuntamiento de SSReyes", subject_country="ES"
- **WHEN** GET /v1/certificates/{id}
- **THEN** la respuesta incluye todos los campos de sujeto y emisor, y ca_type="fnmt"

#### Scenario: Certificado con cadena inválida
- **GIVEN** un certificado con chain_valid=false
- **WHEN** se muestra en la tabla
- **THEN** aparece un badge adicional "⚠ Cadena inválida" junto al estado de caducidad

#### Scenario: Listar solo certificados FNMT
- **GIVEN** GET /v1/certificates?ca_type=fnmt
- **THEN** devuelve solo certificados con ca_type=fnmt

#### Scenario: Certificado referenciado por servicio — no se puede eliminar
- **GIVEN** el certificado "sede.ssreyes.es" está vinculado al endpoint del servicio "Sede Electrónica"
- **WHEN** DELETE /v1/certificates/{id}
- **THEN** responde 409 con mensaje "Certificate is in use by services: [Sede Electrónica]"

#### Scenario: Campo source indica origen Apache Flow
- **GIVEN** un certificado con source="apache-flow" y last_verified_at reciente
- **WHEN** se muestra en la tabla
- **THEN** la columna "Origen" muestra un badge "Apache Flow" con la fecha de última verificación

---

### Requirement: Gestión de bindings de infraestructura (Application ↔ Asset) — modelo extendido con tier

El binding entre una Application y un Asset ahora incluye información de **capa (tier)**, **criticidad** y **punto de fallo único**. Este es el corazón del mapa de topología.

**Endpoints:**
- `GET    /v1/applications/{id}/infra-bindings` — listar assets vinculados con tier y criticidad
- `POST   /v1/applications/{id}/infra-bindings` — vincular asset a aplicación con tier
- `PUT    /v1/applications/{id}/infra-bindings/{binding_id}` — actualizar tier, criticidad o notas
- `DELETE /v1/applications/{id}/infra-bindings/{binding_id}` — desvincular

**Body POST/PUT:**
- `asset_id` (UUID, obligatorio — debe existir en assets)
- `binding_tier` (enum BindingTier, obligatorio) — capa canónica del asset en este contexto
- `tier_order_override` (int | null, opcional) — sobrescribe el tier_order por defecto del enum
- `is_critical` (bool, default true) — si este asset falla, ¿cae la aplicación?
- `is_single_point_of_failure` (bool, default false) — no existe redundancia para este asset
- `redundancy_group` (string | null, opcional) — agrupa assets redundantes entre sí, ej: `"pg-cluster-prod"`. Assets del mismo grupo se consideran redundantes: si uno falla, los otros cubren.
- `notes` (string, opcional, max 300)

**Respuesta de GET incluye además:**
- `asset_name`, `asset_type`, `asset_ips` — campos del asset para no requerir llamada extra
- `tier_order_effective` — tier_order real usado (override si existe, canónico si no)
- `certificate_id` — si binding_tier=`certificate`, referencia al Certificate asociado

**Endpoint adicional para certificados:**
- `POST /v1/applications/{id}/infra-bindings` con `binding_tier="certificate"` y `certificate_id` en lugar de `asset_id`

#### Scenario: Vincular servidor con tier compute, crítico y SPF
- **GIVEN** la aplicación "sede-api" y el asset "srv-app-01"
- **WHEN** POST con asset_id, binding_tier="compute", is_critical=true, is_single_point_of_failure=true
- **THEN** responde 201 con tier_order_effective=6 y los campos SPF

#### Scenario: Vincular dos servidores redundantes
- **GIVEN** "srv-app-01" y "srv-app-02" ambos con binding_tier="compute" y redundancy_group="app-cluster"
- **WHEN** se consultan los bindings de la aplicación
- **THEN** ambos aparecen con is_single_point_of_failure=false implícito (hay redundancia en el grupo)

#### Scenario: Vincular certificado a aplicación
- **GIVEN** un certificado "sede.ssreyes.es" y la aplicación "sede-frontend"
- **WHEN** POST con binding_tier="certificate" y certificate_id="uuid-cert"
- **THEN** responde 201 con el binding de tipo certificado

#### Scenario: Tier override para caso especial
- **GIVEN** un Redis usado como cola de mensajes (normalmente tier=cache, order=5) pero en este servicio actúa como broker (debería estar en order=4)
- **WHEN** POST con binding_tier="cache" y tier_order_override=4
- **THEN** tier_order_effective=4, el mapa lo muestra en la capa 4

---

### Requirement: CRUD /v1/applications (sin cambios en endpoints, actualización de campos)

Igual que antes. Se añaden campos opcionales al body:
- `certificate_ids` (array de UUIDs, opcional) — certificados asociados directamente a la aplicación (ej. si la app gestiona su propio TLS)

---

### Requirement: CRUD /v1/services (sin cambios en endpoints)

Sin cambios. El campo `criticality` se propaga al análisis de impacto.

---

### Requirement: Gestión de endpoints de servicio — campo certificate_id y estado TLS

El modelo `ServiceEndpoint` SHALL incluir un campo `certificate_id` (FK opcional a `certificates.id`) que indica qué certificado TLS protege este endpoint. Si `certificate_id` es null, el endpoint se considera **sin TLS** y el sistema lo muestra con un indicador visual claro.

**Campos actualizados de ServiceEndpoint:**
- `url` (string, obligatorio, max 500)
- `type` (enum: public | internal | vpn | api | webhook, obligatorio)
- `description` (string, opcional, max 200)
- `is_primary` (bool, default false)
- `certificate_id` (string UUID | null) — FK a `certificates.id` ON DELETE SET NULL. Si null → endpoint sin TLS.

**Estado TLS del endpoint** (calculado en la respuesta, no almacenado):
```
tls_status:
  none      → certificate_id IS NULL                    → sin TLS
  valid     → certificate vinculado con cert_status=valid
  expiring  → certificate vinculado con cert_status=expiring
  critical  → certificate vinculado con cert_status=critical
  expired   → certificate vinculado con cert_status=expired
```

**La respuesta de GET /v1/services/{id}** incluye en cada endpoint:
```json
{
  "id": "uuid",
  "url": "https://sede.ssreyes.es",
  "type": "public",
  "is_primary": true,
  "certificate_id": "cert-uuid",
  "certificate": {
    "id": "cert-uuid",
    "common_name": "sede.ssreyes.es",
    "san_domains": ["sede.ssreyes.es", "api.ssreyes.es"],
    "issuer": "Let's Encrypt",
    "issued_at": "2025-12-15",
    "expires_at": "2026-03-15",
    "days_remaining": 0,
    "cert_status": "expired",
    "wildcard": false,
    "auto_renew": true,
    "managed_by": "cert-manager",
    "key_type": "ecdsa_256",
    "serial_number": "03:A1:...",
    "organization": "Ayuntamiento de San Sebastián de los Reyes",
    "organizational_unit": "Sistemas",
    "country": "ES",
    "chain_valid": true,
    "fingerprint_sha256": "AA:BB:CC:..."
  },
  "tls_status": "expired"
}
```

**Endpoints:**
- `GET    /v1/services/{id}/endpoints` — lista con el objeto `certificate` embebido si existe
- `POST   /v1/services/{id}/endpoints` — body incluye `certificate_id` (opcional)
- `PUT    /v1/services/{id}/endpoints/{endpoint_id}` — permite cambiar o quitar el certificado
- `DELETE /v1/services/{id}/endpoints/{endpoint_id}` — elimina el endpoint; el Certificate no se elimina

#### Scenario: Endpoint público con certificado válido
- **GIVEN** POST con url="https://sede.ssreyes.es", certificate_id="uuid-cert-valido"
- **WHEN** se consulta GET /v1/services/{id}/endpoints
- **THEN** el endpoint incluye el objeto certificate completo y tls_status="valid"

#### Scenario: Endpoint sin certificado — sin TLS
- **GIVEN** POST con url="http://interno.ssreyes.local" sin certificate_id
- **WHEN** se consulta el servicio
- **THEN** tls_status="none" y certificate=null

#### Scenario: Certificado expirado vinculado a endpoint público
- **GIVEN** un endpoint público con certificate_id apuntando a un cert expirado
- **WHEN** GET /v1/services/{id}
- **THEN** tls_status="expired" y el servicio propaga una alerta en el grafo de dependencias

#### Scenario: Desvincular certificado de endpoint (quitar TLS)
- **GIVEN** un endpoint con certificate_id relleno
- **WHEN** PUT /v1/services/{id}/endpoints/{eid} con certificate_id=null
- **THEN** tls_status="none"; el Certificate permanece intacto en la tabla certificates

---

### Requirement: Gestión de componentes de servicio (sin cambios)

Sin cambios respecto al spec anterior.

---

### Requirement: Gestión de dependencias entre aplicaciones (sin cambios)

Sin cambios respecto al spec anterior.

---

### Requirement: Endpoint /v1/certificates/expiry-summary — resumen de caducidades

`GET /v1/certificates/expiry-summary` devuelve un resumen rápido para el dashboard:

```json
{
  "total": 24,
  "valid": 18,
  "expiring_soon": 4,
  "critical": 1,
  "expired": 1,
  "next_expiry": { "id": "uuid", "common_name": "sede.ssreyes.es", "expires_at": "2026-04-10", "days_remaining": 26 }
}
```

#### Scenario: Dashboard con certificados críticos
- **GIVEN** 1 certificado expira en 3 días
- **WHEN** GET /v1/certificates/expiry-summary
- **THEN** critical=1, next_expiry apunta a ese certificado

---

### Requirement: Endpoint /dependency-graph — grafo con capas y certificados

**Endpoints:**
- `GET /v1/dependency-graph` — grafo global
- `GET /v1/services/{id}/dependency-graph` — grafo de un servicio

**Query params:**
- `include_assets` (bool, default true) — incluir nodos de infraestructura
- `include_certificates` (bool, default true) — incluir nodos de certificados
- `include_inactive` (bool, default false) — incluir inactivos
- `highlight_spf` (bool, default true) — marcar single points of failure
- `view` (enum: layered | graph, default layered) — modo de renderizado sugerido

**Nodos en la respuesta — campos adicionales:**

Para nodos de tipo `asset`:
```json
{
  "id": "ast-uuid",
  "node_type": "asset",
  "label": "srv-app-01",
  "asset_type": "server_virtual",
  "ips": ["10.0.1.20"],
  "binding_tier": "compute",
  "tier_order": 6,
  "is_critical": true,
  "is_single_point_of_failure": true,
  "redundancy_group": null,
  "compliance_ok": true
}
```

Para nodos de tipo `certificate`:
```json
{
  "id": "cert-uuid",
  "node_type": "certificate",
  "label": "sede.ssreyes.es",
  "binding_tier": "certificate",
  "tier_order": 3,
  "status": "expiring",
  "days_remaining": 12,
  "expires_at": "2026-03-27",
  "issuer": "Let's Encrypt",
  "is_critical": true,
  "is_single_point_of_failure": false
}
```

**Aristas — tipo nuevo:**
- `SECURED_BY` — Application o Asset usa este Certificate

**Campo adicional en la respuesta raíz:**
```json
{
  "nodes": [...],
  "edges": [...],
  "tiers": [
    { "tier_order": 1, "label": "Punto de entrada",  "binding_tier": "entry_point" },
    { "tier_order": 2, "label": "Gateway / Proxy",   "binding_tier": "gateway" },
    { "tier_order": 3, "label": "Certificados TLS",  "binding_tier": "certificate" },
    { "tier_order": 4, "label": "Aplicación / Auth", "binding_tier": "application" },
    { "tier_order": 5, "label": "Datos / Caché",     "binding_tier": "data" },
    { "tier_order": 6, "label": "Cómputo",           "binding_tier": "compute" },
    { "tier_order": 7, "label": "Almacenamiento",    "binding_tier": "storage" },
    { "tier_order": 8, "label": "Red",               "binding_tier": "network" }
  ],
  "spf_nodes": ["ast-uuid-1", "ast-uuid-2"],
  "expiring_certificates": ["cert-uuid-1"]
}
```

El campo `tiers` permite al frontend renderizar los carriles horizontales dinámicamente sin hardcodear las capas.

#### Scenario: Grafo con single points of failure resaltados
- **GIVEN** router-edge-01 con is_single_point_of_failure=true en el servicio "Sede Electrónica"
- **WHEN** GET /v1/services/{id}/dependency-graph?highlight_spf=true
- **THEN** router-edge-01 aparece en spf_nodes y su nodo incluye is_single_point_of_failure=true

#### Scenario: Grafo vista layered con certificados
- **GIVEN** el servicio tiene un certificado expirando en 12 días
- **WHEN** GET /v1/services/{id}/dependency-graph?include_certificates=true
- **THEN** el certificado aparece como nodo en tier_order=3 con status="expiring" y su arista SECURED_BY

#### Scenario: Mapa de impacto — ¿qué cae si falla srv-db-01?
- **GIVEN** srv-db-01 tiene is_single_point_of_failure=true y es_critical=true en la app "sede-api"
- **WHEN** se analiza el grafo transitivo hacia arriba desde srv-db-01
- **THEN** se puede trazar: srv-db-01 → sede-api → Sede Electrónica (servicio crítico afectado)
