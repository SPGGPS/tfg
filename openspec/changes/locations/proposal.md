# Proposal: Localizaciones físicas (Zone → Site → Cell)

## Motivación
El CMDB gestiona activos físicos pero no sabe dónde están ubicados. Para el mapa de dependencias y el análisis de impacto es fundamental conocer si dos elementos comparten rack, sala, CPD o edificio.

## Modelo — tres niveles

```
Zona (agrupación lógica)
  └── Site / Localización física (edificio o campus concreto)
        └── Cell / Celda (CPD, sala, rack, armario — granularidad de asignación)
```

| Nivel | Ejemplos | Tiene dirección | Se asignan assets |
|-------|----------|-----------------|-------------------|
| **Zona** | "Ayuntamiento SSReyes", "AWS eu-west-1" | No | No |
| **Site** | "Edificio Principal", "CPD Externo" | Sí | No |
| **Cell** | "CPD Principal", "Rack A", "Armario Comunicaciones" | No | **Sí** |

## Cambios respecto al modelo anterior

El modelo anterior (`Location` autorreferenciado con `parent_id`) fue descartado por dos motivos:
1. **Error 500 al crear**: SQLAlchemy y el router tenían problemas de orden de declaración con rutas estáticas vs parámetros de path
2. **Semántica débil**: no quedaba claro qué era un "edificio" vs un "rack" vs una "sala"

El nuevo modelo tiene semántica explícita en cada nivel y endpoints separados por entidad.

## Seed
```
Zona: "Ayuntamiento San Sebastián de los Reyes"
  Site: "Edificio Principal" (Plaza de la Constitución s/n)
    Cell: "CPD Principal"  (datacenter)
    Cell: "Rack A"         (rack, Fila A, U1-U42)
    Cell: "Rack Red"       (rack, Fila B, U1-U24)
  Site: "Edificio Anexo" (C/ Cervantes 12)
    Cell: "CPD Backup"     (datacenter)
```

## Bulk assign masivo
Desde cada celda en la UI, botón "Asignar assets" abre un modal con búsqueda y selección múltiple. Endpoint `POST /v1/cells/bulk-assign` (declarado antes del `/{cell_id}` en el router).
