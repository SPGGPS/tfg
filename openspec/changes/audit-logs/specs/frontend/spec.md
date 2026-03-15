# Frontend - Audit Logs

## ADDED Requirements

### Requirement: Vista Auditoría solo para admin

El enlace a la sección "Auditoría" SHALL renderizarse únicamente cuando el JWT contiene el rol 'admin'.

#### Scenario: Visibilidad condicional por rol
- **GIVEN** un usuario con rol 'admin'
- **WHEN** carga la aplicación
- **THEN** el sidebar muestra el enlace a "Auditoría"

#### Scenario: Oculto para editor y viewer
- **GIVEN** un usuario con rol 'editor' o 'viewer'
- **WHEN** carga la aplicación
- **THEN** el enlace a "Auditoría" no aparece en el sidebar

### Requirement: Tabla de logs con filtros dinámicos

La vista de auditoría SHALL mostrar una tabla con filtros por tipo de actividad y rango de fechas.

#### Scenario: Filtrado por activity_type
- **GIVEN** un admin en la vista de Auditoría
- **WHEN** selecciona un tipo (CREATE, UPDATE, DELETE, TAG_ASSIGN, LOGIN)
- **THEN** la tabla se actualiza mostrando solo los registros de ese tipo

#### Scenario: Filtrado por date_range
- **GIVEN** un admin en la vista de Auditoría
- **WHEN** establece un rango de fechas válido (start/end)
- **THEN** la tabla solo muestra logs dentro del rango seleccionado

### Requirement: Modal de detalle con diff JSON

El sistema SHALL permitir ver el diff completo del registro en un modal al seleccionar un registro.

#### Scenario: Detalle de un log
- **GIVEN** un admin visualizando la tabla de auditoría
- **WHEN** hace click en un registro
- **THEN** se abre un modal mostrando el JSON diff exacto almacenado en el campo `changes`
