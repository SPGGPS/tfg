# Backend - Perfil de usuario

## ADDED Requirements

### Requirement: Endpoint de perfil y avatar
El backend SHALL exponer endpoints para consultar y actualizar datos de perfil, incluyendo upload de avatar.

#### Scenario: Obtener perfil
- **GIVEN** un usuario autenticado
- **WHEN** realiza GET /v1/auth/me
- **THEN** recibe su perfil con nombre, email y roles

#### Scenario: Subir avatar
- **GIVEN** un usuario autenticado
- **WHEN** realiza PATCH /v1/auth/me/avatar con imagen válida
- **THEN** el avatar se guarda y se retorna URL/identificador

### Requirement: Validación de archivos
El backend SHALL validar que las imágenes de avatar sean JPEG/PNG y no excedan 2MB.

#### Scenario: Archivo inválido
- **GIVEN** un archivo no permitido (PHP, exe, etc.)
- **WHEN** se intenta subir
- **THEN** el backend responde 422 Unprocessable Entity
