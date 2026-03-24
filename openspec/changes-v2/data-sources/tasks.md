# Tasks: Data Sources

## 1. Backend
- [x] 1.1 Modelo DataSource: name, type, description, connection_config(JSON),
           status, last_sync, sync_status
- [x] 1.2 CRUD /v1/data-sources
- [x] 1.3 POST /v1/data-sources/{id}/validate
- [x] 1.4 Asset.data_source_id FK SET NULL

## 2. Frontend
- [x] 2.1 DataSourcesPage /data-sources: solo admin
- [x] 2.2 Tabla con estado de sync y última sincronización
- [x] 2.3 Modal de creación/edición con campos de configuración

## 3. Pendiente
- [ ] 3.1 Workers de ingesta real: VMware vCenter API
- [ ] 3.2 Workers: Veeam API
- [ ] 3.3 Workers: EDR (CrowdStrike/SentinelOne)
- [ ] 3.4 Workers: Monica asset management
