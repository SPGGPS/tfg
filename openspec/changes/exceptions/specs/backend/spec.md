# Backend - Compliance Exceptions

## ADDED Requirements


### Requirement: Serialización de enums en to_dict — siempre string plano

Todos los campos de tipo `Enum` de SQLAlchemy en los modelos SHALL serializarse como **string plano** en `to_dict()`, nunca como el objeto enum completo.

El patrón correcto es:
```python
# ❌ INCORRECTO — devuelve "ExceptionReasonCode.network_device"
"reason_code": self.reason_code

# ✅ CORRECTO — devuelve "network_device"
"reason_code": str(self.reason_code).split(".")[-1] if self.reason_code else None
```

Esto aplica a **todos** los campos enum del modelo: `indicator`, `reason_code`, `status`, `binding_tier`, `asset_type`, `environment`, etc.

**Motivación:** el frontend compara `exc.reason_code` contra strings como `"network_device"` o `"pending_deployment"`. Si recibe `"ExceptionReasonCode.network_device"` la comparación falla silenciosamente y el badge muestra el color incorrecto (azul en lugar de azul-rojo).

#### Scenario: reason_code devuelto como string plano
- **GIVEN** una excepción con reason_code=ExceptionReasonCode.pending_deployment
- **WHEN** se serializa con to_dict()
- **THEN** el campo reason_code en la respuesta JSON es el string "pending_deployment", no "ExceptionReasonCode.pending_deployment"

---

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

### Requirement: Lógica de creación múltiple en el router POST /v1/exceptions
El router SHALL implementar la lógica de creación múltiple de la siguiente manera:

1. Validar que todos los `asset_ids` existen en la BD. Si alguno no existe, devolver 404 inmediatamente sin crear nada.
2. Para cada `asset_id` del array:
   a. Comprobar si ya existe excepción activa para `(asset_id, indicator)`.
   b. Si existe → incrementar contador `skipped`, continuar con el siguiente.
   c. Si no existe → construir `reason = f"{REASON_LABELS[reason_code]}: {description.strip()}"`, crear la excepción, registrar audit log, incrementar contador `created`.
3. Hacer `db.commit()` una sola vez al final, no por cada excepción.
4. Devolver 201 con `{"created": N, "skipped": M, "exceptions": [lista de creadas]}`.

El router **nunca devuelve 409** por activos que ya tienen excepción activa — los omite silenciosamente. Solo devuelve 409 si se intenta revocar una excepción ya revocada.

#### Scenario: Commit único al final
- **GIVEN** un batch de 5 activos, 2 ya tienen excepción
- **WHEN** se procesa el array
- **THEN** se crean 3 excepciones en una única transacción y se devuelve created=3, skipped=2

#### Scenario: Rollback si falla durante el batch
- **GIVEN** un error inesperado al crear la excepción del activo 3 de 5
- **WHEN** se produce el error
- **THEN** se hace rollback de toda la transacción y no se crea ninguna excepción
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

### Requirement: Catálogo de razones predefinidas en backend
El backend SHALL definir un enum `ExceptionReasonCode` con los 12 valores del catálogo. El endpoint POST /v1/exceptions SHALL recibir `reason_code` y `description` como campos separados. La lógica de negocio construye el campo `reason` almacenado concatenando la etiqueta legible del reason_code con la descripción: `f"{REASON_LABELS[reason_code]}: {description.strip()}"`.

Tabla de etiquetas:
```
agent_not_supported  → "Agente no compatible con el hardware o sistema operativo del dispositivo"
network_device       → "Dispositivo de red (switch/router/AP) — no admite instalación de agentes"
excluded_backup      → "Excluido de política de backup por decisión de negocio aprobada"
excluded_monitoring  → "Excluido de monitorización — entorno aislado, de pruebas o DMZ"
excluded_siem        → "Excluido de envío de logs a SIEM — dato clasificado o entorno restringido"
legacy_system        → "Sistema legacy sin soporte para herramientas de seguridad actuales"
pending_deployment   → "Pendiente de despliegue — instalación/configuración en curso"
decommissioning      → "Activo en proceso de baja o retirada programada"
cloud_backup_only    → "Política de solo backup en cloud, sin backup local"
local_backup_only    → "Política de solo backup local, sin backup cloud"
temporary_exclusion  → "Exclusión temporal por mantenimiento o ventana de cambio"
other                → "Otro motivo"
```

El campo `description` es obligatorio (mínimo 20 chars) incluso cuando `reason_code` es autoexplicativo.

### Requirement: CronJob de expiración de excepciones — limpieza de campos de compliance
Cuando una excepción expira (`expires_at <= now()` y `revoked_at IS NULL`), el sistema SHALL marcarla automáticamente como expirada y, opcionalmente, registrar un evento en audit_logs. El backend NO modifica el campo de compliance del activo directamente (ese campo lo actualiza la ingesta externa). Sin embargo, al expirar la excepción, el badge de compliance vuelve a rojo automáticamente porque `is_active` devuelve `False` y el frontend deja de recibir esa excepción en el campo `exceptions` del activo.

El CronJob diario de limpieza SHALL:
1. Identificar todas las excepciones con `expires_at <= now()` y `revoked_at IS NULL`
2. Registrar un evento en audit_logs por cada una: `activity_type=DELETE`, `entity_type="exception"`, con nota "Expirada automáticamente por CronJob"
3. No modificar el registro de la excepción (permanece en historial con su estado expirado)

La lógica de `is_active` en la consulta de GET /v1/assets ya filtra las expiradas, por lo que el badge cambia en cuanto la excepción expira, sin necesidad de acción manual.

#### Scenario: Excepción expirada detectada en CronJob
- **GIVEN** una excepción con expires_at="2026-03-15T00:00:00Z" y es la 01:00 del 16/03/2026
- **WHEN** el CronJob diario se ejecuta
- **THEN** se registra un audit_log de expiración y GET /v1/assets ya no incluye esa excepción en el campo exceptions del activo

### Requirement: Lógica cuadriestad en el campo exceptions de GET /v1/assets
El backend SHALL incluir en el campo `exceptions` de cada activo tanto las excepciones activas donde el indicador es KO **como** las excepciones activas donde el indicador es OK (origen reporta activo pero excepción sigue abierta). Esto permite al frontend calcular el estado cuadriestad sin lógica adicional:

- Si el indicador es OK y hay excepción activa → el frontend muestra badge azul-verde (gradiente)
- Si el indicador es KO y hay excepción activa → badge azul
- Si el indicador es OK y no hay excepción → badge verde
- Si el indicador es KO y no hay excepción → badge rojo

#### Scenario: Excepción activa con indicador ahora OK
- **GIVEN** un switch tiene excepción activa para "edr" (edr_installed=false)
- **WHEN** CrowdStrike reporta que el switch ahora tiene agente (edr_installed=true)
- **THEN** GET /v1/assets incluye la excepción en el campo exceptions y el frontend muestra badge azul-verde
