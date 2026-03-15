# Backend - Tags Management

## ADDED Requirements

### Requirement: Protecciones de etiquetas del sistema
El backend SHALL bloquear cualquier modificación o eliminación de etiquetas con `origin='system'`.

#### Scenario: Bloqueo de etiqueta system
- **GIVEN** una etiqueta con `origin='system'`
- **WHEN** un admin intenta PUT o DELETE
- **THEN** el backend responde 400 Bad Request

### Requirement: Propagación de cambios de etiqueta
El backend SHALL propagar automáticamente cambios de nombre/color a todos los activos vinculados.

#### Scenario: Propagación de color
- **GIVEN** una etiqueta manual asignada a múltiples activos
- **WHEN** se actualiza su color
- **THEN** todos los activos asociados reflejan el color actualizado en sus datos

### Requirement: Endpoint de asignación masiva
El backend SHALL exponer POST /v1/assets/bulk-tags para asignar etiquetas manuales a múltiples activos.

#### Scenario: Asignación masiva
- **GIVEN** un admin con lista de asset_ids y tag_ids
- **WHEN** llama al endpoint
- **THEN** cada activo recibe las etiquetas solicitadas
