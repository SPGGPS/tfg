# API - Compliance Exceptions

## ADDED Requirements

### Requirement: Endpoint POST /v1/exceptions — crear excepción
El sistema SHALL exponer POST /v1/exceptions restringido a rol 'admin'. Crea una excepción de compliance para un activo y un indicador concreto.

Campos obligatorios del body:
- `asset_id` (string UUID) — id del activo al que se aplica la excepción
- `indicator` (enum: edr | mon | siem | logs | bck | bckcl) — indicador afectado
- `reason` (string, mínimo 20 caracteres) — justificación de la excepción

Campos opcionales:
- `expires_at` (datetime | null) — fecha de expiración; null = permanente

#### Scenario: Crear excepción con motivo válido
- **GIVEN** un admin autenticado con un asset_id válido
- **WHEN** realiza POST /v1/exceptions con indicator="edr" y reason de ≥20 chars
- **THEN** responde 201 con la excepción creada incluyendo id, created_by, created_at

#### Scenario: Motivo demasiado corto
- **GIVEN** un admin que envía reason="ok"
- **WHEN** realiza POST /v1/exceptions
- **THEN** responde 422 Unprocessable Entity con detalle "reason must be at least 20 characters"

#### Scenario: Excepción duplicada activa
- **GIVEN** ya existe una excepción activa para (asset_id, indicator)
- **WHEN** se intenta crear otra para el mismo par
- **THEN** responde 409 Conflict con el id de la excepción existente

#### Scenario: Asset inexistente
- **GIVEN** un asset_id que no existe en la base de datos
- **WHEN** se intenta crear la excepción
- **THEN** responde 404 Not Found

---

### Requirement: Endpoint GET /v1/exceptions — listar excepciones
Lista excepciones con filtros opcionales. Accesible para rol viewer+.

Filtros disponibles:
- `asset_id` (string) — filtrar por activo
- `indicator` (enum) — filtrar por indicador
- `status` (enum: active | revoked | expired | all) — por defecto "active"
- `page`, `page_size` (paginación, máx 100)

#### Scenario: Listar excepciones activas
- **GIVEN** un usuario viewer autenticado
- **WHEN** realiza GET /v1/exceptions?status=active
- **THEN** recibe lista de excepciones con revoked_at IS NULL y no expiradas

#### Scenario: Historial completo
- **GIVEN** un admin que quiere ver todo el historial
- **WHEN** realiza GET /v1/exceptions?status=all
- **THEN** recibe todas las excepciones (activas, revocadas y expiradas)

---

### Requirement: Endpoint GET /v1/exceptions/{id} — detalle de excepción
Devuelve una excepción por id con todos sus campos incluyendo revocación si aplica.

#### Scenario: Excepción existente
- **GIVEN** un id de excepción válido
- **WHEN** se realiza GET /v1/exceptions/{id}
- **THEN** responde 200 con el objeto completo

---

### Requirement: Endpoint DELETE /v1/exceptions/{id} — revocar excepción
Soft delete: marca la excepción como revocada registrando revoked_by y revoked_at. Restringido a admin. No existe PUT ni PATCH.

#### Scenario: Revocar excepción activa
- **GIVEN** una excepción activa y un admin autenticado
- **WHEN** realiza DELETE /v1/exceptions/{id}
- **THEN** responde 200 con la excepción actualizada (revoked_at y revoked_by_name rellenos)

#### Scenario: Revocar excepción ya revocada
- **GIVEN** una excepción ya revocada
- **WHEN** se intenta revocar de nuevo
- **THEN** responde 409 Conflict "Exception already revoked"

---

### Requirement: GET /v1/assets incluye excepciones activas
Cada activo en la respuesta de GET /v1/assets y GET /v1/assets/{id} SHALL incluir un campo `exceptions` con las excepciones activas del activo. Esto permite al frontend calcular el color del badge sin una llamada extra.

Estructura de cada objeto en `exceptions`:
```json
{
  "id": "uuid",
  "indicator": "edr",
  "reason": "Switch Cisco — no soporta agente EDR por diseño de hardware",
  "created_by_name": "admin",
  "created_at": "2026-03-15T10:00:00Z",
  "expires_at": null
}
```

#### Scenario: Asset con excepción activa para EDR
- **GIVEN** un switch con excepción activa para "edr"
- **WHEN** se llama GET /v1/assets
- **THEN** ese activo incluye en su campo exceptions el objeto de la excepción de EDR

#### Scenario: Asset sin excepciones
- **GIVEN** un activo sin excepciones registradas
- **WHEN** se llama GET /v1/assets
- **THEN** el campo exceptions es un array vacío []

### Requirement: POST /v1/exceptions soporta múltiples asset_ids
El endpoint POST /v1/exceptions SHALL aceptar opcionalmente un array `asset_ids` además del campo `asset_id` singular. Si se proporciona `asset_ids`, se crea una excepción para cada activo del array con el mismo indicador, motivo y expires_at. Los activos que ya tengan excepción activa para ese indicador se omiten sin error. La respuesta incluye `created`, `skipped` y la lista de excepciones creadas.

#### Scenario: Creación en múltiples activos
- **GIVEN** un admin envía POST con asset_ids=["id1","id2","id3"] e indicator="edr"
- **WHEN** id2 ya tiene excepción activa para "edr"
- **THEN** responde 201 con {"created": 2, "skipped": 1, "exceptions": [...]}

### Requirement: Catálogo de razones predefinidas en POST /v1/exceptions
El body de POST /v1/exceptions SHALL incluir el campo `reason_code` (string enum, obligatorio) además de `description` (string, mínimo 20 chars, obligatorio). El campo `reason` almacenado SHALL ser la concatenación `"[etiqueta de reason_code]: [description]"`.

Los valores válidos de `reason_code` son:
- `agent_not_supported`
- `network_device`
- `excluded_backup`
- `excluded_monitoring`
- `excluded_siem`
- `legacy_system`
- `pending_deployment`
- `decommissioning`
- `cloud_backup_only`
- `local_backup_only`
- `temporary_exclusion`
- `other`

#### Scenario: reason_code obligatorio
- **GIVEN** un admin envía POST sin reason_code
- **THEN** responde 422 con detalle de validación

#### Scenario: description obligatoria
- **GIVEN** un admin envía POST con reason_code pero sin description o con menos de 20 chars
- **THEN** responde 422 con detalle de validación

#### Scenario: reason almacenado como concatenación
- **GIVEN** reason_code="network_device" y description="Switch Cisco del CPD principal"
- **WHEN** se crea la excepción
- **THEN** el campo reason en BD contiene "Dispositivo de red: Switch Cisco del CPD principal"
