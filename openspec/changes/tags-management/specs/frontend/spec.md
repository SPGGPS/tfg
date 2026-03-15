# Frontend - Gestión de etiquetas

## ADDED Requirements

### Requirement: Modal de confirmación para borrado

La UI SHALL mostrar un modal de confirmación antes de borrar una etiqueta, indicando el número de activos afectados.

#### Scenario: Confirmación de borrado
- **GIVEN** un admin que selecciona borrar una etiqueta
- **WHEN** hace clic en eliminar
- **THEN** aparece un modal con el número de activos que perderán la etiqueta y opción de confirmar/cancelar

### Requirement: Selector de color para edición

La UI SHALL incluir un selector de color (estilo Chrome) para editar el color de etiquetas manuales.

#### Scenario: Editar color de etiqueta
- **GIVEN** un admin editando una etiqueta manual
- **WHEN** abre el selector de color
- **THEN** puede elegir un color en formato hex y guardar el cambio
