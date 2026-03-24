# Frontend - Tests UI / E2E

## ADDED Requirements

### Requirement: Pruebas de UI para rutas protegidas
El frontend SHALL tener pruebas E2E que verifiquen el acceso basado en roles.

#### Scenario: Ruta protegida
- **GIVEN** un usuario con rol 'viewer'
- **WHEN** intenta acceder a una ruta de admin
- **THEN** la aplicación bloquea el acceso y muestra un mensaje apropiado

### Requirement: Pruebas de carga de avatar
El frontend SHALL tener tests que verifiquen la previsualización y subida de avatar.

#### Scenario: Avatar upload
- **GIVEN** un usuario selecciona una imagen
- **WHEN** confirma la subida
- **THEN** se muestra la previsualización y la petición se envía al backend
