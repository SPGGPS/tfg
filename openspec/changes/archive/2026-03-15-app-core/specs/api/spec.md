# API - Plataforma Core (Assets + Tags + Audit + Auth)

## ADDED Requirements

### Requirement: OpenID Connect / RBAC
El sistema SHALL usar OpenID Connect (Keycloak) para autenticación y autorización.
Los endpoints SHALL incluir el campo `x-required-roles` en OpenAPI.

#### Scenario: Login con Keycloak
- **GIVEN** un usuario con credenciales válidas en Keycloak
- **WHEN** completa el flujo Authorization Code + PKCE
- **THEN** obtiene tokens válidos y puede llamar a la API con Authorization: Bearer

### Requirement: Modelo Asset polimórfico y compliance
El modelo Asset SHALL incluir:
- discriminador `type` (server_physical, server_virtual, switch, router, ap)
- `edr_installed` (bool)
- `last_backup` (datetime)
- `monitored` (bool)
- `logs_enabled` (bool)
- `last_sync` (datetime)

#### Scenario: Asset response incluye compliance
- **GIVEN** un activo en la base de datos
- **WHEN** un cliente realiza GET /v1/assets
- **THEN** cada activo contiene los campos de compliance

### Requirement: Historial / versionado
El endpoint `/v1/assets` SHALL aceptar un query param `as_of` (datetime) para ver el inventario en ese punto en el tiempo.

#### Scenario: Consulta histórica
- **GIVEN** datos históricos guardados por hora
- **WHEN** un cliente consulta GET /v1/assets?as_of=2026-03-15T13:00:00Z
- **THEN** la respuesta refleja el estado del inventario en esa hora

### Requirement: Endpoint de ingestión horaria
El sistema SHALL exponer endpoints protegidos para ingestión de datos de Veeam, VMware, EDR y monitorización.

#### Scenario: Ingesta horaria
- **GIVEN** una petición válida desde el servicio de ingestión
- **WHEN** envía datos de inventario
- **THEN** el backend guarda/actualiza assets y registra `last_sync`

### Requirement: Auditoría de cambios importantes
El sistema SHALL registrar en audit-logs los cambios críticos (tags, activos, login).

#### Scenario: Cambio de etiqueta
- **GIVEN** un admin actualiza una etiqueta manual
- **WHEN** el cambio se aplica
- **THEN** se crea una entrada en audit_logs con diferencia JSON
