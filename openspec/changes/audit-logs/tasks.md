# Tasks: Audit Logs

## 1. Base de datos

- [ ] 1.1 Crear migración: tabla audit_logs (id, timestamp, user_id, activity_type, entity_id, entity_type, changes JSONB)
- [ ] 1.2 Añadir índices en (timestamp, activity_type, user_id) y política de retención 180 días

## 2. Backend

- [ ] 2.1 Implementar interceptor/servicio que registre eventos en audit_logs antes del commit
- [ ] 2.2 Crear endpoint GET /v1/audit-logs con filtros activity_type, user_id, date_range (middleware admin)
- [ ] 2.3 Validar que no existan PUT/DELETE sobre audit_logs

## 3. Frontend

- [ ] 3.1 Añadir entrada "Auditoría" en sidebar (solo visible si rol admin)
- [ ] 3.2 Crear vista Admin Audit con tabla (TanStack Table) y filtros dinámicos
- [ ] 3.3 Implementar modal de detalle que muestre el JSON diff del registro seleccionado
