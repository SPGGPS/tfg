# Frontend - Dashboard de inventario

## ADDED Requirements

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
- Motor (db_engine) con badge visual diferenciado por familia (relacional/NoSQL/búsqueda/cloud)
- Versión (db_version)
- Host y Puerto
- Tamaño total (db_size_gb en GB)
- Replicación activa (badge verde/rojo)
- Cluster / Grupo de disponibilidad
- Modo HA (db_ha_mode: primary / replica / standby / none)
- SSL/TLS obligatorio (badge verde/rojo)
- Auditoría del motor activa (badge verde/rojo)
- Codificación (db_encoding)
- Zona horaria (db_timezone)
- Último mantenimiento/vacuum (db_last_vacuum)
- Conexiones máximas / activas
- Notas del administrador (db_notes)

**Sección "Esquemas / Bases de datos alojadas" (tabla):**
- Columnas: Nombre, Tamaño (GB), Nº tablas, Propietario
- Si db_schemas está vacío o null, muestra "Sin datos de esquemas — requiere sincronización con el origen"

**Sección "Usuarios y roles" (tabla):**
- Columnas: Usuario, Rol, Último acceso
- Badges por rol: dba (rojo), read_write (naranja), read_only (gris), backup (azul), monitoring (teal)
- Si db_users está vacío, muestra "Sin datos de usuarios — requiere sincronización con el origen"

#### Scenario: Detalle de base de datos con esquemas
- **GIVEN** un activo PostgreSQL con db_schemas=[{name:"app_prod",size_gb:45.2,table_count:312,owner:"app_user"}]
- **WHEN** el usuario accede a la página de detalle
- **THEN** ve la sección "Esquemas" con una fila: app_prod / 45.2 GB / 312 tablas / app_user

#### Scenario: Detalle de base de datos con usuarios
- **GIVEN** un activo con db_users=[{username:"app_user",role:"read_write",last_login:"2026-03-15T08:00:00Z"}]
- **WHEN** el usuario accede al detalle
- **THEN** ve la sección "Usuarios" con badge naranja "read_write" y la fecha del último acceso

#### Scenario: Motor mostrado con badge por familia
- **GIVEN** un activo con db_engine="oracle"
- **WHEN** se visualiza el campo Motor en el detalle
- **THEN** aparece el badge "Oracle" en color naranja (familia relacional comercial)
- **GIVEN** un activo con db_engine="mongodb"
- **WHEN** se visualiza el campo Motor
- **THEN** aparece el badge "MongoDB" en color verde (familia NoSQL documental)

### Requirement: Filtro por click en etiqueta
Al hacer click en una etiqueta de la tabla SHALL activarse un filtro por esa etiqueta. La etiqueta activa se resalta con `ring-2`. Segundo click o botón ✕ elimina el filtro.

#### Scenario: Activar filtro por etiqueta
- **GIVEN** activos con etiquetas en la tabla
- **WHEN** el usuario hace click en una etiqueta
- **THEN** la tabla filtra por esa etiqueta y aparece un indicador del filtro activo

#### Scenario: Desactivar filtro
- **GIVEN** filtro de etiqueta activo
- **WHEN** click de nuevo en la etiqueta o ✕
- **THEN** filtro eliminado, se muestran todos los activos

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

### Requirement: Color de etiquetas de sistema coherente con estado de compliance
Las etiquetas de sistema que correspondan a un indicador de compliance (EDR, MON, SIEM, BCK, BCKCL) SHALL mostrar el mismo color que el badge de compliance correspondiente del activo al que están asignadas, no un color fijo. La coherencia visual es: si el badge está verde, la etiqueta aparece en verde; si está rojo, en rojo; si hay excepción activa (badge azul), la etiqueta aparece en azul.

Las etiquetas de sistema que NO corresponden a un indicador de compliance (tipo: "Virtual", "Physical", "Switch", "Router", "Access Point"; vendor: "Cisco", "VMware", "Dell", etc.) mantienen su color fijo de sistema (neutro).

Mapeo etiqueta → indicador de compliance:
- "EDR Active" / "EDR Missing" → indicador `edr` → color según estado EDR del activo
- "Monitored" / "No Monitoring" → indicador `mon` → color según estado MON del activo
- "SIEM Active" / "SIEM Missing" → indicador `siem` → color según estado SIEM del activo
- "Backup Local OK" / "Backup Local Missing" → indicador `bck` → color según estado BCK del activo
- "Backup Cloud OK" / "Backup Cloud Missing" → indicador `bckcl` → color según estado BCKCL del activo

El componente que renderiza las etiquetas en la fila del inventario SHALL recibir tanto la etiqueta como el estado de compliance y las excepciones activas del activo para calcular el color dinámicamente.

#### Scenario: Etiqueta "EDR Active" en activo con excepción EDR
- **GIVEN** un switch con edr_installed=false y excepción activa para "edr"
- **WHEN** se muestra la etiqueta de sistema "EDR Missing" en la columna de etiquetas
- **THEN** la etiqueta "EDR Missing" aparece en azul (igual que el badge EDR del compliance)

#### Scenario: Etiqueta "Monitored" en activo sin excepción
- **GIVEN** un activo con monitored=true
- **WHEN** se muestra la etiqueta "Monitored" en la columna de etiquetas
- **THEN** la etiqueta aparece en verde (igual que el badge MON del compliance)

#### Scenario: Etiqueta "Cisco" mantiene color fijo
- **GIVEN** cualquier activo con etiqueta "Cisco"
- **WHEN** se muestra en la columna de etiquetas
- **THEN** "Cisco" mantiene su color azul fijo de vendor sin depender del compliance
