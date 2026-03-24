id: unit-test

# openspec/changes/unit-test/.openspec.yaml
schema: spec-driven
created: 2026-03-14

# Contexto: Plan de Pruebas y Validación Técnica
context: |
  Feature: Testing & Validation Specs
  Domain: Calidad de Software y Seguridad.
  Objective: Definir los escenarios de prueba obligatorios para asegurar la integridad de la CMDB, el RBAC de Keycloak y la consistencia de los Audit Logs.

# Definición de Escenarios de Prueba (Specs)
specs:
  - module: "AUTH_&_RBAC"
    cases:
      - name: "TS-01: Unauthorized Audit Access"
        description: "Validar que un usuario sin rol 'admin' recibe un 403 al consultar logs."
        assertion: "HTTP_STATUS == 403 AND response_body.error == 'Forbidden'"
      - name: "TS-02: Token Expiry Flow"
        description: "Validar que un JWT expirado fuerza el redireccionamiento al OIDC Login."
        assertion: "HTTP_STATUS == 401 AND header.WWW-Authenticate exists"

  - module: "INVENTORY_&_COMPLIANCE"
    cases:
      - name: "TS-03: Asset Reconciliation (Upsert)"
        description: "Validar que la ingesta de VMware no duplica registros basados en MAC/UUID."
        assertion: "DB_COUNT(assets) remains same AND asset.last_sync updated"
      - name: "TS-04: Compliance Health Logic"
        description: "Validar que si Veeam reporta fallo, el badge de backup en el frontend cambia a rojo."
        assertion: "asset.compliance.backup_status == false AND UI_COMPONENT_COLOR == 'red'"
      - name: "TS-05: Hourly Sync Execution"
        description: "Validar que el CronJob de K8s dispara la ingesta cada hora en punto."
        assertion: "CronSchedule == '0 * * * *' AND Trigger_Log exists"

  - module: "TAG_MANAGEMENT"
    cases:
      - name: "TS-06: System Tag Protection"
        description: "Validar que no se puede editar ni borrar una etiqueta con origen 'system'."
        assertion: "DELETE /v1/tags/{sys_id} returns 400 Bad Request"
      - name: "TS-07: Manual Tag Propagation"
        description: "Validar que al cambiar el color de una etiqueta manual, todos los activos asociados muestran el nuevo color."
        assertion: "Update Tag(color) -> GET /v1/assets returns new color for all related IDs"
      - name: "TS-08: Bulk Assignment Atomicity"
        description: "Validar que la asignación masiva de etiquetas es una transacción atómica."
        assertion: "On partial failure, rollback all tag assignments"

  - module: "AUDIT_&_PROFILE"
    cases:
      - name: "TS-09: Audit Diff Generation"
        description: "Validar que cualquier cambio manual genera un registro con el estado anterior y nuevo."
        assertion: "AuditRecord.changes contains JSON_DIFF(old, new)"
      - name: "TS-10: Avatar Security Sandbox"
        description: "Validar que el backend rechaza archivos con contenido malicioso (Magic Bytes check)."
        assertion: "Upload(malicious.php.jpg) returns 422 Unprocessable Entity"
      - name: "TS-11: Admin Dashboard Visibility"
        description: "Validar que la pestaña 'Auditoría' solo es visible para el rol admin."
        assertion: "UI_SIDEBAR.links.contains('Audit') == (user.role == 'admin')"

# Desglose de tareas de validación
tasks:
  - name: "Backend: Implement Pytest suite for RBAC and Ingestion logic"
    hours: 4
  - name: "Frontend: Implement Vitest/RTL specs for Compliance Badges"
    hours: 3
  - name: "E2E: Configure Playwright for Bulk Tagging workflows"
    hours: 4
