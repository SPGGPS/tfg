# Tasks: Inventory Master

## 1. OpenAPI y DB

- [x] 1.1 Diseñar modelos Asset polimórficos y Tag en OpenAPI
- [x] 1.2 Crear migración: tablas assets, tags, asset_tag (N:M)
- [ ] 1.3 Migrar campo `last_backup` → `last_backup_local` + `last_backup_cloud` en modelo Asset y DB
- [ ] 1.4 Añadir campo `siem_enabled` (bool) al modelo Asset

## 2. Backend

- [x] 2.1 Implementar lógica de Auto-Tagging (VMware/Red)
- [x] 2.2 Implementar endpoint POST /v1/assets/bulk-tags
- [x] 2.3 Bloquear edición/borrado de tags con origin=system
- [ ] 2.4 Actualizar modelo Asset: eliminar `last_backup`, añadir `last_backup_local`, `last_backup_cloud`, `siem_enabled`
- [ ] 2.5 Actualizar seed de datos de prueba con los nuevos campos
- [ ] 2.6 Actualizar lógica de auto-tagging: BCK y BCKCL usan los nuevos campos

## 3. Frontend

- [x] 3.1 Dashboard con badges de cumplimiento y etiquetas
- [x] 3.2 Tabla con checkboxes y botón "Asignar Etiquetas"
- [x] 3.3 Selector de fecha y hora (datetime-local) para historificación con botón "Volver a Live"
- [x] 3.4 Búsqueda y ordenación por todos los campos visibles
- [x] 3.5 Filtro por click en etiqueta: activa filtro de etiqueta, segundo click o botón ✕ lo elimina
- [x] 3.6 Perfil de usuario en header superior derecho: nombre (text-base, font-semibold) + rol (text-xs)
- [ ] 3.7 Reemplazar puntos de compliance por rectángulos con texto: EDR, MON, SIEM, LOGS, BCK, BCKCL
- [ ] 3.8 Añadir tooltip con fecha de último backup al hacer hover en BCK y BCKCL
- [ ] 3.9 Separar columna "Backup" en "Backup Local" y "Backup Cloud"

## 4. Infra

- [ ] 4.1 Helm: CronJobs horarios para ingesta
- [ ] 4.2 Secretos vCenter/Veeam/Monica

## 5. Campos extendidos y detalle de activo

- [ ] 5.1 Añadir campos al modelo Asset: serial_number, location, description, purchase_date, warranty_expiry
- [ ] 5.2 Actualizar búsqueda en GET /v1/assets para incluir todos los campos textuales y etiquetas
- [ ] 5.3 Actualizar GET /v1/assets/{id} para incluir recent_audit (últimos 10 registros de auditoría)
- [ ] 5.4 Crear página frontend /assets/:id con toda la información extendida e historial
- [ ] 5.5 Hacer el nombre del activo en la tabla un enlace clickable a /assets/:id
- [ ] 5.6 Reemplazar combo+botón de ordenación por iconos ↑↓ en cabecera de cada columna ordenable
