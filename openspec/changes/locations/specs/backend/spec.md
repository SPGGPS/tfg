# Backend Spec — Localizaciones físicas

## models/location.py

```python
class Zone(Base):
    __tablename__ = "zones"
    id, name(200), description, created_at, updated_at
    sites = relationship("Site", back_populates="zone", cascade="all, delete-orphan")

class Site(Base):
    __tablename__ = "sites"
    id, zone_id(FK zones.id CASCADE), name(200), address(500), description, created_at, updated_at
    zone = relationship("Zone"), cells = relationship("Cell", cascade="all, delete-orphan")

class Cell(Base):
    __tablename__ = "cells"
    id, site_id(FK sites.id CASCADE), name(200), cell_type(50),
    row_id(50), rack_unit(50), description, created_at, updated_at
    site = relationship("Site")

CELL_TYPES = ["datacenter", "serverroom", "rack", "cabinet", "floor", "zone", "other"]
```

## routers/locations.py — orden crítico de declaración
```python
@router.get("/v1/locations/tree")          # específico primero
@router.post("/v1/cells/bulk-assign")       # específico ANTES de /{cell_id}
@router.get("/v1/cells/{cell_id}/assets")   # con parámetro después
```

## Manejo de IntegrityError
```python
from sqlalchemy.exc import IntegrityError

@router.post("/v1/zones", status_code=201)
def create_zone(body, db, user):
    try:
        z = Zone(**body.dict()); db.add(z); db.commit(); db.refresh(z)
        return z.to_dict()
    except IntegrityError:
        db.rollback()  # OBLIGATORIO antes de relanzar
        raise HTTPException(409, f"Ya existe una zona con el nombre '{body.name}'")
```
