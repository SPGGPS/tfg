id: tags-management

context: |
  Feature: CRUD de etiquetas manuales + protección de etiquetas de sistema
  Las etiquetas de sistema (origin=system) NO son editables.

proposal: |
  1. PUT/DELETE /v1/tags/{id} restringidos a admin, bloqueados para origin=system
  2. Propagación de cambios de color/nombre a todos los activos vinculados
  3. Modal de confirmación con número de activos afectados antes de borrar
  4. Visualización en TagsPage: sección Sistema (no editable) + Manual (editable)

status: Implementado al 95%. Pendiente: selector de color estilo Chrome.
