# Design: Audit Logs

## Context

Sistema de trazabilidad y auditoría visible exclusivamente para administradores. El módulo debe registrar eventos (creación/edición/borrado de activos, gestión de etiquetas, asignaciones masivas, login/logout) capturando quién, qué, cuándo y el diff de cambios. Stack: FastAPI, React, PostgreSQL, Keycloak con roles admin/editor/viewer.

## Goals / Non-Goals

**Goals:**
- Tabla de auditoría inmutable en Postgres con soporte JSONB para diffs
- API GET /v1/audit-logs restringida a admin con filtros (activity_type, user_id, date_range)
- Panel de administración en React con tabla filtrable y modal de detalle de diff
- Integración con middleware RBAC existente

**Non-Goals:**
- Edición o borrado de registros de auditoría
- Retención configurable por tipo de evento (usar 180 días fijo)
- Exportación masiva de logs

## Decisions

| Decisión | Rationale |
|----------|-----------|
| JSONB para diff | Permite consultas flexibles y almacenamiento del estado anterior/nuevo sin esquema rígido |
| Interceptor en capa de servicio | Capturar cambios antes del commit; alternativa de triggers descartada por complejidad de diffs |
| Filtros obligatorios en API | Evitar consultas sin acotar (performance); el frontend siempre envía los tres filtros |
| Tabla append-only | Garantiza inmutabilidad; índices en (timestamp, activity_type, user_id) |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Volumen de logs alto | Retención 180 días + CronJob de limpieza; particionado por mes si crece |
| Performance en consultas con date_range amplio | Índices compuestos; paginación obligatoria |
| Exposición de datos sensibles en diff | Sanitizar campos (contraseñas, tokens) antes de guardar |
