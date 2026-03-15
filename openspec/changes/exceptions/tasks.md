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
