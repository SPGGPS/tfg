# API - Gestión de etiquetas

## ADDED Requirements

### Requirement: Endpoints PUT y DELETE para tags restringidos a admin

El sistema SHALL exponer PUT /v1/tags/{tag_id} y DELETE /v1/tags/{tag_id} únicamente para rol 'admin'.

#### Scenario: Admin puede editar etiqueta manual
- **GIVEN** un usuario con rol 'admin' y una etiqueta con origin='manual'
- **WHEN** realiza PUT /v1/tags/{tag_id} con nuevos datos
- **THEN** la etiqueta se actualiza correctamente

### Requirement: Protección de etiquetas de sistema

El backend SHALL prohibir la modificación o borrado de etiquetas con origin='system'.

#### Scenario: No se puede modificar etiqueta de sistema
- **GIVEN** una etiqueta con origin='system'
- **WHEN** un admin intenta PUT o DELETE
- **THEN** el servidor responde con 400 Bad Request

### Requirement: Propagación de cambios en etiquetas manuales

Los cambios en nombre o color de una etiqueta manual SHALL reflejarse automáticamente en todos los activos vinculados.

#### Scenario: Cambio de color se propaga
- **GIVEN** una etiqueta manual asignada a varios activos
- **WHEN** se actualiza el color de la etiqueta
- **THEN** GET /v1/assets devuelve el nuevo color para todos los activos asociados
