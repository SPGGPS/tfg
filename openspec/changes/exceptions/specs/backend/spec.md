# Backend - Compliance Exceptions

## ADDED Requirements

### Requirement: Modelo ComplianceException
El backend SHALL implementar el modelo `ComplianceException` con los campos:
- `id` (UUID PK)
- `asset_id` (FK → assets.id, ON DELETE CASCADE)
- `indicator` (Enum: edr | mon | siem | logs | bck | bckcl)
- `reason` (Text, NOT NULL, mínimo 20 chars validado en capa de negocio)
- `created_by` (String) — sub del JWT
- `created_by_name` (String) — preferred_username del JWT
- `created_at` (DateTime with timezone, default now())
- `expires_at` (DateTime with timezone, nullable)
- `revoked_by` (String, nullable)
- `revoked_by_name` (String, nullable)
- `revoked_at` (DateTime with timezone, nullable)

Índices:
- UNIQUE parcial sobre `(asset_id, indicator)` WHERE `revoked_at IS NULL` — solo una excepción activa por par
- INDEX en `asset_id`, `indicator`, `revoked_at`

#### Scenario: Unicidad de excepción activa
- **GIVEN** una excepción activa para (asset_id="X", indicator="edr")
- **WHEN** se intenta insertar otra para el mismo par
- **THEN** el backend lanza 409 Conflict antes de llegar a la DB (validación en capa de servicio)

---

### Requirement: Lógica de estado de excepción
El backend SHALL implementar una propiedad o función `is_active(exception)` que devuelve `True` si:
- `revoked_at IS NULL`
- Y (`expires_at IS NULL` O `expires_at > datetime.now(utc)`)

Esta lógica se usa en los filtros de GET /v1/exceptions y al enriquecer GET /v1/assets.

#### Scenario: Excepción expirada no es activa
- **GIVEN** una excepción con expires_at en el pasado y revoked_at NULL
- **WHEN** se consulta si está activa
- **THEN** is_active devuelve False → badge vuelve a mostrarse en rojo en la UI

---

### Requirement: Revocación (soft delete)
DELETE /v1/exceptions/{id} SHALL actualizar los campos `revoked_by`, `revoked_by_name` y `revoked_at` en lugar de borrar el registro. El registro permanece en la tabla para trazabilidad histórica.

#### Scenario: Soft delete preserva el registro
- **GIVEN** una excepción activa con id="E1"
- **WHEN** se revoca con DELETE /v1/exceptions/E1
- **THEN** el registro sigue existiendo en la tabla con revoked_at relleno

---

### Requirement: Audit trail de excepciones
Toda creación y revocación de excepción SHALL registrarse en `audit_logs`:
- Creación: `activity_type=CREATE`, `entity_type="exception"`, `entity_id=exception.id`, `changes={"after": {todos los campos}}`
- Revocación: `activity_type=DELETE`, `entity_type="exception"`, `entity_id=exception.id`, `changes={"before": {estado antes}, "after": {estado revocado}}`

#### Scenario: Audit log en creación
- **GIVEN** un admin crea una excepción
- **WHEN** la excepción se guarda exitosamente
- **THEN** se crea un registro en audit_logs con activity_type=CREATE y entity_type="exception"

---

### Requirement: Enriquecimiento de GET /v1/assets con excepciones
Al devolver los activos, el backend SHALL hacer un JOIN o subquery eficiente para incluir las excepciones activas de cada activo en el campo `exceptions`. Para el listado (GET /v1/assets) solo se incluyen las excepciones activas. Para el detalle (GET /v1/assets/{id}) se incluyen todas (activas + historial).

#### Scenario: JOIN eficiente sin N+1
- **GIVEN** una consulta de 50 activos
- **WHEN** el backend construye la respuesta
- **THEN** usa una sola query adicional (o JOIN) para cargar todas las excepciones, no una query por activo
