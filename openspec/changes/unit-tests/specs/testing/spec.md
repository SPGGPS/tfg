# Testing - Especificaciones de prueba

## ADDED Requirements

### Requirement: TS-01 Unauthorized Audit Access

Los tests SHALL validar que un usuario sin rol 'admin' recibe 403 al consultar logs.

#### Scenario: Usuario editor intenta acceder a audit logs
- **GIVEN** un usuario con rol 'editor' o 'viewer'
- **WHEN** realiza GET /v1/audit-logs
- **THEN** la respuesta es HTTP 403 y el body incluye error 'Forbidden'

### Requirement: TS-06 System Tag Protection

Los tests SHALL validar que no se puede editar ni borrar una etiqueta con origen 'system'.

#### Scenario: DELETE de etiqueta de sistema
- **GIVEN** una etiqueta con origin='system'
- **WHEN** un admin intenta DELETE /v1/tags/{sys_id}
- **THEN** la respuesta es 400 Bad Request

### Requirement: TS-09 Audit Diff Generation

Los tests SHALL validar que cualquier cambio manual genera un registro con diff del estado anterior y nuevo.

#### Scenario: Cambio de activo genera diff
- **GIVEN** un activo existente
- **WHEN** se realiza una modificación manual (ej. asignar etiqueta)
- **THEN** AuditRecord.changes contiene JSON_DIFF(old, new)
