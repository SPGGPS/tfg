# API - Inventario y activos

## ADDED Requirements

### Requirement: Modelo Asset polimórfico

El modelo Asset SHALL incluir un discriminador 'type' con valores server_physical, server_virtual, switch, router, ap.

#### Scenario: Tipos de activo soportados
- **GIVEN** un activo en el inventario
- **WHEN** se consulta su tipo
- **THEN** el campo type debe ser uno de: server_physical, server_virtual, switch, router, ap

### Requirement: Endpoint POST /v1/assets/bulk-tags

El sistema SHALL exponer POST /v1/assets/bulk-tags para asignar etiquetas manuales a múltiples asset_ids simultáneamente.

#### Scenario: Asignación masiva exitosa
- **GIVEN** un admin con asset_ids y tag_ids válidos
- **WHEN** realiza POST /v1/assets/bulk-tags con esos IDs
- **THEN** todos los activos reciben las etiquetas especificadas

### Requirement: Campos de cumplimiento en Asset

El modelo Asset SHALL incluir los campos obligatorios de compliance y estado:
- `edr_installed` (bool)
- `last_backup` (datetime)
- `monitored` (bool)
- `logs_enabled` (bool)
- `last_sync` (datetime) - timestamp de la última sincronización de datos

#### Scenario: Respuesta con compliance
- **GIVEN** un cliente que consulta GET /v1/assets
- **WHEN** recibe la respuesta
- **THEN** cada activo incluye los campos edr_installed, last_backup, monitored, logs_enabled y last_sync

### Requirement: Campos básicos del activo
El modelo Asset SHALL incluir campos descriptivos básicos:
- `name` (string) - nombre del activo
- `ips` (array de strings) - lista de direcciones IP asociadas
- `vendor` (string) - fabricante o proveedor (ej. Cisco, VMware, Dell)
- `source` (string) - origen de los datos (ej. VMware, Veeam, Monica, ServiceNow, EDR, Monitorización)

#### Scenario: Respuesta con datos básicos
- **GIVEN** un cliente que consulta GET /v1/assets
- **WHEN** recibe la respuesta
- **THEN** cada activo incluye name, ips, vendor y source

### Requirement: Campos específicos por tipo de activo
El modelo Asset SHALL incluir campos opcionales específicos según el tipo, para proporcionar detalles técnicos.

#### Scenario: Campos para servidores (server_physical o server_virtual)
- **GIVEN** un activo de tipo server_physical o server_virtual
- **WHEN** se consulta su detalle
- **THEN** incluye campos: ram_gb (int), total_disk_gb (int), cpu_count (int), os (string)

#### Scenario: Campos para routers
- **GIVEN** un activo de tipo router
- **WHEN** se consulta su detalle
- **THEN** incluye campos: model (string), port_count (int), firmware_version (string)

#### Scenario: Campos para switches
- **GIVEN** un activo de tipo switch
- **WHEN** se consulta su detalle
- **THEN** incluye campos: model (string), port_count (int), max_speed (string)

#### Scenario: Campos para access points (ap)
- **GIVEN** un activo de tipo ap
- **WHEN** se consulta su detalle
- **THEN** incluye campos: model (string), coverage_area (string), connected_clients (int)



### Requirement: Autenticación con OpenID Connect
Todos los endpoints de inventario SHALL requerir autorización mediante OpenID Connect (Keycloak).

#### Scenario: Token OpenID válido
- **GIVEN** un cliente con un token OIDC válido
- **WHEN** realiza GET /v1/assets
- **THEN** recibe HTTP 200 con la lista de activos

#### Scenario: Token inválido o expirado
- **GIVEN** un cliente con un token caducado o inválido
- **WHEN** realiza GET /v1/assets
- **THEN** recibe HTTP 401 Unauthorized
