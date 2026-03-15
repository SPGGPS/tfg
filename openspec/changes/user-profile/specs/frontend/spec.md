# Frontend - Perfil de usuario

## ADDED Requirements

### Requirement: Vista de perfil con datos del usuario

La página de perfil SHALL mostrar Nombre, Email y Role Badge del usuario.

#### Scenario: Visualización de perfil
- **GIVEN** un usuario autenticado
- **WHEN** accede a la página de perfil
- **THEN** ve su nombre, email y badge con su rol (admin/editor/viewer)

### Requirement: Componente Avatar con fallback

El componente Avatar SHALL usar las iniciales del usuario como fallback cuando no hay imagen.

#### Scenario: Fallback a iniciales
- **GIVEN** un usuario sin avatar subido
- **WHEN** se renderiza el Avatar
- **THEN** se muestran las iniciales del nombre del usuario

### Requirement: Previsualización antes de subir avatar

La UI SHALL mostrar previsualización de la imagen seleccionada antes de confirmar la subida.

#### Scenario: Previsualización de imagen
- **GIVEN** un usuario que selecciona un archivo de imagen
- **WHEN** el archivo es válido
- **THEN** se muestra una previsualización antes del botón de subir
