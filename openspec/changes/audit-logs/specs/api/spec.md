# API - Audit Logs

## ADDED Requirements

### Requirement: Endpoint GET /v1/audit-logs restringido a admin

El sistema SHALL exponer GET /v1/audit-logs únicamente para usuarios con rol 'admin'.

#### Scenario: Acceso denegado para no-admin
- **GIVEN** un usuario con rol 'editor' o 'viewer'
- **WHEN** intenta GET /v1/audit-logs
- **THEN** recibe HTTP 403 Forbidden

#### Scenario: Filtros obligatorios
- **GIVEN** un usuario admin autenticado
- **WHEN** consulta GET /v1/audit-logs
- **THEN** la petición requiere los filtros activity_type, user_id y date_range

#### Scenario: Límite de paginación
- **GIVEN** un usuario admin que consulta GET /v1/audit-logs
- **WHEN** no se indica un límite o se indica uno mayor al máximo (p.ej. 100)
- **THEN** la API devuelve como máximo 100 registros por página para evitar fugas de datos y sobrecarga

### Requirement: Inmutabilidad de registros de auditoría

El sistema SHALL prohibir cualquier endpoint PUT o DELETE sobre registros de auditoría.

#### Scenario: Sin edición ni borrado
- **GIVEN** un registro de auditoría existente
- **WHEN** cualquier cliente intenta PUT o DELETE sobre ese registro
- **THEN** el sistema responde con 405 Method Not Allowed o no expone dichos endpoints
