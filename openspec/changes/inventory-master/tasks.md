# Tasks: Inventory Master

## 1. Modelos y DB
- [x] 1.1 Modelo Asset polimórfico con AssetType enum (`workstation` añadido en iteración Sophos)
- [x] 1.2 Campos compliance: edr_installed, monitored, siem_enabled, logs_enabled,
           last_backup_local, last_backup_cloud, last_sync
- [x] 1.3 Campos servidor: ram_gb, total_disk_gb, cpu_count, os
- [x] 1.4 Campos red: model, port_count, firmware_version, max_speed, coverage_area
- [x] 1.5 Campos database (resumen): db_engine, db_version, db_size_gb, db_host, db_port,
           db_replication, db_cluster, db_is_cluster, db_vip, db_host_asset_id
- [x] 1.6 Campos database (detalle): db_schemas, db_users, db_connections_max/active,
           db_encoding, db_timezone, db_ha_mode, db_ssl_enabled, db_audit_enabled,
           db_last_vacuum, db_notes, db_cluster_nodes
- [x] 1.7 Campos extendidos: serial_number, location, cell_id FK, description,
           purchase_date, warranty_expiry
- [x] 1.10 Campo `created_by` (String 100, nullable) — nombre del usuario que dio de alta el asset
           manualmente. Solo se rellena cuando source='manual'. Usado en la columna "Última sync".
- [x] 1.8 Modelo AssetHistory: asset_id, snapshot_at (INDEX), snapshot (JSON)
- [x] 1.9 Tabla asset_tag (M:N) con CASCADE

## 2. Backend
- [x] 2.1 GET /v1/assets con paginación, búsqueda, filtros, ordenación
- [x] 2.2 Ordenación NULLS FIRST/LAST para last_backup_local, last_backup_cloud, last_sync
- [x] 2.3 Ordenación case-insensitive con func.lower() para campos texto
- [x] 2.4 GET /v1/assets/{id} con detail=True (incluye campos db_* extendidos)
- [x] 2.5 POST /v1/assets/ingest — bulk upsert por id/mac_address. Al crear con source='manual',
          guarda automáticamente `created_by` con el `preferred_username` del token.
- [x] 2.12 DELETE /v1/assets/{id} — elimina un asset. Solo permite borrar assets con source='manual'.
          Requiere rol editor. Registra en audit_log (ActivityType.DELETE).
- [x] 2.6 POST /v1/assets/bulk-tags — asignación masiva
- [x] 2.7 GET /v1/assets/history/snapshots
- [x] 2.8 Serialización enriquecida: tags + active_exceptions en to_dict()
- [x] 2.9 to_dict() — enums siempre como string plano: str(e).split(".")[-1]
- [x] 2.10 tagging_service.py — auto-tags: Virtual, Physical, Cisco, HP, Dell,
            VMware, Switch, Router, Access Point, Database,
            Monitored, No Monitoring, EDR Active, EDR Missing,
            SIEM Active, SIEM Missing, Backup Local OK/Missing, Backup Cloud OK/Missing
- [x] 2.11 GET /v1/assets/{id}/impact — qué servicios dependen de este asset

## 3. Frontend
- [x] 3.1 Tabla de inventario con filas .table-row-alt + hover + selected
- [x] 3.2 Columnas: Nombre (link a detalle), IPs, Tipo, Vendor, Fuente, Compliance, Backup, Etiquetas
- [x] 3.3 Ordenación por columna con iconos SortIcon ↑↓
- [x] 3.4 Filtros: búsqueda libre, tipo, fuente de datos, as_of (histórico)
- [x] 3.5 Checkboxes + "Asignar etiquetas (N)" → modal con lista de etiquetas
- [x] 3.6 Tabs: Inventario | Certificados 🔒 (ruta /certificates)
- [x] 3.7 Tab activo: border-red-600 text-red-700 font-semibold
- [x] 3.8 AssetDetailPage /assets/:id con todos los campos + historial auditoría
- [x] 3.9 Columna "Ubicación" en tabla mostrando cell.full_path (via Asset._get_cell_full_path())
- [x] 3.10 Filas de inventario clickeables (navigate a /assets/:id al pulsar la fila)
- [x] 3.11 Botón "+ Nuevo activo" (solo editor/admin) → modal con formulario por tipo
- [x] 3.12 Formulario nuevo activo: campos comunes (nombre, tipo, IP, vendor) + campos tipo-específicos
         (server: OS/model/serial; database: motor/versión/host; web_server: software/versión;
          k8s_cluster: proveedor/versión; container: imagen/tag/runtime/estado; red: modelo/firmware)
- [x] 3.13 Validación de IP en tiempo real en el formulario: regex IPv4, error inline rojo, bloqueo al submit
- [x] 3.14 Campos obligatorios por tipo: vendor (todos), IP (servers+red), OS (servers), motor (database),
          software (web_server), proveedor+versión (k8s_cluster), imagen (container)
- [x] 3.15 Botón eliminar (icono papelera) en columna propia al final de la tabla — solo visible en filas
          con source='manual' y rol editor/admin. Pide confirmación antes de borrar.
- [x] 3.16 Columna "Última sync" muestra "✏️ <usuario>" para activos manuales en lugar de fecha de sync
- [x] 3.17 Badge ámbar "MANUAL" junto al nombre en filas de activos con source='manual'
- [x] 3.18 SourceBadge "Manual" → color ámbar con icono ✏️ (antes era gris)

## 4. Infra
- [x] 4.1 CronJob Helm para snapshot horario (AssetHistory) — implementado en Helm Y en APScheduler backend
- [x] 4.2 CronJob Helm para purga de history > 1 año — `purge_old_snapshots()` en history_service.py, llamado desde hourly_snapshot
- [x] 4.3 CronJobs de ingesta desde VMware/Veeam/EDR — implementados en `/Desktop/data-integrations/`
         Scripts Airflow DAGs: `vmware_vcenter_sync` (0 */4), `sophos_edr_sync` (15 */4), `veeam_backup_sync` (30 */4)

### Estado de historificación (AssetHistory)

**Implementado:**
- Modelo `AssetHistory` (asset_id, snapshot_at INDEX, snapshot JSON) en `models/asset.py`
- `history_service.py`: `take_snapshot()`, `get_assets_at()`, `get_available_snapshots()`, `purge_old_snapshots()`
- `GET /v1/assets/history/snapshots` — lista snapshots disponibles
- Vista histórica en InventoryPage: filtro `as_of` que usa `get_assets_at()`
- Retención: 365 días (RETENTION_DAYS en history_service.py)
- **CronJob APScheduler**: `hourly_snapshot()` programado `minute=0` (cada hora en punto, Europe/Madrid) — **añadido en esta iteración**

**Pendiente:**
- 4.3 Ingesta real desde fuentes externas (VMware, Veeam, EDR, Monica)

## 6. Seed de datos completo (init_db.py)

- [x] 6.1 10 assets (2 físicos, 2 virtuales, 2 switches, 1 router, 1 AP, 2 databases)
- [x] 6.2 Todos los assets con cell_id asignado a las cells del seed de localizaciones
- [x] 6.3 5 etiquetas manuales: Producción, Pre-producción, DMZ, Crítico, En migración
- [x] 6.4 Etiquetas asignadas: web-prod-01 y db-prod-01 → Producción+Crítico,
           api-vm-prod-01 → Producción, app-vm-staging-01 → Pre-producción+En migración,
           router-edge-01 → Producción+DMZ, postgres-prod-01 → Producción,
           sqlserver-erp-01 → Producción+Crítico
- [x] 6.5 Auto-tags aplicados a todos los assets via apply_auto_tags()

### Seed actualizado — datos de prueba completos
El seed incluye datos para TODAS las pestañas de la aplicación.
Para ejecutarlo en limpio: `docker compose down -v && docker compose build --no-cache && docker compose up -d`

## 6. Modales de gestión de etiquetas (añadidos)

### Modal "Asignar etiquetas" — rediseñado
- Paso 1: selección de etiquetas con colorBadgeStyle (toggle visual con ✓)
- Paso 2: lista de assets actuales con checkboxes (AssetTypeBadge + nombre + IP)
- Checkbox cabecera "Seleccionar todos (N)"
- Footer con texto resumen y botón "Asignar"

### Modal "Eliminar etiqueta" — nuevo
- Botón "🗑 Eliminar etiqueta" siempre visible para editor/admin
- Paso 1: seleccionar la etiqueta a eliminar (1 sola a la vez)
- Paso 2: lista de assets que TIENEN esa etiqueta (GET /assets?tag_ids=[id])
  con checkboxes — marcar los que PERDERÁN la etiqueta
- Footer con resumen y botón "Eliminar etiqueta" (btn-danger)
- Backend: POST /v1/assets/bulk-untag {asset_ids, tag_ids}

### Backend: POST /v1/assets/bulk-untag
- Mismo body que bulk-tags: {asset_ids: [...], tag_ids: [...]}
- Solo etiquetas manuales (origin=manual) — bloquea system tags
- Requiere editor
- Registra en audit_logs (ActivityType.TAG_ASSIGN)
- Devuelve: {removed_from: N, tags_removed: ["nombre"]}

### Bug corregido: complianceCls declarado dos veces en TagBadge
La refactorización de TagBadge dejó la declaración `let complianceCls = ''`
duplicada, causando error de compilación en esbuild.
Solución: eliminar el bloque duplicado.
```
// ❌ Antes:
let complianceCls = ''
if (asset && excMap) { complianceCls = ... }
let complianceCls = ''   // ERROR: ya declarada
if (asset && excMap) { complianceCls = ... }

// ✅ Después:
let complianceCls = ''
if (asset && excMap) { complianceCls = ... }
```

## 7. Gestión de etiquetas desde Inventario
- [x] 7.1 Botón "+ Asignar etiquetas" siempre visible (no condicional a selected.size)
- [x] 7.2 Modal asignar: Paso 1 elige etiquetas (toggle ✓), Paso 2 lista assets con checkboxes
- [x] 7.3 Botón "🗑 Eliminar etiqueta" siempre visible para editor/admin
- [x] 7.4 Modal eliminar: elige etiqueta → lista assets que la tienen → guarda
- [x] 7.5 POST /v1/assets/bulk-untag — soft remove de etiquetas manuales en assets
- [x] 7.6 TanStack v5: invalidateQueries({queryKey:[...]}) en todas las mutaciones

## 8. Bugs de compilación resueltos
- [x] complianceCls declarado dos veces en TagBadge → esbuild error
- [x] const cmp duplicado en ExceptionsPage sort function
- [x] const e duplicado en ComplianceBadge.getTooltip
- [x] getBadgeClass usaba dark-mode colors → texto invisible en tema claro
- [x] CertificatesPage: TabBar definida dentro de JSX → no disponible antes de su uso

## 9. Seed y reseed

### POST /v1/admin/reseed (admin only)
Fuerza el reseed completo borrando todos los datos y recargando desde init_db.
Útil cuando la BD tiene datos corruptos o incompletos de sesiones anteriores.

```bash
curl -X POST http://localhost:8000/v1/admin/reseed
# → {"ok": true, "message": "Reseed completado. 10 activos en BD."}
```

### seed_if_empty(force=False)
Si force=True borra todos los modelos en orden de FK antes de reseedear.
Orden de borrado: AuditLog → InfraBinding → AppDependency → ServiceComponent
→ ServiceEndpoint → ComplianceException → Asset → Application → Service
→ Certificate → EolCycle → EolProduct → Tag → Cell → Site → Zone → DataSource

## 10. Fix seed robusto

### Condición de seed mejorada
Si hay < 5 assets (BD parcialmente rota o vacía), el seed se ejecuta igualmente
sin esperar que el count sea exactamente 0.

```python
if not force and count >= 5: return  # OK, seed correcto
if not force and 0 < count < 5:
    logger.warning("BD parcial, reseedando...")  # rellenar gaps
```

### Reset limpio (recomendado si el inventario aparece vacío)
```bash
docker compose down -v && docker compose build --no-cache && docker compose up -d
```
O desde Swagger: POST /v1/admin/reseed

## 11. Bug crítico: to_dict() retornaba None (inventario vacío)

### Causa
Al añadir `_get_cell_full_path()` como método, se insertó dentro de `to_dict()`
en lugar de después. El método `to_dict` quedó así:

```python
def to_dict(self):
    d = { ... "cell_full_path": self._get_cell_full_path(), ... }
    # ← FALTABA return d aquí
    
    def _get_cell_full_path(self):  # ← METIDO EN MEDIO
        ...
        return None

    if detail:   # ← código muerto, nunca ejecutado
        ...
    return d     # ← nunca alcanzado
```

`to_dict()` retornaba `None` → `_enrich()` en assets.py fallaba con `NoneType`
→ `GET /v1/assets` → 500 → inventario vacío en el frontend.

### Solución
`_get_cell_full_path` es método propio de la clase, DESPUÉS de `to_dict`:

```python
def to_dict(self, include_exceptions=True, detail=False):
    d = { ... "cell_full_path": self._get_cell_full_path(), ... }
    if detail:
        d.update({...})
    return d          # ← return correcto

def _get_cell_full_path(self):  # ← método separado
    try:
        sess = object_session(self)
        if sess and self.cell_id:
            cell = sess.query(Cell).filter_by(id=self.cell_id).first()
            if cell:
                return cell.to_dict().get("full_path") or cell.name
    except Exception:
        pass
    return None
```

### Verificación
```python
# Línea 145: return d (dentro de to_dict)
# Línea 147: def _get_cell_full_path(self): (método separado)
assert '        return d\n\n    def _get_cell_full_path' in asset_code
```

## 12. CMDB completa — inspirada en ServiceNow (v1.4)

### Nuevos AssetType
```python
vcenter        # VMware vCenter / Hyper-V SCVMM
web_server     # Nginx, Apache, IIS, Tomcat, Caddy
firewall       # FortiGate, PaloAlto, CheckPoint, pfSense...
load_balancer  # HAProxy, F5, NGINX Plus, Citrix...
storage_array  # SAN/NAS: Dell EMC, NetApp, HPE...
```

### Nuevos campos por categoría

#### Producto (todos los tipos)
- `product_name` — nombre completo del producto (ej: "Dell PowerEdge R750")
- `product_version` — versión del producto/firmware unificada

#### Virtualización
- `vcenter_id` / `vcenter_name` — FK al vCenter que gestiona la VM
- `hypervisor_id` / `hypervisor_name` — FK al host ESX/Hyper-V donde corre
- `vcenter_host`, `vcenter_datacenter`, `vcenter_cluster` — para nodos vCenter
- `vm_guest_os`, `vm_tools_version`, `vm_cpu_reserved_mhz`, `vm_memory_reserved_mb`
- `vm_datastore`, `vm_folder`, `vm_power_state`

#### Web server
- `web_server_software` (nginx/apache/iis/tomcat...), `web_server_version`
- `web_server_port`, `web_listen_ips`, `web_virtual_hosts` (JSON)
- `web_ssl_enabled`, `web_config_path`
- `host_asset_id` / `host_asset_name` — FK al servidor donde corre

#### Firewall
- `fw_type`, `fw_policy_count`, `fw_ha_mode`
- `fw_nat_enabled`, `fw_vpn_enabled`, `fw_zones` (JSON)
- `fw_last_rule_change`

#### Load Balancer
- `lb_software`, `lb_algorithm`, `lb_virtual_servers`
- `lb_pool_members` (JSON: [{ip, port, weight, state}])
- `lb_health_check`, `lb_ssl_offload`

#### Storage Array
- `storage_type` (SAN/NAS/iSCSI), `storage_protocol`
- `storage_total_raw_tb`, `storage_usable_tb`
- `storage_raid_level`, `storage_controller`, `storage_shelves`

### Relaciones CMDB (auto-FK en assets table)
```
vcenter         ←─ server_virtual (vcenter_id)
server_physical ←─ server_virtual (hypervisor_id)
server_physical ──→ database      (db_host_asset_id)
server_virtual  ──→ database      (db_host_asset_id)
server_virtual  ──→ web_server    (host_asset_id)
server_physical ──→ web_server    (host_asset_id)
```

### Nuevos endpoints backend
```
GET /v1/cmdb/servers           — físicos + virtuales + vCenters con filtros
GET /v1/cmdb/network           — switches/routers/firewalls/LBs/APs
GET /v1/cmdb/databases         — instancias DB con host
GET /v1/cmdb/web-servers       — web servers con host
GET /v1/cmdb/storage           — arrays SAN/NAS
GET /v1/cmdb/asset-relations/{id} — todas las relaciones CMDB de un asset
```

### Seed con 23 assets reales
| Tipo | Cantidad | Ejemplos |
|------|----------|---------|
| vcenter | 1 | vcenter-prod-01 (VMware 8.0.2) |
| server_physical | 4 | esx-host-01/02 (Dell R750 ESXi), db-bare-01 (HP DL380 RHEL9), srv-backup-01 |
| server_virtual | 5 | vm-web/api/erp/keycloak/staging → con vcenter_id + hypervisor_id |
| switch | 2 | Cisco Catalyst 9300 + 2960 |
| router | 1 | Cisco ASR 1001-X |
| firewall | 1 | FortiGate 200F HA |
| load_balancer | 1 | HAProxy Enterprise |
| ap | 1 | Cisco Aironet 2802I |
| storage_array | 1 | Dell EMC PowerStore 500T (SAN) |
| database | 3 | PostgreSQL 16.2 → db-bare-01 · SQL Server 2022 → vm-erp · PostgreSQL 15.6 → vm-keycloak |
| web_server | 3 | nginx portal → vm-web · nginx API → vm-api · IIS ERP → vm-erp |

### Frontend — nuevas páginas CMDB
- `/cmdb/servers` — ServersPage: tabs Todos/vCenter/Físico/Virtual, columna vCenter/Host/Datastore, modal de relaciones
- `/cmdb/network` — NetworkPage: tabs por tipo, columna de detalles específicos (puertos, políticas, zonas, pool)
- `/cmdb/databases` — DatabasesPage: motor+versión, link al servidor host, barra de conexiones, HA/cluster
- `/cmdb/web-servers` — WebServersPage: software+versión, link al host, virtual hosts, SSL, config path

### Sidebar
Inventario tiene sub-menú desplegable con:
- ▤ Inventario (resumen general — página existente)
  - 🖥 Servidores
  - 🌐 Red
  - 🗄 Bases de Datos
  - 🌍 Servidores Web

### InventoryPage actualizada
Columna "Fabricante" → "Producto / Fabricante": muestra product_name como título,
product_version en subtítulo font-mono, vendor como tercera línea si difiere del producto.

---

## 13. Integraciones de datos externas (`/Desktop/data-integrations/`)

### 13.1 VMware vSphere 8

- [x] 13.1.1 `vmware_extract.py` — pyVmomi: conexión SSL configurable a vCenter
- [x] 13.1.2 Extrae vCenter (type=`vcenter`), ESX hosts (type=`server_physical`), VMs (type=`server_virtual`)
- [x] 13.1.3 IDs estables: `vc-<host>`, `host-<fqdn>`, `vm-<moId>`
- [x] 13.1.4 Mapeo completo: vendor, model, serial, CPU packages, RAM, IPs, OS, firmware,
             datacenter, cluster, vm_power_state, vm_tools_version, vm_datastore, vm_folder
- [x] 13.1.5 Modos `--dry-run` y `--output FILE`
- [x] 13.1.6 DAG Airflow `vmware_vcenter_sync` — `0 */4 * * *`
- [x] 13.1.7 Campos añadidos a `IngestAssetRequest`: vcenter_id, hypervisor_id, vm_power_state,
             vm_guest_os, vm_tools_version, vm_datastore, vm_folder, vm_cpu_reserved_mhz, vm_memory_reserved_mb

### 13.2 Veeam Backup & Replication 13

- [x] 13.2.1 `veeam_extract.ps1` — PowerShell: módulo `Veeam.Backup.PowerShell` + fallback `VeeamPSSnapin`
- [x] 13.2.2 Procesa infrastructure jobs (Backup, BackupCopy, EpAgentBackup) y Veeam Agent Jobs
- [x] 13.2.3 Por VM: `Get-VBRRestorePoint` (fecha, count, tamaño), `Get-VBRBackupSession` (estado, duración)
- [x] 13.2.4 `veeam_push.py` — busca el asset por nombre (GET /v1/assets?search=), actualiza vía ingest
- [x] 13.2.5 Campos backend: `backup_job_name`, `backup_last_status` (Success/Warning/Failed), `backup_restore_points`
- [x] 13.2.6 Auto-migración vía `_auto_migrate()` — sin recrear la BD
- [x] 13.2.7 DAG Airflow `veeam_backup_sync` — `30 */4 * * *` (SSHOperator → PS, PythonOperator → push)

### 13.3 Sophos Central EDR

- [x] 13.3.1 `sophos_extract.py` — OAuth2 Client Credentials → tenant → data region
- [x] 13.3.2 GET `/endpoint/v1/endpoints` paginado → todos los endpoints del tenant
- [x] 13.3.3 Mapeo endpoint → asset: ID estable `sophos-<uuid>`, type=`server_physical`/`workstation`, edr_installed=True
- [x] 13.3.4 Live Discover query 1 — `system_info`: cpu_count, ram_gb
- [x] 13.3.5 Live Discover query 2 — web_server_processes: detecta nginx, apache/httpd, IIS (w3wp.exe), tomcat, caddy
- [x] 13.3.6 Live Discover query 3 — database_processes: detecta postgresql, mysql/mariadb, mssql, oracle, mongodb, redis, elasticsearch
- [x] 13.3.7 Live Discover query 4 — listening_ports: puertos web (80/443/8080/…) y DB (1433/1521/3306/5432/…)
- [x] 13.3.8 Campo `detected_services` JSON: `{web_servers:[…], databases:[…], web_ports:[…], db_ports:[…]}`
- [x] 13.3.9 Rate limit respetado: 7s entre queries (límite Sophos: 10/min, cuota diaria: 1000 queries)
- [x] 13.3.10 Polling con backoff exponencial hasta `status == "finished"` (timeout: 300s)
- [x] 13.3.11 Modos `--dry-run`, `--verbose`, `--output FILE`, `--skip-queries`
- [x] 13.3.12 Nuevo tipo de asset `workstation` en AssetType enum
- [x] 13.3.13 Campos backend nuevos: `edr_endpoint_id`, `edr_health`, `edr_last_seen`, `edr_tamper_protected`, `detected_services`
- [x] 13.3.14 Auto-migración vía `_auto_migrate()` — 5 columnas añadidas sin recrear la BD
- [x] 13.3.15 DAG Airflow `sophos_edr_sync` — `15 */4 * * *` (entre VMware :00 y Veeam :30)
