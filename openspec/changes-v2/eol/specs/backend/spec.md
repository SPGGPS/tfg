# Backend Spec — End of Life

## models/eol.py

```python
class EolSyncStatus(str, enum.Enum):
    synced   = "synced"    # presente en la última sync
    unsynced = "unsynced"  # desapareció de endoflife.date (no borrar)

class EolProduct(Base):
    __tablename__ = "eol_products"
    id, product_id(unique index), display_name, category, notes
    sync_status(EolSyncStatus), last_synced_at, created_at, updated_at

class EolCycle(Base):
    __tablename__ = "eol_cycles"
    __table_args__ = (Index("ix_eol_cycles_product_cycle", "product_id", "cycle"),)
    id, product_id(index), cycle
    release_date, eol_date, eol_boolean, support_end, lts, latest, link
    custom_eol_date, custom_notes   ← valores admin (sobrescriben API)
    sync_status, last_synced_at, raw_data(JSON)
```

## Propiedades calculadas de EolCycle

```python
@property
def effective_eol_date(self):
    return self.custom_eol_date or self.eol_date

@property
def eol_status(self) -> str:
    if self.eol_boolean is True: return "eol"
    d = self.effective_eol_date
    if not d: return "unknown"
    days = (d - date.today()).days
    if days <= 0:   return "eol"
    if days <= 365: return "warning"   # ≤ 1 año
    if days <= 730: return "warning"   # ≤ 2 años
    return "ok"                        # > 2 años
```

## _sync_product(db, product_id) — lógica crítica

1. GET https://endoflife.date/api/{product_id}.json
2. Por cada ciclo: upsert por (product_id, cycle) — crear o actualizar
3. Ciclos locales NO en la respuesta → sync_status = unsynced (NO borrar)
4. Actualizar EolProduct.sync_status = synced, last_synced_at = now
5. Commit

## Parseo del campo "eol" de la API
```python
eol_raw = item.get("eol")
if isinstance(eol_raw, bool):
    eol_bool = eol_raw    # true = ya EOL, false = sin fecha
elif isinstance(eol_raw, str):
    eol_date = date.fromisoformat(eol_raw)
```

## apply_eol_tags(db, asset) — tagging_service.py

Mapeos de búsqueda:
- asset.os → ubuntu/debian/rhel/centos/windows-server/rocky-linux/almalinux/amazon-linux
- asset.db_engine → postgresql/mssqlserver/mysql/mariadb/oracle-db/mongodb/redis

Extracción de versión con regex:
1. Patrón X.Y: `\b(\d+\.\d+)\b` → "22.04", "3.11"
2. Patrón X:   `\b(\d+)\b`        → "9", "8"

Etiquetas de sistema generadas:
| eol_status | Nombre etiqueta | Color |
|-----------|----------------|-------|
| eol       | "EOL"          | #dc2626 (rojo) |
| warning   | "EOL Próximo"  | #d97706 (ámbar) |
| ok        | "EOL OK"       | #16a34a (verde) |

Solo se asigna la etiqueta del peor estado encontrado entre todos los matches.

## Imports obligatorios al inicio del archivo
```python
import httpx, logging, re
from datetime import datetime, date, timezone
from typing import Optional
```
NO repetir imports al final del archivo.

## Integración con inventario

### apply_eol_tags(db, asset) — tagging_service.py
Se llama automáticamente:
1. Desde `_sync_product()` tras cada sync de producto EOL
2. Desde `init_db.py` al cargar el seed
3. Desde `POST /v1/eol/recalculate-tags` (llamada manual)

```python
EOL_TAGS = {
    "eol":     {"name": "EOL KO",  "color_code": "#dc2626"},
    "warning": {"name": "EOL WARN","color_code": "#d97706"},
    "ok":      {"name": "EOL OK",  "color_code": "#16a34a"},
}
```

### SYSTEM_TAGS — dict global (tagging_service.py)
Incluye las etiquetas EOL para que aparezcan en TagsPage sección Sistema:
```python
"EOL KO":   "#dc2626",
"EOL WARN": "#d97706",
"EOL OK":   "#16a34a",
```

---

## Matching EOL mejorado — todos los campos del asset

### Campos utilizados por apply_eol_tags()

| Campo del asset | Producto EOL buscado | Ejemplo |
|----------------|---------------------|---------|
| `os` | ubuntu, debian, rhel, centos, windows-server, amazon-linux, rocky-linux | "Ubuntu 22.04 LTS" → ubuntu + "22.04" |
| `db_engine` + `db_version` | postgresql, mssqlserver, mysql, mariadb, mongodb, redis | "postgresql" + "16.2" → postgresql + "16.2" |
| `vendor` + `firmware_version` | cisco-ios, cisco-ios-xe | vendor="Cisco" fw="16.12.4" → cisco-ios + "16.12" |

### Lógica de versión
1. Intenta match exacto X.Y (ej: "22.04", "16.2")
2. Fallback a major X (ej: "22", "16")
3. Solo busca en productos que existan en `eol_products` BD

### Condición para asignar etiqueta
- Si no existe el producto en BD → no se asigna etiqueta (no hay datos)
- Si existe pero no hay ciclo para esa versión → no se asigna
- Si hay ciclo → asigna EOL KO / EOL WARN / EOL OK según `eol_status`
- Si hay múltiples matches → asigna el peor estado (eol > warning > ok)

### Para que funcione: productos a cargar en EOL
Mínimo recomendado para cubrir el seed de activos:
- ubuntu (web-prod-01, api-vm-prod-01)
- rhel (db-prod-01)
- windows-server (app-vm-staging-01)
- postgresql (postgres-prod-01)
- mssqlserver (sqlserver-erp-01)

---

## Matching real de assets por producto en listado EOL

El endpoint `GET /v1/eol/products` calcula por cada producto cuántos assets
del inventario coinciden por OS o db_engine con ese producto específico:

```python
OS_SLUGS  = {"ubuntu": ["ubuntu"], "rhel": ["rhel","red hat"], ...}
DB_SLUGS  = {"postgresql": ["postgresql","postgres"], "mssqlserver": ["sqlserver",...], ...}

# Para cada asset: ¿coincide con este producto?
# Si coincide: ¿tiene etiqueta EOL KO/WARN/OK?
d["asset_eol_ko"]   = len(matched_with_tag("EOL KO"))
d["asset_eol_warn"] = len(matched_with_tag("EOL WARN"))
d["asset_eol_ok"]   = len(matched_with_tag("EOL OK"))
```

Los IDs de assets afectados también se devuelven (`asset_eol_ko_ids`) para
filtrado desde el modal de assets.
