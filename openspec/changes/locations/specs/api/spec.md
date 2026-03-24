# API Spec — Localizaciones físicas

## GET /v1/locations/tree
Árbol completo Zone → Site → Cell en un solo query.
```json
[{
  "id": "...", "name": "Zona", "site_count": 2,
  "sites": [{
    "id": "...", "name": "Site", "zone_name": "Zona", "cell_count": 3,
    "cells": [{
      "id": "...", "name": "Rack A", "cell_type": "rack",
      "row_id": "Fila A", "rack_unit": "U1-U42",
      "full_path": "Zona › Site › Rack A"
    }]
  }]
}]
```

## CRUD Zones — /v1/zones
- GET /v1/zones → lista de zonas
- POST /v1/zones → crea. Requiere editor. Body: {name, description}
  ⚠️ IntegrityError → HTTP 409 (no 500)
- PUT /v1/zones/{id} → edita. Requiere editor.
- DELETE /v1/zones/{id} → elimina (CASCADE). Requiere admin.

## CRUD Sites — /v1/sites
- GET /v1/sites?zone_id=... → lista
- POST /v1/sites → valida zone_id existe → 404 si no. IntegrityError → 409.
- PUT /v1/sites/{id}, DELETE /v1/sites/{id}

## CRUD Cells — /v1/cells
- GET /v1/cells?site_id=...
- POST /v1/cells → valida site_id existe → 404 si no
  Body: {site_id, name, cell_type, row_id, rack_unit, description}
- PUT /v1/cells/{id}, DELETE /v1/cells/{id}
- GET /v1/cells/{id}/assets → assets asignados

## POST /v1/cells/bulk-assign
⚠️ DECLARAR ANTES DE /v1/cells/{cell_id} EN EL ROUTER
```json
{"cell_id": "uuid-o-null", "asset_ids": ["uuid1", "uuid2"]}
```
Si cell_id = null → desvincula los assets (pone cell_id a null en assets).
