# Tasks: Inventory Master

## 1. OpenAPI y DB

- [ ] 1.1 Diseñar modelos Asset polimórficos y Tag en OpenAPI
- [ ] 1.2 Crear migración: tablas assets, tags, asset_tag (N:M)

## 2. Backend

- [ ] 2.1 Implementar lógica de Auto-Tagging (VMware/Red)
- [ ] 2.2 Implementar endpoint POST /v1/assets/bulk-tags
- [ ] 2.3 Bloquear edición/borrado de tags con origin=system

## 3. Frontend

- [ ] 3.1 Dashboard con badges de cumplimiento y etiquetas
- [ ] 3.2 Tabla con checkboxes y botón "Asignar Etiquetas"
- [ ] 3.3 Selector historificación (Live / día-hora) y búsqueda/ordenación

## 4. Infra

- [ ] 4.1 Helm: CronJobs horarios para ingesta
- [ ] 4.2 Secretos vCenter/Veeam/Monica
