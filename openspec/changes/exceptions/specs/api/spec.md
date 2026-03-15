# API - Compliance Exceptions

## ADDED Requirements

### Requirement: Endpoint POST /v1/exceptions — crear excepción (singular o múltiple)
El sistema SHALL exponer POST /v1/exceptions restringido a rol 'admin'. Crea una o varias excepciones de compliance para un indicador concreto.

Campos obligatorios del body:
- `asset_ids` (array de string UUID, mínimo 1 elemento) — lista de activos a los que se aplica la excepción. Para un solo activo, enviar array de un elemento.
- `indicator` (enum: edr | mon | siem | logs | bck | bckcl) — indicador afectado
- `reason_code` (enum, ver catálogo) — código de razón predefinida
- `description` (string, mínimo 20 caracteres) — justificación específica del caso

Campos opcionales:
- `expires_at` (datetime | null) — fecha de expiración; null = permanente

El campo `reason` almacenado en BD se construye como: `f"{REASON_LABELS[reason_code]}: {description.strip()}"`.

**Comportamiento con múltiples activos**: se intenta crear una excepción por cada asset_id del array. Los activos que ya tengan excepción activa para ese indicador se omiten sin error (no generan 409). La respuesta incluye `created` (int), `skipped` (int) y `exceptions` (array de las creadas).

**Respuesta en creación exitosa**: 201 Created con `{"created": N, "skipped": M, "exceptions": [...]}`. Si `created=0` y `skipped>0`, responde igualmente 201 (no es un error, todos ya tenían excepción).

**Errores que SÍ detienen toda la operación** (responden con error HTTP sin crear nada):
- 404: algún asset_id no existe en la BD → `{"detail": "Asset not found: <id>"}`
- 422: description < 20 chars, reason_code inválido, indicator inválido, array vacío

#### Scenario: Crear excepción para un solo activo
- **GIVEN** un admin con asset_ids=["id1"], indicator="edr", reason_code válido, description ≥20 chars
- **WHEN** realiza POST /v1/exceptions
- **THEN** responde 201 con created=1, skipped=0, exceptions=[{...}]

#### Scenario: Crear excepción para múltiples activos con uno ya existente
- **GIVEN** asset_ids=["id1","id2","id3"], id2 ya tiene excepción activa para "edr"
- **WHEN** realiza POST /v1/exceptions
- **THEN** responde 201 con created=2, skipped=1, exceptions=[excepción_id1, excepción_id3]

#### Scenario: Todos los activos ya tienen excepción activa
- **GIVEN** todos los asset_ids ya tienen excepción activa para el indicador
- **WHEN** realiza POST /v1/exceptions
- **THEN** responde 201 con created=0, skipped=N, exceptions=[]

#### Scenario: Asset inexistente detiene la operación
- **GIVEN** uno de los asset_ids no existe en la base de datos
- **WHEN** realiza POST /v1/exceptions
- **THEN** responde 404 y no se crea ninguna excepción

#### Scenario: Description demasiado corta
- **GIVEN** description="ok"
- **WHEN** realiza POST /v1/exceptions
- **THEN** responde 422 con detalle "description must be at least 20 characters"

#### Scenario: reason_code inválido
- **GIVEN** reason_code="motivo_inventado"
- **WHEN** realiza POST /v1/exceptions
- **THEN** responde 422 con detalle de validación del enum

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

### Requirement: GET /v1/assets incluye excepciones activas con reason_code

Cada activo en la respuesta de GET /v1/assets y GET /v1/assets/{id} SHALL incluir un campo `exceptions` con las excepciones activas del activo. Esto permite al frontend calcular el color del badge localmente sin llamadas extra.

**El campo `reason_code` es obligatorio en la respuesta.** Sin él, el frontend no puede distinguir entre excepción permanente (azul) y excepción temporal (azul-rojo).

Estructura de cada objeto en `exceptions`:
```json
{
  "id": "uuid",
  "indicator": "edr",
  "reason_code": "network_device",
  "reason": "Dispositivo de red — Switch Cisco, no soporta agente EDR por diseño de hardware",
  "created_by_name": "admin",
  "created_at": "2026-03-15T10:00:00Z",
  "expires_at": null
}
```

**Campos obligatorios en la respuesta:** `id`, `indicator`, `reason_code`, `reason`, `created_by_name`, `created_at`, `expires_at`.

El backend obtiene estos datos de la tabla `compliance_exceptions` en una sola consulta adicional agrupada por `asset_id` (no N+1). Solo se incluyen excepciones activas: `revoked_at IS NULL` y (`expires_at IS NULL` OR `expires_at > now()`).

#### Scenario: Asset con excepción activa para EDR — reason_code incluido
- **GIVEN** un switch con excepción activa para "edr" con reason_code="network_device"
- **WHEN** se llama GET /v1/assets
- **THEN** ese activo incluye en su campo exceptions el objeto con reason_code="network_device"

#### Scenario: Asset sin excepciones
- **GIVEN** un activo sin excepciones registradas
- **WHEN** se llama GET /v1/assets
- **THEN** el campo exceptions es un array vacío []

#### Scenario: Excepción expirada no aparece en el campo exceptions
- **GIVEN** un activo con una excepción cuyo expires_at es en el pasado
- **WHEN** se llama GET /v1/assets
- **THEN** el campo exceptions NO incluye esa excepción (está expirada), y el badge vuelve a su color sin excepción

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
