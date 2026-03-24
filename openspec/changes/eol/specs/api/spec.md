# API Spec — End of Life

## GET /v1/eol/all-products
Sin BD. Proxy a https://endoflife.date/api/all.json.
Devuelve: array de strings (slugs), ej: ["ubuntu","python","rhel",...]

## GET /v1/eol/products
Lista productos guardados en BD con contadores.
```json
[{
  "id": "uuid", "product_id": "ubuntu", "display_name": "Ubuntu",
  "category": "OS", "notes": null,
  "sync_status": "synced", "last_synced_at": "2026-03-22T03:00:00Z",
  "cycle_count": 6, "eol_count": 2, "warning_count": 1
}]
```

## POST /v1/eol/products/{product_id}
Requiere admin. Añade producto y hace primera sync.
Body (opcional): `{"display_name": "Ubuntu Linux", "category": "OS", "notes": "..."}`
Respuesta: `{"product": {...}, "sync": {"created": 6, "updated": 0, "unsynced": 0}}`
Error 409 si ya existe.

## PUT /v1/eol/products/{product_id}
Requiere admin. Edita display_name, category, notes (valores custom del ayuntamiento).

## DELETE /v1/eol/products/{product_id}
Requiere admin. Borra producto y TODOS sus ciclos. Irreversible.

## POST /v1/eol/products/{product_id}/sync
Requiere admin. Sync manual. Respuesta con stats: created/updated/unsynced.

## POST /v1/eol/sync-all
Requiere admin. Sync todos los productos. Usado por el CronJob diario.

## GET /v1/eol/products/{product_id}/cycles
```json
{
  "product": {<EolProduct.to_dict()>},
  "cycles": [{
    "id": "uuid", "product_id": "ubuntu", "cycle": "22.04",
    "release_date": "2022-04-21", "eol_date": "2027-04-21",
    "eol_boolean": null, "support_end": null,
    "lts": true, "latest": "22.04.5", "link": null,
    "custom_eol_date": null, "custom_notes": null,
    "effective_eol_date": "2027-04-21",
    "eol_status": "ok",
    "sync_status": "synced", "last_synced_at": "..."
  }]
}
```

## PUT /v1/eol/products/{product_id}/cycles/{cycle_id}
Requiere admin. Edita solo custom_eol_date y custom_notes.
`custom_eol_date` null → usar la fecha de endoflife.date.

## GET /v1/eol/asset-status
Cruza activos × ciclos EOL. Busca por OS y db_engine.
```json
[{"asset_id":"...", "asset_name":"ubuntu-prod-01", "matches":[
  {"product_id":"ubuntu","cycle":"22.04","eol_status":"ok","effective_eol_date":"2027-04-21"}
]}]
```

## API externa — endoflife.date
```
GET https://endoflife.date/api/all.json
→ ["ubuntu","python","rhel","postgresql",...]

GET https://endoflife.date/api/{product}.json
→ [{"cycle":"22.04","eol":"2027-04-21","lts":true,"latest":"22.04.5","releaseDate":"2022-04-21"}, ...]
```
El campo `eol` puede ser: fecha ISO string, `true` (ya EOL) o `false` (sin fecha de EOL).
