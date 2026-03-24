# Design: Localizaciones físicas

## Modelo conceptual
```
Zone (agrupación lógica)
  └── Site (edificio/campus con dirección física)
        └── Cell (CPD/rack/sala — aquí se asignan assets y applications)
```

| Nivel | Tiene dirección | Se asignan assets |
|-------|-----------------|-------------------|
| Zone  | No | No |
| Site  | Sí | No |
| Cell  | No | Sí (FK cell_id en assets y applications) |

## Cell types
datacenter, serverroom, rack, cabinet, floor, zone, other

## full_path
Calculado en Cell.to_dict(): "Zona › Site › Cell"
Ejemplo: "Ayuntamiento SSReyes › Edificio Principal › Rack A"

## Seed inicial (init_db.py)
```
Zona: "Ayuntamiento San Sebastián de los Reyes"
  Site: "Edificio Principal" (Plaza de la Constitución s/n)
    Cell: "CPD Principal" (datacenter)
    Cell: "Rack A" (rack, row_id="Fila A", rack_unit="U1-U42")
    Cell: "Rack Red" (rack, row_id="Fila B", rack_unit="U1-U24")
  Site: "Edificio Anexo" (C/ Cervantes 12)
    Cell: "CPD Backup" (datacenter)
```

## Decisiones

| Decisión | Rationale |
|----------|-----------|
| 3 niveles Zone/Site/Cell | Granularidad suficiente: lógica/edificio/rack |
| FK en Asset y Application | Permiten query "qué activos están en Rack A" |
| SET NULL on delete | Borrar una celda no borra los activos, los desvincula |
| BulkAssign endpoint | Asignar múltiples assets a una celda en un solo POST |
