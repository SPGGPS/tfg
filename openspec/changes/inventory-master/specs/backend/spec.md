# Backend - Inventario (FastAPI + Sync)

## ADDED Requirements

### Requirement: Ingesta horaria y sincronización
El backend SHALL exponer endpoints protegidos para ingestión de datos cada hora (Veeam, VMware, EDR, monitorización) y actualizar `last_sync`.

#### Scenario: Sincronización horaria
- **GIVEN** un servicio de ingestión con credenciales válidas
- **WHEN** llama al endpoint de ingestión
- **THEN** el backend actualiza assets, registra `last_sync` y almacena historial por hora

### Requirement: Historial por hora (as_of)
El backend SHALL mantener un historial por hora que permita consultar el inventario en un momento puntual con un query param `as_of`.

#### Scenario: Consulta histórica
- **GIVEN** inventario histórico almacenado por hora
- **WHEN** un cliente solicita GET /v1/assets?as_of=2026-03-15T13:00:00Z
- **THEN** el backend retorna el inventario tal como estaba a esa hora

### Requirement: Compliance fields — escritos exclusivamente por la ingesta
El backend SHALL incluir en el modelo Asset los siguientes campos de compliance. **Ninguno de estos campos es modificable por endpoints de usuario** — solo se actualizan a través del endpoint de ingestión `/v1/assets/ingest` llamado por los CronJobs de sincronización:

| Campo | Origen de ingesta | Significado |
|-------|-------------------|-------------|
| `edr_installed` (bool) | CrowdStrike / SentinelOne | El agente EDR reporta el activo como protegido |
| `monitored` (bool) | Zabbix / Nagios | El activo está dado de alta y enviando métricas |
| `siem_enabled` (bool) | SIEM / Syslog | El activo envía logs al SIEM |
| `logs_enabled` (bool) | Monitorización / Syslog | Generación de logs del sistema activa |
| `last_backup_local` (datetime\|null) | Veeam local/on-prem | Fecha del último backup local exitoso; null = nunca |
| `last_backup_cloud` (datetime\|null) | Veeam cloud/offsite | Fecha del último backup cloud exitoso; null = nunca |
| `last_sync` (datetime) | Cualquier fuente | Timestamp de la última ingesta recibida |

El backend NO debe exponer endpoints PUT/PATCH para modificar estos campos directamente. Solo `POST /v1/assets/ingest` (rol admin, llamado por CronJobs) puede escribirlos.

#### Scenario: Ingesta actualiza solo los campos que reporta el origen
- **GIVEN** una ingesta de Veeam que solo envía datos de backup
- **WHEN** el backend procesa el payload
- **THEN** actualiza last_backup_local/cloud y last_sync, sin tocar edr_installed ni monitored

### Requirement: Tipo database en el modelo Asset
El enum `AssetType` SHALL incluir el valor `database`. El modelo Asset SHALL incluir los campos de resumen y detalle para este tipo:

**Campos de resumen** (columnas en Asset):
- `db_engine` (String enum — ver catálogo en spec de API)
- `db_version` (String nullable)
- `db_size_gb` (Float nullable)
- `db_port` (Integer nullable)
- `db_replication` (Boolean, default False)
- `db_cluster` (String nullable) — nombre del cluster / grupo de disponibilidad / replica set
- `db_is_cluster` (Boolean, default False) — es nodo de cluster HA
- `db_vip` (String nullable) — Virtual IP o FQDN del listener del cluster
- `db_host_asset_id` (String nullable, FK a assets.id ON DELETE SET NULL) — activo servidor que aloja esta instancia
- `db_host_display` (String nullable) — nombre o IP del host para mostrar en UI; se actualiza automáticamente si db_host_asset_id existe

**Lógica de db_host_display**: cuando se guarda o actualiza un activo database, si `db_host_asset_id` está relleno, el backend SHALL consultar el nombre del activo referenciado y almacenarlo en `db_host_display`. Si el activo host es eliminado (ON DELETE SET NULL), `db_host_asset_id` queda null pero `db_host_display` conserva el último valor conocido para trazabilidad.

**Campos de detalle extendido** (JSONB — solo en GET /v1/assets/{id}):
- `db_schemas` (JSONB array) — `[{name, size_gb, table_count, owner, charset, collation, description}]`
- `db_cluster_nodes` (JSONB array) — `[{hostname, role, asset_id, status}]` — solo cuando db_is_cluster=true
- `db_users` (JSONB array) — `[{username, role, last_login}]`
- `db_connections_max` (Integer nullable)
- `db_connections_active` (Integer nullable)
- `db_encoding` (String nullable)
- `db_timezone` (String nullable)
- `db_ha_mode` (String nullable — enum: `primary`, `replica`, `standby`, `arbiter`, `standalone`, `unknown`)
- `db_ssl_enabled` (Boolean nullable)
- `db_audit_enabled` (Boolean nullable)
- `db_last_vacuum` (DateTime nullable)
- `db_notes` (Text nullable)

Los campos JSONB se incluyen en `to_dict()` solo en el endpoint de detalle (`GET /v1/assets/{id}`), no en el listado, para evitar sobrecarga de payload.

#### Scenario: Asset de tipo database cluster con VIP
- **GIVEN** un activo database con db_is_cluster=true, db_vip="10.0.1.50", db_cluster_nodes=[{hostname:"db01",role:"primary"},{hostname:"db02",role:"replica"}]
- **WHEN** se consulta GET /v1/assets/{id}
- **THEN** la respuesta incluye db_vip, db_cluster_nodes con los dos nodos y sus roles

#### Scenario: db_host_display sincronizado con asset host
- **GIVEN** un activo database con db_host_asset_id="uuid-srv-db-01"
- **WHEN** se guarda el activo
- **THEN** db_host_display se rellena automáticamente con el nombre del asset "srv-db-01"

#### Scenario: db_host_display conservado al eliminar host
- **GIVEN** un activo database con db_host_asset_id="uuid-srv" y db_host_display="srv-db-01"
- **WHEN** el activo servidor es eliminado
- **THEN** db_host_asset_id queda NULL pero db_host_display conserva "srv-db-01"

#### Scenario: db_vip solo relevante en cluster
- **GIVEN** un activo database con db_is_cluster=false y db_vip="10.0.1.50"
- **WHEN** el validador procesa el activo
- **THEN** el backend registra un warning en logs pero no rechaza el valor (puede ser útil en migración de datos)

### Requirement: Ordenación con NULLS LAST para campos datetime
El backend SHALL añadir al modelo Asset los campos: `serial_number` (String, nullable), `location` (String, nullable), `description` (Text, nullable), `purchase_date` (Date, nullable), `warranty_expiry` (Date, nullable). Estos campos participan en la búsqueda full-text del endpoint GET /v1/assets.

#### Scenario: Búsqueda por serial_number
- **GIVEN** un activo con serial_number definido
- **WHEN** se llama GET /v1/assets?search=<serial>
- **THEN** el activo aparece en resultados

### Requirement: Búsqueda extendida en backend
La lógica de filtrado por `search` SHALL incluir todos los campos textuales del activo: name, vendor, source, os, model, serial_number, location, description, firmware_version, mac_address, IPs (cast a string) y nombres de etiquetas asociadas.

### Requirement: Detalle de activo con audit reciente
El endpoint GET /v1/assets/{id} SHALL incluir en la respuesta un campo `recent_audit` con los últimos 10 registros de AuditLog donde entity_id == asset_id, ordenados por timestamp desc.

### Requirement: Ordenación con NULLS LAST para campos datetime
Al ordenar por campos datetime nullable (`last_backup_local`, `last_backup_cloud`, `last_sync`), el backend SHALL usar `NULLS LAST` en la cláusula ORDER BY para que los registros sin valor aparezcan siempre al final, tanto en ordenación ascendente como descendente.

#### Scenario: NULLS LAST en last_backup_local — ambas direcciones
- **GIVEN** activos con y sin last_backup_local
- **WHEN** se ordena por ese campo en cualquier dirección (asc o desc)
- **THEN** los activos con null (sin backup) **siempre aparecen al final**, independientemente de la dirección de orden

**Semántica:** null en campos de backup significa "nunca se ha hecho backup" — el peor estado posible. Debe estar siempre al final tanto en ASC (peores al final = más recientes primero sin null) como en DESC (mejores primero sin null, peores al final). Se implementa con `nullslast()` en ambas direcciones en SQLAlchemy.
