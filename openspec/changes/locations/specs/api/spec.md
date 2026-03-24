# API — Localizaciones físicas (Zone → Site → Cell)

## Modelo conceptual

La infraestructura física se organiza en tres niveles:

```
Zona (agrupación lógica)
  └── Site / Localización física (edificio o campus)
        └── Cell / Celda (CPD, sala, rack, armario — donde se asignan los assets)
```

**Principio:** los assets y las aplicaciones se asignan siempre a una **Cell**, nunca a un Site o una Zona directamente. Esto permite saber con precisión dónde está cada dispositivo (rack, fila, posición U).

---

### Requirement: Entidad Zone

Agrupación lógica de varias ubicaciones físicas. Ejemplo: "Ayuntamiento SSReyes", "Nube AWS eu-west-1".

**Tabla `zones`:**
- `id` (UUID PK)
- `name` (string, max 200, único, obligatorio)
- `description` (text, nullable)
- `created_at`, `updated_at` (TIMESTAMPTZ)

**Endpoints:**
- `GET  /v1/zones` — lista de zonas con `site_count`
- `POST /v1/zones` — crear zona (body: `name`, `description?`)
- `PUT  /v1/zones/{id}` — actualizar
- `DELETE /v1/zones/{id}` — eliminar en cascada (elimina sus Sites y Cells)

---

### Requirement: Entidad Site (Localización física)

Edificio o campus concreto dentro de una zona. Ejemplo: "Edificio Principal", "CPD Externo Rackspace".

**Tabla `sites`:**
- `id` (UUID PK)
- `zone_id` (UUID FK → zones.id CASCADE, obligatorio)
- `name` (string, max 200, obligatorio)
- `address` (string, max 500, nullable) — dirección postal completa
- `description` (text, nullable)
- `created_at`, `updated_at` (TIMESTAMPTZ)

**Endpoints:**
- `GET  /v1/sites?zone_id={id}` — lista de sites, filtrable por zona; devuelve `zone_name` y `cell_count`
- `POST /v1/sites` — body: `zone_id` (obligatorio), `name`, `address?`, `description?`
- `PUT  /v1/sites/{id}`
- `DELETE /v1/sites/{id}` — elimina sus Cells en cascada

---

### Requirement: Entidad Cell (Celda / CPD / Rack)

Ubicación precisa dentro de un site donde se instala la infraestructura. Es el nivel de granularidad al que se asignan assets y aplicaciones.

**Tabla `cells`:**
- `id` (UUID PK)
- `site_id` (UUID FK → sites.id CASCADE, obligatorio)
- `name` (string, max 200, obligatorio) — ej: "CPD Principal", "Rack A", "Armario Comunicaciones"
- `cell_type` (string, max 50, nullable) — enum: `datacenter` | `serverroom` | `rack` | `cabinet` | `floor` | `zone` | `other`
- `row_id` (string, max 50, nullable) — fila dentro del CPD, ej: "Fila A", "Pasillo Frío"
- `rack_unit` (string, max 50, nullable) — posición en el rack, ej: "U1-U42", "U12"
- `description` (text, nullable)
- `created_at`, `updated_at` (TIMESTAMPTZ)

**Campo calculado `full_path`** (no almacenado): `"{zone.name} › {site.name} › {cell.name}"`

**Endpoints:**
- `GET  /v1/cells?site_id={id}` — lista de cells, filtrable por site; devuelve `site_name`, `zone_name`, `full_path`
- `POST /v1/cells` — body: `site_id`, `name`, `cell_type?`, `row_id?`, `rack_unit?`, `description?`
- `PUT  /v1/cells/{id}`
- `DELETE /v1/cells/{id}`
- `GET  /v1/cells/{id}/assets` — assets asignados a esta cell

---

### Requirement: GET /v1/locations/tree — árbol completo

Devuelve todas las zonas con sus sites y cells anidados. Usado por la página de localizaciones para renderizar el árbol completo de una sola llamada.

```json
[
  {
    "id": "zone-ayto",
    "name": "Ayuntamiento San Sebastián de los Reyes",
    "description": "Instalaciones físicas del Ayuntamiento",
    "site_count": 2,
    "sites": [
      {
        "id": "site-main",
        "zone_id": "zone-ayto",
        "zone_name": "Ayuntamiento San Sebastián de los Reyes",
        "name": "Edificio Principal",
        "address": "Plaza de la Constitución s/n",
        "cell_count": 3,
        "cells": [
          {
            "id": "cell-cpd1",
            "site_id": "site-main",
            "site_name": "Edificio Principal",
            "zone_name": "Ayuntamiento San Sebastián de los Reyes",
            "name": "CPD Principal",
            "cell_type": "datacenter",
            "row_id": null,
            "rack_unit": null,
            "full_path": "Ayuntamiento San Sebastián de los Reyes › Edificio Principal › CPD Principal"
          },
          {
            "id": "cell-rack-a",
            "name": "Rack A",
            "cell_type": "rack",
            "row_id": "Fila A",
            "rack_unit": "U1-U42",
            "full_path": "Ayuntamiento San Sebastián de los Reyes › Edificio Principal › Rack A"
          }
        ]
      }
    ]
  }
]
```

---

### Requirement: POST /v1/cells/bulk-assign — asignación masiva de assets

Asigna (o desvincula) un conjunto de assets a una cell de una sola llamada.

**Body:**
```json
{
  "asset_ids": ["uuid1", "uuid2", "uuid3"],
  "cell_id": "cell-rack-a"   // null = desvincular
}
```

**Respuesta:**
```json
{ "updated": 3, "cell_id": "cell-rack-a" }
```

**IMPORTANTE:** este endpoint debe declararse **antes** de `GET /v1/cells/{cell_id}` en el router para que FastAPI no interprete "bulk-assign" como un `cell_id`.

#### Scenario: Asignación masiva correcta
- **GIVEN** 3 assets sin cell asignada
- **WHEN** POST /v1/cells/bulk-assign con asset_ids=[id1,id2,id3] y cell_id="cell-rack-a"
- **THEN** responde 200 con {"updated": 3, "cell_id": "cell-rack-a"}
- **THEN** GET /v1/cells/cell-rack-a/assets devuelve los 3 assets

#### Scenario: Desvinculación masiva
- **GIVEN** 2 assets asignados a "cell-rack-a"
- **WHEN** POST /v1/cells/bulk-assign con asset_ids=[id1,id2] y cell_id=null
- **THEN** responde 200 con {"updated": 2, "cell_id": null}
- **THEN** los assets ya no tienen cell asignada

---

### Requirement: cell_id en Asset y Application

Tanto `Asset` como `Application` tienen un campo `cell_id` (UUID FK → cells.id, ON DELETE SET NULL, nullable).

La respuesta de GET /v1/applications incluye:
- `cell_id` — UUID de la cell asignada (o null)
- `cell_name` — nombre de la cell (o null)
- `location_path` — ruta completa calculada (o null), ej: "Ayuntamiento › Edificio Principal › Rack A"

#### Scenario: Asset con celda asignada
- **GIVEN** el asset "web-prod-01" con cell_id="cell-rack-a"
- **WHEN** GET /v1/assets/{id}
- **THEN** el asset incluye cell_id, y la ruta completa es "Ayuntamiento SSReyes › Edificio Principal › Rack A"

---

### Datos de seed

```
Zona: "Ayuntamiento San Sebastián de los Reyes"
  Site: "Edificio Principal" (Plaza de la Constitución s/n)
    Cell: "CPD Principal"  (type: datacenter)
    Cell: "Rack A"         (type: rack, row: Fila A, unit: U1-U42)
    Cell: "Rack Red"       (type: rack, row: Fila B, unit: U1-U24)
  Site: "Edificio Anexo" (C/ Cervantes 12)
    Cell: "CPD Backup"     (type: datacenter)
```
