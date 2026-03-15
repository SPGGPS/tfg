# API - Perfil de usuario y avatar

## ADDED Requirements

### Requirement: Endpoint PATCH /v1/auth/me/avatar

El sistema SHALL exponer PATCH /v1/auth/me/avatar para subir imagen de avatar (multipart/form-data).

#### Scenario: Subida exitosa de avatar
- **GIVEN** un usuario autenticado con una imagen válida (JPEG/PNG, máx 2MB)
- **WHEN** realiza PATCH /v1/auth/me/avatar con el archivo
- **THEN** el avatar se guarda y la respuesta confirma el éxito

### Requirement: Validación de archivos de avatar

El backend SHALL aceptar solo image/jpeg e image/png con tamaño máximo de 2MB.

#### Scenario: Rechazo de archivo inválido
- **GIVEN** un usuario que intenta subir un archivo con extensión .php o tipo incorrecto
- **WHEN** realiza PATCH /v1/auth/me/avatar
- **THEN** el servidor responde con 422 Unprocessable Entity (Magic Bytes check)
