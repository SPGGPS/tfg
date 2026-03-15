# API - Inventario y activos

## ADDED Requirements

### Requirement: Modelo Asset polimórfico

El modelo Asset SHALL incluir un discriminador 'type' con valores: `server_physical`, `server_virtual`, `switch`, `router`, `ap`, `database`.

#### Scenario: Tipos de activo soportados
- **GIVEN** un activo en el inventario
- **WHEN** se consulta su tipo
- **THEN** el campo type debe ser uno de: server_physical, server_virtual, switch, router, ap, database

### Requirement: Campos específicos para tipo database
El modelo Asset SHALL incluir campos opcionales específicos para activos de tipo `database`, divididos en dos niveles: campos de resumen (visibles en tabla) y campos de detalle (visibles solo en la página de detalle).

**Campos de resumen (en tabla y detalle):**
- `db_engine` (string enum) — motor de base de datos. Valores válidos:

  | Familia | Valores del enum |
  |---------|-----------------|
  | Relacional open-source | `postgresql`, `mysql`, `mariadb`, `sqlite`, `percona` |
  | Relacional comercial | `oracle`, `oracle_xe`, `sqlserver`, `sqlserver_express`, `sqlserver_standard`, `sqlserver_enterprise`, `db2`, `sybase` |
  | NoSQL documental | `mongodb`, `couchdb`, `couchbase`, `firestore`, `documentdb` |
  | NoSQL clave-valor | `redis`, `memcached`, `dynamodb`, `keydb` |
  | NoSQL columnar | `cassandra`, `hbase`, `scylladb`, `bigquery`, `clickhouse` |
  | NoSQL grafo | `neo4j`, `arangodb`, `janusgraph` |
  | Búsqueda / analítica | `elasticsearch`, `opensearch`, `solr`, `splunk` |
  | Cloud managed | `aurora_mysql`, `aurora_postgresql`, `azure_sql`, `azure_cosmos`, `cloud_spanner`, `cloud_sql`, `neon`, `planetscale` |
  | Warehouse / OLAP | `snowflake`, `redshift`, `databricks`, `synapse` |
  | Time-series | `influxdb`, `timescaledb`, `prometheus` |
  | `other` | Cualquier otro motor — especificar en db_notes |

- `db_version` (string) — versión del motor (ej. "16.2", "19c Enterprise", "2022 SP1")
- `db_size_gb` (float) — tamaño total de datos en GB
- `db_port` (int) — puerto de escucha principal
- `db_replication` (bool, default False) — tiene replicación activa
- `db_cluster` (string | null) — nombre del cluster, grupo de disponibilidad (AlwaysOn, RAC, Patroni, etc.) o replica set (MongoDB)
- `db_is_cluster` (bool, default False) — indica si es un nodo de un cluster HA (vs instancia standalone)
- `db_vip` (string | null) — Virtual IP o FQDN del listener del cluster (ej. "10.0.1.100" o "db-cluster.ssreyes.local"). Solo aplicable cuando `db_is_cluster=true`.
- `db_host_asset_id` (string UUID | null) — FK opcional al Asset (server_physical o server_virtual) que aloja físicamente esta instancia de base de datos. Permite navegar del activo de base de datos al servidor host y viceversa.
- `db_host_display` (string | null) — nombre o IP del servidor host tal como se muestra en UI. Si `db_host_asset_id` existe, se rellena automáticamente con el nombre del asset referenciado; si no, es un campo libre.

**Campos de detalle extendido (solo en GET /v1/assets/{id}):**
- `db_schemas` (array de objetos) — esquemas o bases de datos alojados. La estructura del objeto es común a todos los motores:
  - `name` (string) — nombre del esquema/database/keyspace/índice según el motor
  - `size_gb` (float | null) — tamaño en GB
  - `table_count` (int | null) — número de tablas, colecciones, índices o equivalentes
  - `owner` (string | null) — propietario o schema owner
  - `charset` (string | null) — juego de caracteres/codificación del esquema (MySQL/MariaDB)
  - `collation` (string | null) — collation del esquema
  - `description` (string | null) — descripción libre
  Nota terminológica por motor: PostgreSQL → schemas; MySQL/MariaDB/SQLServer → databases; Oracle → schemas/PDB; MongoDB → databases; Cassandra/ScyllaDB → keyspaces; Elasticsearch/OpenSearch → indices; Redis → databases (0-15).
- `db_cluster_nodes` (array de objetos | null) — nodos del cluster cuando `db_is_cluster=true`. Cada objeto:
  - `hostname` (string) — nombre o IP del nodo
  - `role` (string) — rol del nodo: `primary`, `replica`, `standby`, `arbiter`, `shard`, `config`
  - `asset_id` (string UUID | null) — FK al Asset servidor que es este nodo
  - `status` (string | null) — `online`, `offline`, `syncing`, `unknown`
- `db_users` (array de objetos) — usuarios/roles de la base de datos. Cada objeto:
  - `username` (string)
  - `role` (string enum) — `dba`, `read_only`, `read_write`, `backup`, `monitoring`, `app`, `service`, `other`
  - `last_login` (datetime | null)
- `db_connections_max` (int | null) — conexiones máximas configuradas
- `db_connections_active` (int | null) — conexiones activas en última sync
- `db_encoding` (string | null) — codificación del servidor (ej. "UTF-8", "AL32UTF8", "LATIN1")
- `db_timezone` (string | null) — zona horaria configurada
- `db_ha_mode` (string enum | null) — `primary`, `replica`, `standby`, `arbiter`, `standalone`, `unknown`
- `db_ssl_enabled` (bool | null) — conexiones SSL/TLS requeridas
- `db_audit_enabled` (bool | null) — auditoría de accesos activada en el motor
- `db_last_vacuum` (datetime | null) — último mantenimiento/vacuum (PostgreSQL/MySQL)
- `db_notes` (text | null) — notas libres del administrador

#### Scenario: Campos de resumen para tipo database
- **GIVEN** un activo de tipo database en la tabla de inventario
- **WHEN** se visualiza la fila
- **THEN** la columna "Tipo" muestra el badge "BD" y el fabricante muestra el db_engine (ej. "PostgreSQL")

#### Scenario: Campos de detalle para tipo database
- **GIVEN** un activo de tipo database
- **WHEN** se consulta GET /v1/assets/{id}
- **THEN** incluye db_schemas, db_users, db_connections_max, db_connections_active, db_encoding, db_timezone, db_ha_mode, db_ssl_enabled, db_audit_enabled

### Requirement: Endpoint POST /v1/assets/bulk-tags

El sistema SHALL exponer POST /v1/assets/bulk-tags para asignar etiquetas manuales a múltiples asset_ids simultáneamente.

#### Scenario: Asignación masiva exitosa
- **GIVEN** un admin con asset_ids y tag_ids válidos
- **WHEN** realiza POST /v1/assets/bulk-tags con esos IDs
- **THEN** todos los activos reciben las etiquetas especificadas

### Requirement: Campos de cumplimiento en Asset — derivados del origen de datos

El modelo Asset SHALL incluir los siguientes campos de compliance. **Todos son de solo escritura por el sistema de ingesta** — se establecen automáticamente cuando el origen de datos correspondiente reporta la presencia o ausencia del servicio. No son editables manualmente por usuarios.

| Campo | Tipo | Origen de datos | Verde cuando… |
|-------|------|----------------|---------------|
| `edr_installed` | bool | EDR (CrowdStrike / SentinelOne) | El agente EDR reporta el activo como protegido y activo |
| `monitored` | bool | Monitorización (Zabbix / Nagios) | El activo está dado de alta y enviando métricas |
| `siem_enabled` | bool | SIEM / Syslog | El activo está enviando logs al SIEM |
| `logs_enabled` | bool | Monitorización / Syslog | La generación de logs del sistema está activa |
| `last_backup_local` | datetime \| null | Veeam (backup local/on-prem) | Veeam reporta un backup completado; contiene la fecha del último backup exitoso |
| `last_backup_cloud` | datetime \| null | Veeam (backup cloud/offsite) | Veeam reporta un backup cloud completado; contiene la fecha del último backup exitoso |
| `last_sync` | datetime | Cualquier fuente | Timestamp de la última sincronización recibida de cualquier origen |

**Lógica de color en UI:**
- **Verde**: el campo bool es `true`, o el campo datetime tiene valor (backup reciente)
- **Rojo**: el campo bool es `false`, o el campo datetime es `null` (nunca se ha recibido backup de ese origen)
- Un activo puede no tener fuente EDR asociada (p.ej. un switch): en ese caso `edr_installed = false` → rojo, lo cual es correcto y esperado

#### Scenario: Agente EDR reporta activo protegido
- **GIVEN** CrowdStrike reporta que el activo "web-prod-01" tiene agente activo
- **WHEN** el CronJob de ingesta del EDR procesa los datos
- **THEN** `edr_installed = true` y el rectángulo EDR aparece en verde en la UI

#### Scenario: Veeam no reporta backup cloud para un activo
- **GIVEN** Veeam local tiene backup pero no hay política de backup cloud configurada para "db-prod-01"
- **WHEN** el CronJob de ingesta de Veeam procesa los datos
- **THEN** `last_backup_local` tiene fecha, `last_backup_cloud = null`, BCK verde, BCKCL rojo

#### Scenario: Switch sin agente EDR
- **GIVEN** un switch Cisco que no puede ejecutar agente EDR
- **WHEN** se ingesta desde Monica/Zabbix
- **THEN** `edr_installed = false` → rectángulo EDR en rojo; es el estado esperado para este tipo de activo

#### Scenario: Activo recién descubierto sin datos de compliance
- **GIVEN** un activo recién ingresado desde VMware sin datos aún de Veeam, EDR ni monitorización
- **WHEN** se muestra en la tabla
- **THEN** todos los indicadores de compliance aparecen en rojo hasta que los orígenes correspondientes reporten sus datos en la siguiente sincronización

### Requirement: Campos básicos del activo
El modelo Asset SHALL incluir campos descriptivos básicos:
- `name` (string) - nombre del activo
- `ips` (array de strings) - lista de direcciones IP asociadas
- `vendor` (string) - fabricante o proveedor (ej. Cisco, VMware, Dell)
- `source` (string) - origen de los datos (ej. VMware, Veeam, Monica, ServiceNow, EDR, Monitorización)

#### Scenario: Respuesta con datos básicos
- **GIVEN** un cliente que consulta GET /v1/assets
- **WHEN** recibe la respuesta
- **THEN** cada activo incluye name, ips, vendor y source

### Requirement: Campos específicos por tipo de activo
El modelo Asset SHALL incluir campos opcionales específicos según el tipo, para proporcionar detalles técnicos.

#### Scenario: Campos para servidores (server_physical o server_virtual)
- **GIVEN** un activo de tipo server_physical o server_virtual
- **WHEN** se consulta su detalle
- **THEN** incluye campos: ram_gb (int), total_disk_gb (int), cpu_count (int), os (string)

#### Scenario: Campos para routers
- **GIVEN** un activo de tipo router
- **WHEN** se consulta su detalle
- **THEN** incluye campos: model (string), port_count (int), firmware_version (string)

#### Scenario: Campos para switches
- **GIVEN** un activo de tipo switch
- **WHEN** se consulta su detalle
- **THEN** incluye campos: model (string), port_count (int), max_speed (string)

#### Scenario: Campos para access points (ap)
- **GIVEN** un activo de tipo ap
- **WHEN** se consulta su detalle
- **THEN** incluye campos: model (string), coverage_area (string), connected_clients (int)

#### Scenario: Campos para bases de datos (database) — resumen
- **GIVEN** un activo de tipo database
- **WHEN** se consulta GET /v1/assets (listado)
- **THEN** incluye: db_engine (enum), db_version, db_size_gb, db_host, db_port, db_replication, db_cluster

#### Scenario: Campos para bases de datos (database) — detalle extendido
- **GIVEN** un activo de tipo database
- **WHEN** se consulta GET /v1/assets/{id} (detalle)
- **THEN** incluye además: db_schemas (array con name/size_gb/table_count/owner), db_users (array con username/role/last_login), db_connections_max, db_connections_active, db_encoding, db_timezone, db_ha_mode, db_ssl_enabled, db_audit_enabled, db_last_vacuum, db_notes



### Requirement: Autenticación con OpenID Connect
Todos los endpoints de inventario SHALL requerir autorización mediante OpenID Connect (Keycloak).

#### Scenario: Token OpenID válido
- **GIVEN** un cliente con un token OIDC válido
- **WHEN** realiza GET /v1/assets
- **THEN** recibe HTTP 200 con la lista de activos

#### Scenario: Token inválido o expirado
- **GIVEN** un cliente con un token caducado o inválido
- **WHEN** realiza GET /v1/assets
- **THEN** recibe HTTP 401 Unauthorized

### Requirement: Campos extendidos del activo
El modelo Asset SHALL incluir campos adicionales para mayor trazabilidad y gestión:
- `serial_number` (string | null) — número de serie del hardware
- `location` (string | null) — ubicación física (rack, sala, edificio)
- `description` (string | null) — descripción libre del activo
- `purchase_date` (date | null) — fecha de compra
- `warranty_expiry` (date | null) — fecha de expiración de garantía

Estos campos son opcionales y buscables desde el endpoint GET /v1/assets mediante el parámetro `search`.

#### Scenario: Búsqueda por número de serie
- **GIVEN** un activo con serial_number "SN-ABC-12345"
- **WHEN** un cliente realiza GET /v1/assets?search=SN-ABC-12345
- **THEN** el activo aparece en los resultados

### Requirement: Endpoint de detalle extendido de activo
El endpoint GET /v1/assets/{id} SHALL devolver todos los campos del activo incluyendo los campos extendidos, los últimos registros de auditoría relacionados y la lista completa de etiquetas.

#### Scenario: Detalle con historial
- **GIVEN** un activo con registros de auditoría
- **WHEN** se llama GET /v1/assets/{id}
- **THEN** la respuesta incluye un array `recent_audit` con los últimos 10 cambios

### Requirement: Filtro por múltiples etiquetas en GET /v1/assets
El endpoint GET /v1/assets SHALL aceptar el parámetro `tag_ids` como lista de IDs de etiquetas separados por coma. La lógica de filtrado es **AND**: solo se devuelven activos que tengan **todas** las etiquetas indicadas.

- `tag_ids` (string, opcional): IDs de etiquetas separados por coma. Ejemplo: `?tag_ids=id1,id2,id3`
- Si `tag_ids` está vacío o no se proporciona, no se aplica ningún filtro de etiqueta.
- El filtro AND se implementa con múltiples `.filter(Asset.tags.any(Tag.id == tag_id))` encadenados, uno por cada ID del array.
- El parámetro es compatible con todos los demás filtros (type, search, edr_installed, etc.) y con la paginación y ordenación.

El parámetro singular `tag_id` (un solo ID) queda **deprecado** en favor de `tag_ids`. El backend SHALL aceptar ambos durante el período de transición: si se proporciona `tag_id`, se trata como `tag_ids` de un elemento.

#### Scenario: Filtrar por una etiqueta
- **GIVEN** GET /v1/assets?tag_ids=id-produccion
- **THEN** devuelve solo activos que tengan la etiqueta "Producción"

#### Scenario: Filtrar por dos etiquetas (AND)
- **GIVEN** GET /v1/assets?tag_ids=id-produccion,id-cisco
- **THEN** devuelve solo activos que tengan AMBAS etiquetas "Producción" y "Cisco"

#### Scenario: Sin filtro de etiqueta
- **GIVEN** GET /v1/assets (sin tag_ids)
- **THEN** devuelve todos los activos sin filtrar por etiqueta

#### Scenario: tag_ids con ID inexistente
- **GIVEN** GET /v1/assets?tag_ids=id-real,id-inventado
- **THEN** devuelve array vacío (ningún activo tiene ambas etiquetas si una no existe), sin error 404

---

### Requirement: Campo source — origen del activo
El campo `source` (string, nullable) en el modelo Asset SHALL registrar el sistema o proceso que creó o actualizó por última vez el activo en el inventario. Es un campo libre pero el sistema de ingesta SHOULD usar valores canónicos para que la detección de badge en frontend sea fiable.

**Valores canónicos recomendados para `source`:**
| Sistema | Valor recomendado |
|---------|------------------|
| VMware vCenter API | `vmware` o `vcenter` |
| Veeam Backup | `veeam` |
| CrowdStrike API | `crowdstrike` |
| SentinelOne API | `sentinelone` |
| Zabbix API | `zabbix` |
| Nagios/ICINGA | `nagios` |
| Ansible playbook | `ansible` |
| Monica / otro inventario | `monica` o `inventario` |
| Script / cron job propio | `script` o `cron` |
| Entrada manual por admin | `manual` |
| Syslog / SIEM | `syslog` |
| API genérica REST | `api` |

El campo `source` es incluido en la búsqueda full-text (`search`) y es ordenable (`sort_by=source`).

#### Scenario: Activo ingresado desde VMware con source correcto
- **GIVEN** un CronJob que llama a la API de vCenter
- **WHEN** ingesta activos vía POST /v1/assets/ingest
- **THEN** cada activo incluye source="vmware" para que el frontend muestre el badge correcto

---

### Requirement: Búsqueda extendida en GET /v1/assets
El parámetro `search` SHALL buscar en todos los campos textuales: name, ips, vendor, source, os, model, serial_number, location, description, firmware_version, mac_address y nombres de etiquetas asignadas.

#### Scenario: Búsqueda full-text
- **GIVEN** un cliente con search=cisco
- **WHEN** realiza GET /v1/assets?search=cisco
- **THEN** devuelve activos cuyo vendor, model o etiquetas contengan "cisco" (case-insensitive)

### Requirement: Parámetros de ordenación en GET /v1/assets
El endpoint GET /v1/assets SHALL aceptar los parámetros `sort_by` y `sort_order` para ordenar resultados. El parámetro `sort_by` SHALL aceptar los valores: `name`, `type`, `vendor`, `source`, `last_sync`, `created_at`, `last_backup_local`, `last_backup_cloud`. Para campos datetime nullable (`last_backup_local`, `last_backup_cloud`), los registros con valor NULL SHALL ordenarse al final independientemente del sentido de la ordenación (NULLS LAST).

#### Scenario: Ordenar por last_backup_local con NULLS LAST
- **GIVEN** una consulta GET /v1/assets?sort_by=last_backup_local&sort_order=asc
- **WHEN** hay activos con y sin backup local
- **THEN** los activos con backup aparecen ordenados por fecha ascendente; los que tienen last_backup_local=null aparecen al final

---

### Requirement: Endpoints de certificados accesibles desde inventario

Los certificados gestionados en la subtab de Inventario se sirven desde los endpoints definidos en el change `applications`:
- `GET    /v1/certificates` — lista con filtros (status, environment, search, expiring_days)
- `GET    /v1/certificates/{id}` — detalle con bindings de aplicaciones
- `POST   /v1/certificates` — crear
- `PUT    /v1/certificates/{id}` — actualizar
- `DELETE /v1/certificates/{id}` — eliminar
- `GET    /v1/certificates/expiry-summary` — resumen de estados para el banner

La página de Inventario (tab Certificados) consume estos endpoints directamente. No se duplican ni se crean endpoints paralelos. El change `inventory-master` solo define la vista frontend; el contrato de API vive en `applications`.

#### Scenario: Navegación entre inventario y certificados
- **GIVEN** un usuario en el tab Inventario en `/`
- **WHEN** hace click en el tab "Certificados"
- **THEN** navega a `/certificates` y la tabla carga datos de GET /v1/certificates?sort_by=expires_at&sort_order=asc
