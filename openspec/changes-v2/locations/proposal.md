id: locations

context: |
  Feature: Localización física de activos (Zone → Site → Cell)
  Domain: Gestión de infraestructura física.
  Motivación: El CMDB gestiona activos pero no sabe dónde están físicamente.
  Para análisis de impacto es fundamental saber si dos elementos comparten rack,
  sala, CPD o edificio.

proposal: |
  Modelo jerárquico de 3 niveles:
    Zone  → agrupación lógica (sin dirección). Ej: "Ayuntamiento SSReyes"
    Site  → edificio/campus con dirección. Ej: "Edificio Principal"
    Cell  → CPD/rack/sala donde se asignan assets. Ej: "Rack A", "CPD Backup"

  Los assets y Applications tienen FK cell_id → cells.id (SET NULL on delete).
  La ruta /locations muestra un árbol jerárquico con CRUD en cada nivel.
  Seed inicial con 1 zona, 2 sites, 4 cells de ejemplo.

status: Implementado al 100%.
