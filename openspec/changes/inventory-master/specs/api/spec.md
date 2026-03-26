# API Spec — Inventory Master

## GET /v1/assets

Lista paginada de activos con tags y excepciones activas enriquecidas.

### Query parameters

| Param | Tipo | Descripción |
|-------|------|-------------|
| search | string | Busca en: name, ips, vendor, source, os, model, serial_number |
| type | string | Filtra por AssetType |
| data_source_id | string | Filtra por fuente de datos |
| as_of | ISO datetime | Consulta histórica desde AssetHistory |
| sort_by | string | name, vendor, type, source, last_backup_local, last_backup_cloud, last_sync |
| sort_order | asc/desc | Default: asc |
| page | int | Default: 1 |
| page_size | int | Default: 20 |

### Ordenación especial (backup y sync)
- `ASC` → `NULLS FIRST` (activos sin backup aparecen primero — estado peor visible arriba)
- `DESC` → `NULLS LAST` (más recientes primero, sin dato al final)
- Campos texto → `func.lower()` para ordenación case-insensitive

### Respuesta
```json
{
  "data": [<Asset.to_dict()>],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

### Asset.to_dict() — campos incluidos siempre
id, name, type, ips, mac_address, vendor, source, data_source_id,
edr_installed, monitored, siem_enabled, logs_enabled, monica_registered,
last_backup_local, last_backup_cloud, last_sync,
ram_gb, total_disk_gb, cpu_count, os,
model, port_count, firmware_version, max_speed, coverage_area, connected_clients,
db_engine, db_version, db_size_gb, db_host, db_port, db_replication, db_cluster,
db_is_cluster, db_vip, db_host_asset_id, db_host_display,
product_name, product_version,
vcenter_id, vcenter_name, hypervisor_id, hypervisor_name, vcenter_datacenter, vcenter_cluster,
vm_guest_os, vm_tools_version, vm_cpu_reserved_mhz, vm_memory_reserved_mb,
vm_datastore, vm_folder, vm_power_state,
backup_job_name, backup_last_status, backup_restore_points,
**edr_endpoint_id** (UUID del endpoint en Sophos Central),
**edr_health** (good/suspicious/bad/unknown),
**edr_last_seen** (ISO datetime — último contacto con Sophos),
**edr_tamper_protected** (bool),
**detected_services** (JSON: {web_servers:[…], databases:[…], web_ports:[…], db_ports:[…]}),
serial_number, location, cell_id, description, purchase_date, warranty_expiry,
**created_by** (string|null — usuario que dio de alta; solo para source='manual'),
created_at, updated_at, tags[], exceptions[]

### Asset.to_dict(detail=True) — campos adicionales solo en detalle
db_schemas, db_users, db_connections_max, db_connections_active,
db_encoding, db_timezone, db_ha_mode, db_ssl_enabled, db_audit_enabled,
db_last_vacuum, db_notes, db_cluster_nodes

---

## GET /v1/assets/{id}
Devuelve Asset.to_dict(detail=True).

---

## POST /v1/assets/ingest
Requiere **admin**. Bulk upsert por `id` o `mac_address`. Body: array de assets.
Si `source='manual'`, rellena automáticamente `created_by` con el `preferred_username` del token JWT.
Si `source='manual'`, valida unicidad de nombre (409) e IPs (409) antes de crear.

### Campos aceptados (IngestAssetRequest) — resumen por integración
| Campo | Fuente | Descripción |
|-------|--------|-------------|
| `vcenter_id`, `hypervisor_id` | VMware | FKs a otros assets |
| `vm_power_state`, `vm_guest_os`, `vm_tools_version` | VMware | Estado de VM |
| `vm_datastore`, `vm_folder`, `vm_cpu_reserved_mhz`, `vm_memory_reserved_mb` | VMware | Config VM |
| `backup_job_name`, `backup_last_status`, `backup_restore_points` | Veeam | Estado backup |
| `edr_endpoint_id`, `edr_health`, `edr_last_seen`, `edr_tamper_protected` | Sophos | Estado EDR |
| `detected_services` | Sophos Live Discover | Servicios detectados (JSON) |

---

## DELETE /v1/assets/{id}
Requiere **editor**. Elimina un asset **solo si** `source='manual'`.
Devuelve `403` si el asset no es manual. Registra en audit_log con `ActivityType.DELETE`.

```json
// Respuesta 200
{ "ok": true, "deleted": "<asset_id>" }

// Respuesta 403
{ "detail": "Solo se pueden eliminar activos dados de alta manualmente" }
```

---

## POST /v1/assets/bulk-tags
Requiere editor.
```json
{"asset_ids": ["uuid1", "uuid2"], "tag_ids": ["tag-uuid1"]}
```

---

## GET /v1/assets/history/snapshots
Lista de timestamps disponibles para consulta histórica.

---

## GET /v1/assets/{id}/impact
Devuelve servicios y aplicaciones que dependen de este asset.
