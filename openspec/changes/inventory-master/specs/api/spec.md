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

El modelo Asset SHALL incluir los campos obligatorios: edr_installed (bool), last_backup (datetime), monitored (bool), logs_enabled (bool).

#### Scenario: Respuesta con compliance
- **GIVEN** un cliente que consulta GET /v1/assets
- **WHEN** recibe la respuesta
- **THEN** cada activo incluye los campos edr_installed, last_backup, monitored y logs_enabled
