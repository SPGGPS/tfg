# Backend Spec — Inventory Master

## Modelo Asset (models/asset.py)

```python
class AssetType(str, enum.Enum):
    server_physical = "server_physical"
    server_virtual  = "server_virtual"
    switch          = "switch"
    router          = "router"
    ap              = "ap"
    database        = "database"
```

Tabla: `assets`. PK: UUID string. Todos los enums serializados como string plano en to_dict().

## Regla crítica de serialización
```python
# SIEMPRE así para enums:
"type": str(self.type).split(".")[-1] if self.type else None
# NUNCA:
"type": self.type  # devuelve "AssetType.server_physical" — INCORRECTO
```

## to_dict(detail=False)
- Sin detail: devuelve todos los campos base + db_* de resumen + tags + exceptions activas
- Con detail=True: añade db_schemas, db_users, db_connections_*, db_encoding, etc.

## active_exceptions()
```python
def active_exceptions(self):
    now = datetime.now(timezone.utc)
    return [e for e in self.exceptions
            if e.revoked_at is None and (e.expires_at is None or e.expires_at > now)]
```

## tagging_service.py — etiquetas automáticas
Se ejecuta al ingestar. Asigna etiquetas según type y vendor:
- type=server_virtual + source contiene "vmware" → "Virtual", "VMware"
- type=server_physical → "Physical"
- vendor contiene "cisco" → "Cisco"
- vendor contiene "hp" o "hewlett" → "HP"
- vendor contiene "dell" → "Dell"
- type=switch → "Switch"
- type=router → "Router"
- type=ap → "Access Point"
- type=database → "Database"
- monitored=True → "Monitored", monitored=False → "No Monitoring"
- edr_installed=True → "EDR Active", False → "EDR Missing"
- siem_enabled=True → "SIEM Active", False → "SIEM Missing"
- last_backup_local reciente → "Backup Local OK", None → "Backup Local Missing"
- last_backup_cloud reciente → "Backup Cloud OK", None → "Backup Cloud Missing"

## Router assets.py

GET /v1/assets:
- Filtro search: ilike sobre name, vendor, source, os, model + contains sobre ips (JSON)
- Ordenación: usar SQLAlchemy asc()/desc() + nullsfirst()/nullslast() según campo y dirección
- Paginación: offset + limit + count total

Requiere: nada (viewer puede acceder)
Requiere editor: POST /v1/assets/ingest, POST /v1/assets/bulk-tags
