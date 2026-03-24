id: audit-logs

context: |
  Feature: Sistema de trazabilidad de acciones (solo admin)
  Registra: quién, qué, cuándo, qué cambió (diff JSON)

proposal: |
  1. Tabla audit_logs inmutable (no PUT/DELETE)
  2. GET /v1/audit-logs restringido a admin con filtros
  3. AuditPage en frontend con tabla filtrable y modal de detalle
  4. audit_service.py registra eventos automáticamente en acciones clave

status: Implementado al 100%.
