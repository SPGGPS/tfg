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
  - Relacionales: `postgresql`, `mysql`, `mariadb`, `oracle`, `oracle_xe`, `sqlserver`, `sqlserver_express`, `sqlserver_standard`, `sqlserver_developer`, `sqlserver_azure`, `db2`, `sqlite`
  - NoSQL documentales: `mongodb`, `couchdb`, `firestore`
  - NoSQL clave-valor: `redis`, `memcached`, `dynamodb`
  - NoSQL columnar: `cassandra`, `hbase`, `bigquery`
  - NoSQL grafo: `neo4j`, `arangodb`
  - Búsqueda: `elasticsearch`, `opensearch`, `solr`
  - Cloud managed: `aurora_mysql`, `aurora_postgresql`, `azure_sql`, `cloud_spanner`, `cloud_sql`
  - `other` — para cualquier otro motor
- `db_version` (string) — versión del motor (ej. "16.2", "19c", "2022")
- `db_size_gb` (int) — tamaño total de los datos en GB
- `db_host` (string) — hostname o IP del servidor que aloja la base de datos
- `db_port` (int) — puerto de escucha
- `db_replication` (bool, default False) — tiene replicación activa
- `db_cluster` (string | null) — nombre del cluster o grupo de disponibilidad

**Campos de detalle extendido (solo en GET /v1/assets/{id}):**
- `db_schemas` (array de objetos) — esquemas/bases de datos alojados. Cada objeto contiene:
  - `name` (string) — nombre del esquema
  - `size_gb` (float | null) — tamaño en GB
  - `table_count` (int | null) — número de tablas
  - `owner` (string | null) — propietario o schema owner
- `db_users` (array de objetos) — usuarios/roles de la base de datos. Cada objeto contiene:
  - `username` (string) — nombre del usuario
  - `role` (string) — rol (ej. "dba", "read_only", "read_write", "backup", "monitoring")
  - `last_login` (datetime | null) — último acceso registrado
- `db_connections_max` (int | null) — número máximo de conexiones configurado
- `db_connections_active` (int | null) — conexiones activas en el momento de la última sync
- `db_encoding` (string | null) — codificación del servidor (ej. "UTF-8", "AL32UTF8")
- `db_timezone` (string | null) — zona horaria configurada
- `db_ha_mode` (string | null) — modo de alta disponibilidad (ej. "primary", "replica", "standby", "none")
- `db_ssl_enabled` (bool | null) — conexiones SSL/TLS obligatorias
- `db_audit_enabled` (bool | null) — auditoría de accesos activada en el motor
- `db_last_vacuum` (datetime | null) — fecha del último mantenimiento/vacuum (PostgreSQL/MySQL)
- `db_notes` (text | null) — notas libres del administrador sobre esta instancia

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
