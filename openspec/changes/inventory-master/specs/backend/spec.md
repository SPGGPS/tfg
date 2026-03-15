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

**Campos de resumen** (columnas en Asset): `db_engine` (String enum con los motores del catálogo), `db_version` (String), `db_size_gb` (Integer), `db_host` (String), `db_port` (Integer), `db_replication` (Boolean, default False), `db_cluster` (String nullable).

**Campos de detalle extendido** (JSON columns o tablas relacionadas para el endpoint de detalle):
- `db_schemas` (JSON array) — lista de esquemas: [{name, size_gb, table_count, owner}]
- `db_users` (JSON array) — lista de usuarios: [{username, role, last_login}]
- `db_connections_max` (Integer nullable)
- `db_connections_active` (Integer nullable)
- `db_encoding` (String nullable)
- `db_timezone` (String nullable)
- `db_ha_mode` (String nullable — "primary", "replica", "standby", "none")
- `db_ssl_enabled` (Boolean nullable)
- `db_audit_enabled` (Boolean nullable)
- `db_last_vacuum` (DateTime nullable)
- `db_notes` (Text nullable)

Los campos `db_schemas` y `db_users` se almacenan como JSON (JSONB en PostgreSQL) para flexibilidad. Se incluyen en `to_dict()` solo cuando se llama desde el endpoint de detalle (`GET /v1/assets/{id}`), no en el listado para evitar sobrecarga.

#### Scenario: Asset de tipo database con campos específicos
- **GIVEN** un activo de tipo database ingresado con db_engine="postgresql" y db_version="16.2"
- **WHEN** se consulta GET /v1/assets/{id}
- **THEN** la respuesta incluye todos los campos de resumen y de detalle extendido

### Requirement: Ordenación con NULLS LAST para campos datetime
Al ordenar por campos datetime nullable (`last_backup_local`, `last_backup_cloud`, `last_sync`), el backend SHALL usar `NULLS LAST` en la cláusula ORDER BY para que los registros sin valor aparezcan siempre al final, tanto en ordenación ascendente como descendente.

#### Scenario: NULLS LAST en last_backup_local
- **GIVEN** activos con y sin last_backup_local
- **WHEN** se ordena por ese campo en cualquier dirección
- **THEN** los activos con null siempre aparecen al final de la lista



### Requirement: Campos extendidos en modelo Asset
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

#### Scenario: NULLS LAST en last_backup_local
- **GIVEN** activos con y sin last_backup_local
- **WHEN** se ordena por ese campo en cualquier dirección
- **THEN** los activos con null siempre aparecen al final de la lista
