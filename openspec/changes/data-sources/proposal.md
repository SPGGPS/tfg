id: data-sources

context: |
  Feature: Gestión de conexiones a fuentes de datos externas
  Tipos: vmware, veeam, edr, monica, zabbix, manual

proposal: |
  1. Modelo DataSource: name, type, connection_config(JSON), status, last_sync
  2. CRUD completo /v1/data-sources
  3. POST /v1/data-sources/{id}/validate — testea la conexión
  4. Asset.data_source_id FK → data_sources

status: Implementado al 100%. Lógica de ingesta real pendiente.
