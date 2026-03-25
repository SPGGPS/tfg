# Tasks: Tags Management

## 1. Backend
- [x] 1.1 PUT /v1/tags/{id}: bloquea si origin=system → 400
- [x] 1.2 DELETE /v1/tags/{id}: bloquea si origin=system → 400. Requiere admin.
- [x] 1.3 Propagación de color/nombre a activos vinculados tras PUT
- [x] 1.4 POST /v1/tags: solo etiquetas manuales. Requiere admin.

## 2. Frontend
- [x] 2.1 TagsPage: sección Sistema (20 etiquetas, no editables) + Manual (editables)
- [x] 2.2 Modal confirmación borrado con número de activos afectados
- [x] 2.3 Formulario edición: nombre, descripción, color hex
- [x] 2.4 Selector de color estilo Chrome (hue slider + saturation picker)
