id: unit-tests

context: |
  Feature: Tests unitarios, de integración y E2E
  Stack: Pytest (backend), Vitest/RTL (frontend), Playwright (E2E)

proposal: |
  Casos de prueba prioritarios:
  TS-01: GET /v1/audit-logs con rol viewer → 403
  TS-06: DELETE /v1/tags/{system_id} → 400
  TS-09: Crear asset genera AuditLog
  E2E: Flujo completo de asignación de etiquetas masiva

status: Pendiente de implementar.
