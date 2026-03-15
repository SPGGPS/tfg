id: audit-logs

# openspec/changes/audit-logs/.openspec.yaml
schema: spec-driven
created: 2026-03-14

# Contexto: Trazabilidad y Auditoría del Sistema (Admin-Only)
context: |
  Feature: System-wide Audit Logging (Visible for Admins)
  Domain: Seguridad y cumplimiento (Compliance).
  Visibility: Módulo exclusivo para usuarios con rol 'admin'.
  Logic: 
    - Registro de eventos: Creación/Edición/Borrado de activos, gestión de etiquetas, asignaciones masivas, login/logout.
    - Metadatos: Captura de Quién (user_id), Qué (acción), Cuándo (timestamp) y el diff de cambios.

# Definición del Cambio
proposal: |
  Implementar un motor de logs y un panel de administración para auditoría:
  1. Backend: Interceptor de acciones para registrar cambios manuales y automáticos.
  2. Frontend (Vista Admin): Nueva sección "Auditoría" en el panel de administración.
  3. RBAC UI: El acceso al menú y a los datos de log está bloqueado para roles 'editor' y 'viewer'.

# Reglas de implementación
rules:
  openapi_spec:
    - Endpoint 'GET /v1/audit-logs': Restringido exclusivamente a 'admin' vía middleware de roles.
    - Filtros obligatorios: 'activity_type' (CREATE, UPDATE, DELETE, TAG_ASSIGN, LOGIN), 'user_id' y 'date_range'.
  backend_code:
    - Inmutabilidad: Prohibido cualquier endpoint de edición (PUT) o borrado (DELETE) de registros de auditoría.
    - Trazabilidad: Registrar el ID del activo para permitir el salto "ver activo afectado" desde el log.
  frontend_code:
    - Acceso Admin: El link a "Auditoría" solo se renderiza si el JWT contiene el rol 'admin'.
    - UI de Trazabilidad: Tabla con filtros dinámicos por tipo de actividad.
    - Detalle: Modal que muestra el JSON diff (qué cambió exactamente en el activo o la etiqueta).
  k8s_manifests:
    - Configurar retención de datos en Postgres para limpiar logs de más de 180 días.

# Desglose de tareas
tasks:
  - name: "DB Design: Audit Logs table with JSONB diff support"
    hours: 2
  - name: "Backend: Role-protected API for log retrieval with multi-filtering"
    hours: 3
  - name: "Frontend: Admin Audit Dashboard (React + TanStack Table)"
    hours: 4
  - name: "Frontend: Protected Route and Sidebar entry for Audit (Admin only)"
    hours: 1