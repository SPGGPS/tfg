id: tags-management

# openspec/changes/tags-management/.openspec.yaml
schema: spec-driven
created: 2026-03-14

# Contexto: Gestión de Etiquetas (Manuales vs Automáticas)
context: |
  Feature: User-defined Tagging System (Full Lifecycle)
  Domain: Clasificación de activos.
  Logic: 
    - Etiquetas Automáticas (Sistema): Generadas por el backend (ej. 'Virtual', 'Cisco'). Color fijo.
    - Etiquetas Manuales (Admin): Creadas por administradores. Color dinámico.
    - Integridad: Las modificaciones en etiquetas manuales deben propagarse a todos los activos vinculados.

# Definición del Cambio
proposal: |
  Crear el módulo de administración de etiquetas con soporte para edición y borrado:
  1. CRUD completo de etiquetas manuales (Nombre, Color, Descripción,nombre de usuario que la creo y fecha de creacion).
  2. El backend debe diferenciar el origen (origin: system | manual).
  3. Propagación: Los cambios en el nombre o color de una etiqueta manual se reflejan automáticamente en el inventario.
  4. Borrado: El administrador puede eliminar etiquetas manuales, desvinculándolas de todos los activos de forma atómica.

# Reglas de implementación
rules:
  openapi_spec:
    - Endpoint 'PUT /v1/tags/{tag_id}' y 'DELETE /v1/tags/{tag_id}' restringidos a 'admin'.
    - El modelo Tag incluye 'id' (UUID), 'name', 'color_code' (hex) y 'origin'.
  backend_code:
    - Validación: Prohibir la modificación o borrado de etiquetas con 'origin: system'.
    - Integridad: Implementar borrado (ON DELETE CASCADE en la tabla de relación o desvinculación limpia).
    - Cache: Invalidar cualquier caché de activos en el frontend tras una actualización de etiqueta para asegurar consistencia visual.
  frontend_code:
    - UI: Modal de confirmación para borrado de etiquetas con advertencia del número de activos afectados.
    - UI: Selector de color (Chrome-style) para edición de etiquetas manuales.
    - Reactivity: Uso de 'TanStack Query' para refrescar la lista de activos cuando una etiqueta global sea modificada.

# Desglose de tareas
tasks:
  - name: "Design API: CRUD endpoints (GET, POST, PUT, DELETE) for Tags"
    hours: 2
  - name: "Backend: Implement Tag lifecycle logic and protection of system tags"
    hours: 3
  - name: "Frontend: Tag Management Dashboard with Edit/Delete workflows"
    hours: 4
  - name: "DB: Migration for Tag table and Asset-Tag relationship (M:N)"
    hours: 2
