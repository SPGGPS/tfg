# Frontend - Dashboard de inventario

## ADDED Requirements

---

### Requirement: Estructura de la página de inventario — tabs principal e Inventario / Certificados

La ruta `/` (inventario) SHALL mostrar **dos pestañas** en la cabecera de la página:

| Tab | Descripción |
|-----|-------------|
| **Inventario** (default) | Tabla actual de assets: servidores, switches, routers, APs, bases de datos |
| **Certificados** | Tabla dedicada a certificados TLS/SSL — entidad `Certificate` del módulo de aplicaciones |

Los tabs usan la misma barra de navegación visual que `/applications`. La URL cambia a `/certificates` al seleccionar el segundo tab, y vuelve a `/` al seleccionar Inventario.

**Motivación del diseño:** los certificados no comparten columnas con el resto de activos (no tienen IPs relevantes, no tienen EDR, no tienen backup local/cloud), por lo que una tabla conjunta resulta confusa. La subtab los trata como una vista propia con sus columnas específicas.

---

### Requirement: Tab "Certificados" — tabla dedicada de certificados TLS/SSL

La tabla de certificados SHALL mostrar las siguientes columnas específicas, completamente distintas a las del inventario de assets:

**Columnas:**
| Columna | Campo | Notas |
|---------|-------|-------|
| Common Name | `common_name` | Nombre principal del cert; link al detalle |
| SANs | `san_domains` | Lista de dominios alternativos, truncada con tooltip |
| Emisor | `issuer` | Let's Encrypt, FNMT, DigiCert… |
| Estado | `cert_status` (calculado) | Badge de color — ver tabla de estados |
| Días restantes | `days_remaining` (calculado) | Número con color dinámico |
| Caduca | `expires_at` | Fecha formateada dd/MM/yyyy |
| Tipo clave | `key_type` | RSA 2048, ECDSA P-256… |
| Wildcard | `wildcard` | ✓ o — |
| Renovación auto | `auto_renew` | ✓ o — |
| Gestionado por | `managed_by` | cert-manager, manual, FNMT… |
| Entorno | `environment` | Badge Producción/Staging/Desarrollo/DR |
| Acciones | — | Editar, Eliminar |

**Badges de estado de caducidad:**
| Estado | Color | Label | Condición |
|--------|-------|-------|-----------|
| `valid` | `bg-green-900/60 text-green-300` | ✓ Válido | expires_at > hoy + 30d |
| `expiring` | `bg-orange-900/60 text-orange-300` | ⚠ Caduca pronto | expires_at ≤ hoy + 30d |
| `critical` | `bg-red-900 text-red-200 animate-pulse` | 🔴 Crítico | expires_at ≤ hoy + 7d |
| `expired` | `bg-red-950 text-red-400` | ❌ Expirado | expires_at ≤ hoy |

**Columna "Días restantes":**
- > 30 días → texto verde
- 8–30 días → texto naranja con `⚠`
- 1–7 días → texto rojo pulsante con `🔴`
- ≤ 0 → texto `❌ Expirado hace N días` en rojo

**Barra de resumen encima de la tabla** (desde `/v1/certificates/expiry-summary`):
```
[24 total]  [18 válidos ✓]  [4 próximos a caducar ⚠]  [1 crítico 🔴]  [1 expirado ❌]
```
Cada contador es clickable y aplica el filtro correspondiente en la tabla.

**Alerta sticky** cuando hay certificados `critical` o `expired`:
```
🔴 1 certificado caduca en 3 días: sede.ssreyes.es  [Ver]
```

**Filtros disponibles:**
- Búsqueda libre: common_name, issuer, san_domains
- Estado: Todos / Válido / Caduca pronto / Crítico / Expirado
- Entorno: Todos / Producción / Staging / Desarrollo / DR
- Renovación auto: Todos / Sí / No

**Ordenación:** por defecto `expires_at ASC` (los que caducan antes aparecen primero).

**Formulario de creación/edición** (modal, accesible con "+ Nuevo certificado", rol editor+):
- `common_name` — obligatorio, placeholder: `sede.ssreyes.es`
- `san_domains` — input de chips (Enter para añadir), placeholder: `api.ssreyes.es`
- `issuer` — input libre: `Let's Encrypt`, `FNMT`, `DigiCert`
- `issued_at` — date picker (opcional)
- `expires_at` — date picker, **obligatorio**, resaltado si es < 30 días desde hoy
- `serial_number` — input texto (opcional)
- `key_type` — select: RSA 2048 / RSA 4096 / ECDSA P-256 / ECDSA P-384 / Ed25519 / Otro
- `wildcard` — checkbox
- `auto_renew` — checkbox
- `managed_by` — input libre: `cert-manager`, `manual`, `Keycloak`, `FNMT`
- `environment` — select
- `notes` — textarea

**Página de detalle del certificado** (al hacer click en el Common Name):
Ruta `/certificates/:id`. Muestra todos los campos del certificado más:
- **Aplicaciones que lo usan**: lista de `AppInfraBinding` donde `certificate_id` = este certificado, con link a cada aplicación y al servicio del que forma parte
- **Mapa de impacto**: si el certificado expira, ¿qué aplicaciones y servicios se ven afectados?
- **Historial de cambios**: últimos registros de audit_log

**Viewer** no ve botones de crear/editar/eliminar.

#### Scenario: Banner de resumen con certificado crítico
- **GIVEN** 1 certificado con expires_at en 4 días
- **WHEN** el usuario abre el tab Certificados
- **THEN** el contador "1 crítico 🔴" aparece resaltado y el banner de alerta sticky es visible

#### Scenario: Tabla ordenada por caducidad
- **GIVEN** varios certificados con distintas fechas de caducidad
- **WHEN** se carga el tab por defecto
- **THEN** el certificado que caduca antes aparece en la primera fila

#### Scenario: Filtrar por estado "Caduca pronto"
- **GIVEN** el usuario pulsa el contador "4 próximos a caducar ⚠"
- **THEN** la tabla filtra y muestra solo los 4 certificados con status=expiring

#### Scenario: Detalle con aplicaciones que lo usan
- **GIVEN** el certificado "sede.ssreyes.es" está vinculado a la aplicación "sede-frontend"
- **WHEN** el usuario accede al detalle del certificado
- **THEN** ve la sección "Aplicaciones que usan este certificado" con "sede-frontend → Sede Electrónica"

#### Scenario: Viewer no puede crear certificados
- **GIVEN** un usuario con rol viewer en el tab Certificados
- **WHEN** visualiza la tabla
- **THEN** no aparece el botón "+ Nuevo certificado" ni botones de editar/eliminar

---

### Requirement: Ordenación por columna con iconos ↑↓
El dashboard SHALL mostrar iconos de ordenación (↑↓) en el encabezado de cada columna ordenable (todas excepto Etiquetas y Compliance). Al hacer click en el encabezado se ordena asc; segundo click desc. No habrá combo ni botón separado para ordenar.

Las columnas ordenables y sus campos de API correspondientes son:
- **Nombre** → `name`
- **Tipo** → `type`
- **Fabricante** → `vendor`
- **Backup Local** → `last_backup_local` (nullable datetime — los null van al final en ambos sentidos)
- **Backup Cloud** → `last_backup_cloud` (nullable datetime — los null van al final en ambos sentidos)
- **Última sync** → `last_sync`
- **Creado** → `created_at`

#### Scenario: Ordenar por Backup Local
- **GIVEN** un usuario hace click en la cabecera "Backup Local"
- **WHEN** se aplica la ordenación ascendente
- **THEN** los activos con backup más antiguo aparecen primero; los activos sin backup (null) aparecen al final

#### Scenario: Ordenar por Backup Cloud
- **GIVEN** un usuario hace click en la cabecera "Backup Cloud"
- **WHEN** se aplica la ordenación descendente
- **THEN** los activos con backup cloud más reciente aparecen primero; los activos sin backup cloud (null) aparecen al final

#### Scenario: Columnas Etiquetas y Compliance no son ordenables
- **GIVEN** un usuario en la tabla
- **WHEN** visualiza las columnas Etiquetas y Compliance
- **THEN** no aparece ningún icono de ordenación en esas cabeceras

### Requirement: Búsqueda extendida por todos los campos
El campo de búsqueda SHALL filtrar por todos los campos del activo incluyendo campos no visibles en la tabla principal: nombre, IPs, vendor, OS, número de serie, modelo, firmware, MAC address, etiquetas (por nombre), y cualquier campo de datos extendidos. La búsqueda es case-insensitive y busca en todos los campos simultáneamente.

#### Scenario: Búsqueda por número de serie
- **GIVEN** un usuario introduce un número de serie en el campo de búsqueda
- **WHEN** el texto coincide con el serial_number de un activo
- **THEN** ese activo aparece en los resultados aunque serial_number no sea una columna visible

#### Scenario: Búsqueda por nombre de etiqueta
- **GIVEN** un usuario introduce "Producción" en el campo de búsqueda
- **WHEN** hay activos con la etiqueta "Producción"
- **THEN** esos activos aparecen en los resultados

#### Scenario: Búsqueda por IP
- **GIVEN** un usuario introduce una IP parcial o completa
- **WHEN** hay activos con esa IP en su array de IPs
- **THEN** esos activos aparecen en los resultados

### Requirement: Indicadores de compliance como rectángulos con etiqueta
Los indicadores de estado de cumplimiento SHALL mostrarse como rectángulos (badges) con texto corto. **El color de cada rectángulo refleja lo que el origen de datos externo ha reportado en la última ingesta**, no un valor introducido manualmente por el usuario.

Los 6 indicadores y su origen son:

| Badge | Origen del dato | Verde cuando… |
|-------|----------------|---------------|
| `EDR` | CrowdStrike / SentinelOne | El agente reporta el activo como protegido (`edr_installed = true`) |
| `MON` | Zabbix / Nagios | El activo envía métricas a monitorización (`monitored = true`) |
| `SIEM` | SIEM / Syslog | El activo envía logs al SIEM (`siem_enabled = true`) |
| `LOGS` | Monitorización / Syslog | Generación de logs activa (`logs_enabled = true`) |
| `BCK` | Veeam local/on-prem | Veeam ha reportado backup exitoso (`last_backup_local` tiene fecha) |
| `BCKCL` | Veeam cloud/offsite | Veeam ha reportado backup cloud exitoso (`last_backup_cloud` tiene fecha) |

**Verde** (`bg-green-900/60 text-green-300 border-green-700`): el origen reporta presencia/OK.
**Rojo** (`bg-red-900/60 text-red-300 border-red-700`): el origen no reporta ese servicio, o nunca se han recibido datos de ese origen para este activo.

Para BCK y BCKCL: tooltip al hacer hover con la fecha del último backup. Si es null: "Sin datos de Veeam local" / "Sin datos de Veeam cloud". Font: `text-[10px] font-bold tracking-wide`.

#### Scenario: Switch sin EDR — rojo es correcto y esperado
- **GIVEN** un switch Cisco que no puede ejecutar agente EDR
- **WHEN** el dato de EDR no llega de ningún origen de ingesta
- **THEN** EDR aparece en rojo; es el estado correcto, no un error

#### Scenario: Servidor con todos los orígenes en OK
- **GIVEN** un servidor con EDR activo, Zabbix, SIEM, Veeam local y Veeam cloud
- **WHEN** todos los CronJobs de ingesta han procesado sus datos
- **THEN** los 6 rectángulos aparecen en verde

#### Scenario: Tooltip en BCK
- **GIVEN** un activo con last_backup_local = "2026-03-15T06:00:00Z"
- **WHEN** el usuario hace hover sobre BCK
- **THEN** aparece tooltip "Último backup local: 15/03/2026 06:00"

### Requirement: Columnas de backup separadas
La columna de backup SHALL dividirse en dos columnas independientes visibles en la tabla:
- **Backup Local** — fecha de `last_backup_local` o "Sin backup"
- **Backup Cloud** — fecha de `last_backup_cloud` o "Sin backup"

#### Scenario: Columnas de backup
- **GIVEN** un usuario en el dashboard
- **WHEN** visualiza la tabla
- **THEN** hay dos columnas "Backup Local" y "Backup Cloud" con sus fechas

### Requirement: Página de detalle de activo
Al hacer click en el nombre de un activo SHALL abrirse una página de detalle (`/assets/:id`) que muestre toda la información extendida no visible en la tabla principal:
- Información general: id, name, type, ips, mac_address, vendor, source, data_source
- Compliance completo: EDR, MON, SIEM, LOGS, BCK (con fecha), BCKCL (con fecha), monica_registered
- Campos específicos por tipo: ram_gb, total_disk_gb, cpu_count, os (servidores); model, port_count, firmware_version, max_speed (switches/routers); model, coverage_area, connected_clients (APs); db_engine, db_version, db_size_gb, db_host, db_port, db_replication, db_cluster (databases)
- Campos extendidos: serial_number, location, description, purchase_date, warranty_expiry
- Etiquetas asignadas (manuales y de sistema)
- Historial de cambios: últimos registros de audit_log relacionados con ese asset_id
- Timestamps: created_at, updated_at, last_sync

#### Scenario: Acceder al detalle de un activo
- **GIVEN** un usuario en el dashboard de inventario
- **WHEN** hace click en el nombre de un activo
- **THEN** navega a /assets/:id y ve toda la información extendida del activo

#### Scenario: Historial de cambios en detalle
- **GIVEN** un activo con registros de auditoría
- **WHEN** el usuario accede a su página de detalle
- **THEN** ve los últimos N cambios registrados (actividad, usuario, fecha, diff)

### Requirement: Filtro por tipo con selector
El dashboard SHALL incluir un selector de tipo de activo para filtrar la tabla. Los tipos disponibles son: `server_physical`, `server_virtual`, `switch`, `router`, `ap`, `database`.

#### Scenario: Filtrar por tipo database
- **GIVEN** un usuario selecciona "database"
- **WHEN** se aplica el filtro
- **THEN** solo aparecen activos de tipo database en la tabla

### Requirement: Badge visual para tipo database
El tipo `database` SHALL mostrarse con un badge de color diferenciado del resto (`bg-cyan-900 text-cyan-200`) y la etiqueta "BD" en la columna Tipo de la tabla. En la columna "Fabricante" se mostrará el `db_engine` en lugar del campo `vendor` cuando el tipo es database.

#### Scenario: Badge de tipo database
- **GIVEN** un activo de tipo database en la tabla
- **WHEN** se muestra la columna "Tipo"
- **THEN** aparece un badge "BD" en color cyan

### Requirement: Página de detalle extendido para tipo database
Al hacer click en el nombre de un activo de tipo `database`, la página de detalle SHALL mostrar secciones específicas adicionales a las comunes:

**Sección "Instancia de Base de Datos":**
- Motor (db_engine) con badge visual diferenciado por familia (ver colores abajo)
- Versión (db_version)
- Puerto (db_port)
- Tamaño total (db_size_gb en GB)
- Replicación activa (badge verde/rojo)
- Modo HA (db_ha_mode: primary / replica / standby / standalone / unknown)
- SSL/TLS (badge verde/rojo)
- Auditoría del motor (badge verde/rojo)
- Codificación (db_encoding)
- Zona horaria (db_timezone)
- Último vacuum/mantenimiento (db_last_vacuum)
- Conexiones máximas / activas
- Notas del administrador (db_notes)

**Sección "Infraestructura y Alta Disponibilidad":**
Esta sección es la más importante para un CMDB. SHALL mostrar:
- **Servidor host**: si `db_host_asset_id` existe, muestra un enlace al activo servidor (`db_host_display`), clickable para navegar a su detalle. Si no existe, muestra `db_host_display` como texto simple.
- **¿Es cluster?**: badge "Cluster HA" (verde) o "Standalone" (gris) según `db_is_cluster`.
- **Nombre del cluster / Grupo de disponibilidad**: `db_cluster` (ej. "AlwaysOn-PROD", "Patroni-PG01", "RAC-ORACLE", "rs0").
- **VIP / Listener**: `db_vip` — la IP virtual o FQDN por el que se conectan las aplicaciones. Solo visible si `db_is_cluster=true`. Mostrado con un icono de red y texto "VIP del cluster".
- **Nodos del cluster** (`db_cluster_nodes`): tabla con columnas Hostname, Rol, Estado, Asset. El campo Asset es un enlace al activo servidor si `asset_id` está relleno. Los roles se muestran con badges: `primary` (verde), `replica` (azul), `standby` (amarillo), `arbiter` (gris), `shard` (cyan), `config` (púrpura).

Si el activo es standalone (`db_is_cluster=false`), la sección solo muestra el servidor host y oculta VIP y nodos.

**Sección "Esquemas / Bases de datos alojadas" (tabla):**
- Columnas: Nombre, Tamaño (GB), Nº objetos (tablas/colecciones/índices), Propietario, Charset, Descripción
- La cabecera "Nº objetos" muestra el término correcto según el motor: "Tablas" para relacionales, "Colecciones" para MongoDB/CouchDB, "Índices" para Elasticsearch/OpenSearch, "Keyspaces" para Cassandra.
- Si `db_schemas` está vacío o null: mensaje "Sin datos de esquemas — requiere sincronización con el origen de datos"

**Sección "Usuarios y roles" (tabla):**
- Columnas: Usuario, Rol, Último acceso
- Badges por rol: `dba` (rojo), `read_write` (naranja), `read_only` (gris), `backup` (azul), `monitoring` (teal), `app` (verde), `service` (cyan), `other` (gris oscuro)
- Si vacío: "Sin datos de usuarios — requiere sincronización con el origen de datos"

**Colores de badge por familia de motor:**
| Familia | Color | Motores |
|---------|-------|---------|
| Relacional open-source | Verde (`bg-green-900 text-green-200`) | PostgreSQL, MySQL, MariaDB, SQLite, Percona |
| Relacional comercial | Naranja (`bg-orange-900 text-orange-200`) | Oracle, SQL Server, DB2, Sybase |
| NoSQL documental | Amarillo (`bg-yellow-900 text-yellow-200`) | MongoDB, CouchDB, Couchbase, Firestore |
| NoSQL clave-valor | Rojo (`bg-red-900 text-red-200`) | Redis, Memcached, DynamoDB |
| NoSQL columnar | Cyan (`bg-cyan-900 text-cyan-200`) | Cassandra, HBase, ScyllaDB, ClickHouse |
| NoSQL grafo | Púrpura (`bg-purple-900 text-purple-200`) | Neo4j, ArangoDB |
| Búsqueda / analítica | Índigo (`bg-indigo-900 text-indigo-200`) | Elasticsearch, OpenSearch, Solr |
| Cloud managed | Azul claro (`bg-sky-900 text-sky-200`) | Aurora, Azure SQL, Cloud Spanner, Neon |
| Warehouse / OLAP | Azul (`bg-blue-900 text-blue-200`) | Snowflake, Redshift, Databricks |
| Time-series | Teal (`bg-teal-900 text-teal-200`) | InfluxDB, TimescaleDB, Prometheus |
| Other | Gris (`bg-gray-700 text-gray-300`) | other |

#### Scenario: Detalle de cluster Oracle RAC
- **GIVEN** un activo Oracle con db_is_cluster=true, db_vip="10.0.1.50", db_cluster="RAC-ORACLE", 2 nodos (primary + standby)
- **WHEN** el usuario accede a la página de detalle
- **THEN** ve la sección "Infraestructura" con badge "Cluster HA", VIP "10.0.1.50", nombre "RAC-ORACLE" y tabla de nodos con sus roles

#### Scenario: Detalle de PostgreSQL standalone con servidor host
- **GIVEN** un activo PostgreSQL standalone con db_host_asset_id apuntando a "srv-db-01"
- **WHEN** el usuario accede al detalle
- **THEN** ve "Servidor host: srv-db-01" como enlace clickable y badge "Standalone"

#### Scenario: VIP oculta en standalone
- **GIVEN** un activo con db_is_cluster=false
- **WHEN** se visualiza la sección de infraestructura
- **THEN** el campo VIP no aparece

#### Scenario: Esquemas con término correcto por motor
- **GIVEN** un activo de tipo MongoDB
- **WHEN** se visualiza la sección de esquemas
- **THEN** la cabecera muestra "Colecciones" en lugar de "Tablas"

#### Scenario: Enlace nodo cluster a su activo servidor
- **GIVEN** un nodo del cluster con asset_id="uuid-servidor-02"
- **WHEN** se muestra la tabla de nodos
- **THEN** el campo Asset es un enlace que navega al detalle del servidor "srv-db-02"

#### Scenario: Badge de motor PostgreSQL (relacional open-source)
- **GIVEN** un activo con db_engine="postgresql"
- **WHEN** se visualiza el campo Motor en el detalle
- **THEN** aparece badge verde con texto "PostgreSQL"

#### Scenario: Badge de motor Oracle (relacional comercial)
- **GIVEN** un activo con db_engine="oracle"
- **WHEN** se visualiza el campo Motor
- **THEN** aparece badge naranja con texto "Oracle"

#### Scenario: Badge de motor MongoDB (NoSQL documental)
- **GIVEN** un activo con db_engine="mongodb"
- **WHEN** se visualiza el campo Motor
- **THEN** aparece badge amarillo con texto "MongoDB"

### Requirement: Filtro por click en etiqueta — selección múltiple
Al hacer click en una etiqueta de la tabla SHALL activarse un filtro acumulativo por etiquetas. Se pueden seleccionar múltiples etiquetas simultáneamente. La lógica de filtrado es **AND**: solo se muestran activos que tengan **todas** las etiquetas seleccionadas.

Comportamiento:
- **Primer click** en una etiqueta → se añade al filtro activo; la etiqueta se resalta con `ring-2 ring-primary`.
- **Segundo click** en la misma etiqueta → se elimina del filtro activo; vuelve a su aspecto normal.
- Las etiquetas seleccionadas aparecen como chips con ✕ individual en la barra de filtros, encima o debajo de los otros filtros.
- Un botón "Limpiar etiquetas" o ✕ global elimina todos los filtros de etiqueta a la vez.
- La lógica AND significa: si el usuario filtra por "Producción" y "Cisco", solo se muestran activos que tengan ambas etiquetas.

La barra de filtros activos SHALL mostrar las etiquetas seleccionadas de forma clara, con el mismo color de la etiqueta, para que el usuario entienda qué filtros están aplicados. Ejemplo: `Etiquetas activas: [Producción ✕] [Cisco ✕]  [Limpiar todo]`.

La URL (query params) SHALL reflejar las etiquetas activas para permitir copiar y compartir el enlace. Parámetro: `tag_ids=id1,id2`.

#### Scenario: Filtrar por una etiqueta
- **GIVEN** activos con etiquetas en la tabla
- **WHEN** el usuario hace click en "Producción"
- **THEN** la tabla filtra y muestra solo activos con la etiqueta "Producción"; la etiqueta se resalta con ring y aparece como chip en la barra de filtros

#### Scenario: Añadir segunda etiqueta al filtro (AND)
- **GIVEN** el filtro "Producción" ya está activo
- **WHEN** el usuario hace click en "Cisco"
- **THEN** la tabla muestra solo activos que tengan AMBAS etiquetas "Producción" y "Cisco"

#### Scenario: Eliminar una etiqueta del filtro múltiple
- **GIVEN** filtros activos "Producción" y "Cisco"
- **WHEN** el usuario hace click en el ✕ del chip "Cisco" o en la propia etiqueta "Cisco" en la tabla
- **THEN** solo queda activo el filtro "Producción"; la tabla se actualiza

#### Scenario: Limpiar todos los filtros de etiqueta
- **GIVEN** dos o más etiquetas filtradas
- **WHEN** el usuario pulsa "Limpiar todo" o el ✕ global de etiquetas
- **THEN** todos los filtros de etiqueta se eliminan y la tabla muestra los activos sin ese filtro

### Requirement: Selector de fecha y hora para historificación
Input `datetime-local` para seleccionar fecha y hora exacta. Botón "🟢 Volver a Live" para cancelar. Header muestra modo activo (verde=Live, ámbar=Histórico con fecha).

#### Scenario: Consulta histórica
- **GIVEN** un usuario selecciona fecha y hora
- **THEN** la tabla muestra el inventario en ese instante

### Requirement: Perfil en header superior derecho
Avatar + nombre de usuario (text-base, font-semibold) + rol (text-xs) en la esquina superior derecha, visible en todas las páginas autenticadas. El nombre que se muestra SHALL ser el `preferred_username` extraído del JWT (nunca un placeholder, interrogación u otro texto por defecto). Si el JWT aún no está disponible durante la carga inicial, el header muestra un skeleton/spinner en lugar del nombre. En modo SKIP_AUTH (desarrollo), muestra el username del usuario simulado.

#### Scenario: Username real en header
- **GIVEN** un usuario autenticado con preferred_username="jgarcia"
- **WHEN** accede a cualquier página de la aplicación
- **THEN** el header muestra "jgarcia" como nombre, no "?" ni ningún placeholder

#### Scenario: Sin estado de carga visible con "?"
- **GIVEN** la aplicación está cargando el perfil del usuario
- **WHEN** el JWT aún no ha sido procesado
- **THEN** el header muestra un skeleton animado, no el carácter "?"

### Requirement: Color de etiquetas de sistema coherente con estado de compliance (cuadriestad)
Las etiquetas de sistema que correspondan a un indicador de compliance SHALL mostrar **exactamente el mismo color** que el badge de compliance correspondiente en la columna Compliance. El color es dinámico y se calcula en tiempo de render usando el mismo estado del activo.

**Regla**: el color de la etiqueta = color del badge de compliance para ese indicador en ese activo:
- Badge **verde** → etiqueta en **verde** (`bg-green-900/60 text-green-300 border-green-700`)
- Badge **azul-verde** (gradiente) → etiqueta con **gradiente** diagonal idéntico
- Badge **rojo-azul** (gradiente) → etiqueta con **gradiente rojo-azul** idéntico — KO con excepción (permanente o temporal)

- Badge **rojo** → etiqueta en **rojo** (`bg-red-900/60 text-red-300 border-red-700`)

**Esto es lo que se ve en la captura y está MAL**: "Monitored" aparece en azul fijo aunque MON está verde — eso es porque la etiqueta usa un color fijo en lugar del color calculado del badge. La implementación correcta recalcula el color en cada render igual que lo hace el badge.

**Mapeo etiqueta → indicador de compliance:**
| Nombre de etiqueta | Indicador | Lógica de color |
|-------------------|-----------|-----------------|
| `EDR Active` / `EDR Missing` | `edr` | Color del badge EDR del activo |
| `Monitored` / `No Monitoring` | `mon` | Color del badge MON del activo |
| `SIEM Active` / `SIEM Missing` | `siem` | Color del badge SIEM del activo |
| `Logs Active` / `Logs Missing` | `logs` | Color del badge LOGS del activo |
| `Backup Local OK` / `Backup Local Missing` | `bck` | Color del badge BCK del activo |
| `Backup Cloud OK` / `Backup Cloud Missing` | `bckcl` | Color del badge BCKCL del activo |

Las etiquetas que NO corresponden a compliance mantienen su `color_code` fijo definido en la tabla de tags (vendor: "Cisco", "VMware", "Dell"; tipo: "Virtual", "Physical", "Switch", "Router", "AP"; etiquetas manuales de usuario).

**Implementación**: el componente `TagBadge` SHALL recibir una prop opcional `complianceColor` (string de clase CSS o null). Si se pasa, usa ese color en lugar del `color_code` de la etiqueta. La lógica de cálculo del `complianceColor` vive en el componente padre (la fila de inventario), que ya tiene acceso al estado de compliance y excepciones del activo.

#### Scenario: "Monitored" verde cuando MON está verde (CASO CRÍTICO)
- **GIVEN** un activo con monitored=true (badge MON verde) y etiqueta "Monitored"
- **WHEN** se renderiza la fila en el inventario
- **THEN** la etiqueta "Monitored" aparece en **verde**, idéntico al badge MON. NO en azul fijo.

#### Scenario: "EDR Missing" rojo-azul cuando hay excepción (permanente o temporal)
- **GIVEN** un switch con edr_installed=false y excepción activa para "edr"
- **WHEN** se muestra la etiqueta "EDR Missing"
- **THEN** la etiqueta aparece con **gradiente rojo-azul** (igual que el badge EDR)

#### Scenario: "SIEM Missing" rojo sin excepción
- **GIVEN** un activo con siem_enabled=false y sin excepción para "siem" (badge SIEM rojo)
- **WHEN** se muestra la etiqueta "SIEM Missing"
- **THEN** la etiqueta aparece en **rojo** (igual que el badge SIEM)

#### Scenario: "Backup Local Missing" con excepción que ya no aplica (azul-verde)
- **GIVEN** un activo con last_backup_local no nulo (origen OK) Y excepción activa para "bck" (badge BCK azul-verde)
- **WHEN** se muestra la etiqueta "Backup Local OK"
- **THEN** la etiqueta muestra el mismo gradiente azul-verde que el badge BCK

#### Scenario: "Cisco" mantiene color fijo
- **GIVEN** cualquier activo con etiqueta manual/vendor "Cisco"
- **WHEN** se muestra en la columna de etiquetas
- **THEN** "Cisco" usa su `color_code` fijo, sin depender del compliance

---

### Requirement: Columna "Origen" en la tabla de inventario
La tabla de inventario SHALL incluir una columna **"Origen"** que muestre la fuente de datos de la que procede el activo. Es una columna de solo lectura, no ordenable, posicionada entre "Fabricante" y "Compliance".

El valor mostrado es el campo `source` del activo. El campo `source` es un string libre ingresado durante la ingesta, pero SHALL mostrarse con un **badge con icono y color** según el tipo de origen detectado. La detección es por coincidencia de substrings (case-insensitive):

| Origen detectado | Badge | Color |
|-----------------|-------|-------|
| `vmware` / `vcenter` | 🖥 VMware | `bg-indigo-900/60 text-indigo-300` |
| `veeam` | 💾 Veeam | `bg-blue-900/60 text-blue-300` |
| `crowdstrike` / `cs` / `edr` | 🛡 CrowdStrike | `bg-orange-900/60 text-orange-300` |
| `sentinelone` / `s1` | 🛡 SentinelOne | `bg-purple-900/60 text-purple-300` |
| `zabbix` | 📊 Zabbix | `bg-red-900/60 text-red-300` |
| `nagios` | 📊 Nagios | `bg-yellow-900/60 text-yellow-300` |
| `ansible` | ⚙ Ansible | `bg-red-900/60 text-red-200` |
| `monica` / `asset` / `inventario` | 📋 Inventario | `bg-teal-900/60 text-teal-300` |
| `api` / `rest` | 🔌 API | `bg-cyan-900/60 text-cyan-300` |
| `script` / `cron` / `manual` | 🔧 Script/Manual | `bg-gray-700/60 text-gray-300` |
| `syslog` / `siem` | 📡 Syslog | `bg-violet-900/60 text-violet-300` |
| Cualquier otro valor | texto plano | `bg-gray-800/60 text-gray-400` |
| Null / vacío | `—` | gris claro |

Si el valor exacto no coincide con ningún patrón pero no está vacío, se muestra el valor tal cual en gris con un icono genérico 📦.

El tooltip al hacer hover sobre el badge SHALL mostrar el valor exacto del campo `source` del activo.

El campo `source` también es ordenable: añadirlo a `SORT_FIELDS` del backend y a la lista de columnas ordenables de la tabla.

#### Scenario: Activo de VMware muestra badge VMware
- **GIVEN** un activo con source="VMware vCenter"
- **WHEN** se visualiza en la tabla
- **THEN** la columna Origen muestra badge índigo con texto "VMware" e icono 🖥

#### Scenario: Activo de Ansible muestra badge Script/Ansible
- **GIVEN** un activo con source="ansible-playbook-inventario"
- **WHEN** se visualiza en la tabla
- **THEN** la columna Origen muestra badge rojo oscuro con texto "Ansible" e icono ⚙

#### Scenario: Source desconocido muestra valor literal
- **GIVEN** un activo con source="CustomScript_v2"
- **WHEN** se visualiza en la tabla
- **THEN** la columna Origen muestra "CustomScript_v2" en gris con icono genérico y tooltip con el valor completo

#### Scenario: Source vacío muestra guión
- **GIVEN** un activo con source=null
- **WHEN** se visualiza en la tabla
- **THEN** la columna Origen muestra "—"
