# Backend — Localizaciones físicas (Zone → Site → Cell)

## ADDED Requirements

---

### Requirement: Modelos SQLAlchemy Zone, Site, Cell

Tres modelos separados en `app/models/location.py`:

```python
class Zone(Base):
    __tablename__ = "zones"
    id          = Column(String, PK, default=uuid4)
    name        = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), ...)
    updated_at  = Column(DateTime(timezone=True), ...)
    sites = relationship("Site", back_populates="zone", cascade="all, delete-orphan")

class Site(Base):
    __tablename__ = "sites"
    id          = Column(String, PK)
    zone_id     = Column(String, ForeignKey("zones.id", ondelete="CASCADE"), nullable=False)
    name        = Column(String(200), nullable=False)
    address     = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    zone  = relationship("Zone", back_populates="sites")
    cells = relationship("Cell", back_populates="site", cascade="all, delete-orphan")

class Cell(Base):
    __tablename__ = "cells"
    id          = Column(String, PK)
    site_id     = Column(String, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    name        = Column(String(200), nullable=False)
    cell_type   = Column(String(50), nullable=True)
    row_id      = Column(String(50), nullable=True)
    rack_unit   = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    site = relationship("Site", back_populates="cells")
```

`Cell._full_path()` — método de instancia que devuelve la ruta completa:
```python
def _full_path(self):
    parts = []
    if self.site and self.site.zone: parts.append(self.site.zone.name)
    if self.site: parts.append(self.site.name)
    parts.append(self.name)
    return " › ".join(parts)
```

---

### Requirement: cell_id en Asset y Application

```python
# Asset
cell_id = Column(String, ForeignKey("cells.id", ondelete="SET NULL"), nullable=True)

# Application
cell_id = Column(String, ForeignKey("cells.id", ondelete="SET NULL"), nullable=True)
```

`ON DELETE SET NULL` — si se elimina una cell, los assets y aplicaciones que la referenciaban quedan sin cell asignada (no se eliminan).

---

### Requirement: orden de endpoints en el router de locations

El router `locations.py` contiene todos los endpoints de Zone, Site y Cell. El endpoint `POST /v1/cells/bulk-assign` **debe declararse antes** de `GET /v1/cells/{cell_id}`. Si se declara después, FastAPI trata "bulk-assign" como un `cell_id` y devuelve 404.

```python
# ✅ CORRECTO — bulk-assign antes que /{cell_id}
@router.post("/v1/cells/bulk-assign", ...)
def bulk_assign(...): ...

@router.get("/v1/cells/{cell_id}/assets", ...)
def cell_assets(...): ...

# ❌ INCORRECTO — bulk-assign después de /{cell_id}
# FastAPI procesa las rutas en orden de declaración; "bulk-assign" matchea primero /{cell_id}
```

Esta regla aplica también a cualquier ruta estática que comparta prefijo con una ruta con parámetro de path.

---

### Requirement: Registro en __init__ y main.py

```python
# models/__init__.py
from app.models.location import Zone, Site, Cell   # NO Location

# main.py
from app.routers.locations import router as locations_router
app.include_router(locations_router)
```

---

### Requirement: Seed de localizaciones en init_db.py

El seed crea el árbol de ejemplo completo antes del commit final:

```python
from app.models.location import Zone, Site, Cell

zone1 = Zone(id="zone-ayto", name="Ayuntamiento San Sebastián de los Reyes")
site1 = Site(id="site-main", zone_id="zone-ayto", name="Edificio Principal",
             address="Plaza de la Constitución s/n")
site2 = Site(id="site-backup", zone_id="zone-ayto", name="Edificio Anexo",
             address="C/ Cervantes 12")
cell1 = Cell(id="cell-cpd1",    site_id="site-main",   name="CPD Principal",  cell_type="datacenter")
cell2 = Cell(id="cell-rack-a",  site_id="site-main",   name="Rack A",         cell_type="rack",
             row_id="Fila A",   rack_unit="U1-U42")
cell3 = Cell(id="cell-rack-net",site_id="site-main",   name="Rack Red",       cell_type="rack",
             row_id="Fila B",   rack_unit="U1-U24")
cell4 = Cell(id="cell-cpd2",    site_id="site-backup", name="CPD Backup",     cell_type="datacenter")
```

---

### Requirement: Enrichment de cell en listado de aplicaciones

El endpoint `GET /v1/applications` enriquece cada aplicación con la información de su cell:

```python
def enrich_app(a):
    d = a.to_dict()
    if a.cell_id:
        cell = db.query(Cell).filter_by(id=a.cell_id).first()
        d['cell_name']      = cell.name if cell else None
        d['location_path']  = cell._full_path() if cell else None
    else:
        d['cell_name'] = None
        d['location_path'] = None
    return d
```

#### Scenario: Aplicación con cell asignada en el listado
- **GIVEN** la aplicación "sede-api" con cell_id="cell-rack-a"
- **WHEN** GET /v1/applications
- **THEN** la app devuelve cell_name="Rack A" y location_path="Ayuntamiento SSReyes › Edificio Principal › Rack A"

#### Scenario: 500 evitado — orden de endpoints correcto
- **GIVEN** el router tiene bulk-assign declarado ANTES de /{cell_id}
- **WHEN** POST /v1/cells/bulk-assign con body válido
- **THEN** responde 200 (no 404 ni 422 por path param erróneo)
