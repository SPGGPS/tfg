# Backend Spec — Dashboard

## routers/dashboard.py

```python
@router.get("/v1/dashboard")
def get_dashboard(db: Session = Depends(get_db), user=Depends(require_viewer)):
    assets = db.query(Asset).all()
    certs  = db.query(Certificate).all()
    exceptions_active = [e for e in db.query(ComplianceException).all() if e.is_active]

    return {
        "kpis": _kpis(assets, certs, exceptions_active),
        "eol_by_type": _eol_by_type(assets),
        "compliance": _compliance(assets, exceptions_active),
        "backup": _backup(assets),
        "certificates": _certificates(certs),
    }
```

### _eol_by_type(assets)
Para cada AssetType:
  - Filtrar assets de ese tipo
  - Para cada asset buscar si tiene tag "EOL KO", "EOL WARN" o "EOL OK"
  - Segmentar por status

### _compliance(assets, exceptions_active)
Para cada indicador en [edr, mon, siem, logs, bck, bckcl]:
  - Construir excMap: {asset_id: {indicator: exception}}
  - Para cada asset: determinar getComplianceState equivalente en Python
  - Segmentar en ok / ko_with_exception / ko

```python
def _get_state(asset, indicator, exc_map):
    ok_map = {
        "edr": asset.edr_installed,
        "mon": asset.monitored,
        "siem": asset.siem_enabled,
        "logs": asset.logs_enabled,
        "bck": bool(asset.last_backup_local),
        "bckcl": bool(asset.last_backup_cloud),
    }
    is_ok = ok_map.get(indicator, False)
    has_exc = any(e.indicator.value == indicator for e in exc_map.get(asset.id, []))
    if is_ok and has_exc: return "ok_with_exception"
    if is_ok:             return "ok"
    if has_exc:           return "ko_with_exception"
    return "ko"
```

### _backup(assets)
Separar en last_backup_local y last_backup_cloud.
Estado: ok si fecha existe, missing si None.

### _certificates(certs)
Reusar cert_status calculado del modelo Certificate.

## Registro en main.py
```python
from app.routers.dashboard import router as dashboard_router
app.include_router(dashboard_router)
```
