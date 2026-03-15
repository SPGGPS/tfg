# Tasks — Applications, Services & Infrastructure Topology

## Bloque 1 — Base de datos y modelos (5h)
- [ ] Definir enums: AppEnvironment, AppStatus, ServiceStatus, ServiceCriticality,
      ServiceCategory, ComponentRole, BindingTier (con TIER_ORDER y TIER_LABELS), DepType, EndpointType, KeyType
- [ ] Implementar modelo Certificate con cert_status y days_remaining calculados
- [ ] Implementar modelos Application, Service, ServiceEndpoint, ServiceComponent
- [ ] Actualizar AppInfraBinding: binding_tier, tier_order_override, is_critical,
      is_single_point_of_failure, redundancy_group, certificate_id
- [ ] CheckConstraint asset XOR certificate en AppInfraBinding
- [ ] Implementar AppDependency
- [ ] Registrar todos los modelos en app/models/__init__.py
- [ ] Añadir índices: certificates.expires_at, app_infra_bindings.redundancy_group

## Bloque 2 — Backend CRUD aplicaciones y servicios (4h)
- [ ] Router /v1/applications: GET list (con search por tech_stack), GET detail, POST, PUT, DELETE
- [ ] Router /v1/services: GET list, GET detail, POST, PUT, DELETE en cascada
- [ ] Endpoints service_endpoints: GET, POST (is_primary único por servicio), DELETE
- [ ] Endpoints service_components: GET, POST (validar unicidad + role_notes si other), PUT, DELETE
- [ ] Audit trail en todas las mutaciones

## Bloque 3 — Backend certificados (3h)
- [ ] Router /v1/certificates: GET list (con filtros status, expiring_days), GET detail,
      POST, PUT, DELETE (409 si tiene bindings)
- [ ] GET /v1/certificates/expiry-summary con contadores y next_expiry
- [ ] Ordenación por expires_at ASC en el listado
- [ ] Añadir router al main.py

## Bloque 4 — Backend bindings e infra topology (4h)
- [ ] Actualizar router app_infra_bindings con binding_tier, tier_order_override, is_critical,
      is_single_point_of_failure, redundancy_group, certificate_id
- [ ] Validaciones: asset XOR certificate según binding_tier, existencia de asset/cert, unicidad
- [ ] Propiedad tier_order_effective en el modelo
- [ ] Endpoints app_dependencies: GET, POST (con DAG check), DELETE
- [ ] GET /v1/assets/{id}/impact — análisis de impacto transitivo

## Bloque 5 — Backend dependency-graph actualizado (3h)
- [ ] Actualizar _build_graph: nodos con binding_tier, tier_order, is_critical, is_spf, redundancy_group
- [ ] Añadir nodos de tipo certificate cuando include_certificates=True
- [ ] Añadir aristas SECURED_BY para bindings de certificado
- [ ] Calcular campo tiers dinámico (solo tiers presentes en el grafo)
- [ ] Calcular campos spf_nodes y expiring_certificates en la respuesta raíz
- [ ] Query params: include_certificates, highlight_spf, view
- [ ] Optimizar con joinedload para evitar N+1

## Bloque 6 — Frontend Tab "Aplicaciones" (3h)
- [ ] Tabla de aplicaciones con filtros
- [ ] Modal crear/editar con tech_stack como chips
- [ ] Sección de infra bindings en detalle de app: tabla por tiers con formulario extendido
- [ ] Toggle asset/certificado en formulario de binding
- [ ] Selector de binding_tier con botones de colores y tier_order canónico
- [ ] Toggles is_critical, is_spf, campo redundancy_group
- [ ] Sección de dependencias outgoing/incoming

## Bloque 7 — Frontend Tab "Certificados" (3h)
- [ ] Banner de resumen con contadores (valid, expiring, critical, expired)
- [ ] Tabla con badges de estado por color, columna días restantes con colores dinámicos
- [ ] Alerta sticky cuando hay críticos o expirados
- [ ] Modal crear/editar con san_domains como chips
- [ ] Filtros por estado y entorno

## Bloque 8 — Frontend Tab "Servicios" actualizado (2h)
- [ ] Sección "Infraestructura del servicio" en detalle de servicio, agrupada por capas
- [ ] Mini-tabla de capas con assets, badges de compliance e indicadores SPF/redundancia

## Bloque 9 — Frontend Mapa de Topología actualizado (5h)
- [ ] Toggle Vista Capas / Vista Grafo
- [ ] Vista de Capas: carriles horizontales por tier_order, colores de carril por tier
- [ ] Nodos de certificado en carril tier=3 con estado visual
- [ ] Borde naranja pulsante para SPFs, borde rojo pulsante para certs críticos
- [ ] Panel lateral con análisis de impacto (llamada a /v1/assets/{id}/impact)
- [ ] Toggle "Solo puntos de fallo único" — muestra solo la ruta crítica
- [ ] Toggle "Mostrar certificados"
- [ ] Widget de alertas en cabecera cuando hay SPFs o certs problemáticos
- [ ] Leyenda actualizada con todos los tipos de nodo y arista
- [ ] Botón exportar PNG
