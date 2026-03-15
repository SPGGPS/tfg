# Frontend - Dashboard de inventario

## ADDED Requirements

### Requirement: Ordenación por columna con iconos ↑↓
El dashboard SHALL mostrar iconos de ordenación (↑↓) en el encabezado de cada columna ordenable (todas excepto Etiquetas). Al hacer click en el encabezado se ordena asc; segundo click desc; tercer click quita la ordenación. No habrá combo ni botón separado para ordenar.

#### Scenario: Ordenar por columna haciendo click en cabecera
- **GIVEN** un usuario en la tabla de activos
- **WHEN** hace click en el encabezado de una columna ordenable
- **THEN** la tabla se ordena por ese campo en ascendente, mostrando ↑ activo; segundo click ordena descendente mostrando ↓ activo

#### Scenario: Columna Etiquetas no es ordenable
- **GIVEN** un usuario en la tabla
- **WHEN** visualiza la columna Etiquetas
- **THEN** no aparece ningún icono de ordenación en esa cabecera

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
- Campos específicos por tipo: ram_gb, total_disk_gb, cpu_count, os (servidores); model, port_count, firmware_version, max_speed (switches/routers); model, coverage_area, connected_clients (APs)
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
El dashboard SHALL incluir un selector de tipo de activo para filtrar la tabla.

#### Scenario: Filtrar por tipo específico
- **GIVEN** un usuario selecciona "switch"
- **WHEN** se aplica el filtro
- **THEN** solo aparecen activos de ese tipo

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
Avatar + nombre (text-base, font-semibold) + rol (text-xs) en la esquina superior derecha, visible en todas las páginas autenticadas.
