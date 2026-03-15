# Frontend - Dashboard de inventario

## ADDED Requirements

### Requirement: Búsqueda por todos los campos mostrados

El dashboard SHALL incluir un botón de búsqueda que permita buscar por todos los campos visibles.

#### Scenario: Búsqueda por texto
- **GIVEN** un usuario en el dashboard de inventario
- **WHEN** introduce texto en el campo de búsqueda
- **THEN** la tabla se filtra mostrando solo activos que coinciden en algún campo visible

### Requirement: Ordenación por todos los campos

El dashboard SHALL permitir ordenar la tabla por todos los campos mostrados.

#### Scenario: Ordenar por columna
- **GIVEN** un usuario en la tabla de activos
- **WHEN** hace clic en el encabezado de una columna
- **THEN** la tabla se reordena según ese campo (asc/desc)

### Requirement: Historificación con selector de momento

El dashboard SHALL permitir seleccionar "Live" o un momento pasado (día y hora) para consultar el inventario histórico.

#### Scenario: Vista Live vs histórico
- **GIVEN** un usuario en el dashboard
- **WHEN** selecciona "Live" o un día/hora del desplegable
- **THEN** la tabla muestra el inventario en ese momento temporal
