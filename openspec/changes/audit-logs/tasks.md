# Tasks: Audit Logs

## 1. Base de datos

- [x] 1.1 Crear migración: tabla audit_logs (id, timestamp, user_id, activity_type, entity_id, entity_type, changes JSONB)
- [x] 1.2 Añadir índices en (timestamp, activity_type, user_id) y política de retención 180 días

## 2. Backend

- [x] 2.1 Implementar interceptor/servicio que registre eventos en audit_logs antes del commit
- [x] 2.2 Crear endpoint GET /v1/audit-logs con filtros activity_type, user_id, date_range (middleware admin)
- [x] 2.3 Validar que no existan PUT/DELETE sobre audit_logs

## 3. Frontend

- [x] 3.1 Añadir entrada "Auditoría" en sidebar (solo visible si rol admin)
- [x] 3.2 Crear vista Admin Audit con tabla (TanStack Table) y filtros dinámicos
- [x] 3.3 Implementar modal de detalle que muestre el JSON diff del registro seleccionado

## 4. Infraestructura / Kubernetes

- [ ] 4.1 Crear manifests de K8s para despliegue de la API y la base de datos (Deployment + Service)
- [ ] 4.2 Configurar Secret para JWT y credenciales de Postgres
- [ ] 4.3 Añadir CronJob que limpie `audit_logs` mayores de 180 días
- [ ] 4.4 Añadir probes de readiness/liveness que usen `/v1/healthz`
