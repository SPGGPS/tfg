# Tasks: Compliance Exceptions

## 1. Base de datos

- [ ] 1.1 Crear modelo ComplianceException (id, asset_id FK, indicator ENUM, reason TEXT, created_by, created_by_name, created_at, expires_at, revoked_by, revoked_by_name, revoked_at)
- [ ] 1.2 Añadir índice UNIQUE parcial sobre (asset_id, indicator) WHERE revoked_at IS NULL
- [ ] 1.3 Añadir índices en asset_id, indicator y revoked_at

## 2. Backend

- [ ] 2.1 Implementar router /v1/exceptions con POST, GET, GET/{id}, DELETE (soft)
- [ ] 2.2 Validación: reason ≥ 20 chars, asset_id existente, no duplicado activo por (asset_id, indicator)
- [ ] 2.3 Lógica is_active(): revoked_at IS NULL AND (expires_at IS NULL OR expires_at > now())
- [ ] 2.4 Soft delete: rellenar revoked_by, revoked_by_name, revoked_at en lugar de borrar
- [ ] 2.5 Registrar creación y revocación en audit_logs (entity_type="exception")
- [ ] 2.6 Enriquecer respuesta de GET /v1/assets con campo exceptions (excepciones activas por activo, sin N+1)
- [ ] 2.7 En GET /v1/assets/{id}: incluir historial completo de excepciones (activas + revocadas + expiradas)

## 3. Frontend

- [ ] 3.1 Añadir entrada "Excepciones" en sidebar (solo admin) entre "Fuentes de Datos" y "Auditoría"
- [ ] 3.2 Crear página /exceptions con tabla de activas y sección de historial
- [ ] 3.3 Formulario de creación: selector de activo (typeahead), selector de indicador, textarea con contador mínimo 20 chars, date picker opcional para expiración
- [ ] 3.4 Botón "Crear excepción" deshabilitado hasta que motivo ≥ 20 chars
- [ ] 3.5 Modal de confirmación al revocar con motivo original visible
- [ ] 3.6 Actualizar lógica de color de badges: triestado verde/azul/rojo basado en campo exceptions de cada activo
- [ ] 3.7 Tooltip en badge azul con motivo de la excepción y quién la creó
- [ ] 3.8 Actualizar leyenda al pie de la tabla de inventario: 🟢 OK · 🔵 Excepción · 🔴 KO
- [ ] 3.9 Toast de confirmación al crear/revocar excepción

## 4. Razones predefinidas (nuevo)

- [ ] 4.1 Definir enum ExceptionReasonCode con 12 valores en backend
- [ ] 4.2 Actualizar POST /v1/exceptions: añadir campos reason_code (enum, obligatorio) y description (str, min 20, obligatorio)
- [ ] 4.3 Lógica de concatenación: reason = f"{REASON_LABELS[reason_code]}: {description}"
- [ ] 4.4 Actualizar frontend: añadir selector de razón predefinida (obligatorio) y textarea de descripción (obligatorio, min 20 chars)
- [ ] 4.5 Actualizar validación del botón: deshabilitado si falta activos, indicador, razón o descripción insuficiente

## 5. Expiración automática y estado cuadriestad

- [ ] 5.1 CronJob diario: detectar excepciones con expires_at <= now() y revoked_at IS NULL, registrar audit_log por cada una con nota "Expirada automáticamente"
- [ ] 5.2 Verificar que is_active() excluye las expiradas correctamente → badge vuelve a rojo sin acción manual
- [ ] 5.3 GET /v1/assets: incluir en el campo exceptions tanto las excepciones activas con indicador KO como con indicador OK (para calcular el cuadriestad en frontend)
- [ ] 5.4 Frontend: implementar lógica cuadriestad en ComplianceBadge — gradiente azul-verde cuando origen=OK y excepción activa
- [ ] 5.5 Frontend: tooltip en badge azul-verde: "OK desde el origen. Excepción activa: [motivo]. Considera revocarla."
- [ ] 5.6 Frontend: actualizar leyenda con los 4 estados (verde / azul-verde / azul / rojo)
