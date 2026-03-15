# API - Perfil de usuario y avatar

## ADDED Requirements

### Requirement: Endpoint GET /v1/auth/me con datos de login
GET /v1/auth/me SHALL devolver el perfil del usuario incluyendo:
- sub, preferred_username, email, roles
- last_login_at (datetime | null) — fecha/hora del último login exitoso
- last_login_ip (string | null) — IP del último login exitoso
- last_failed_login_at (datetime | null) — fecha/hora del último intento fallido
- last_failed_login_ip (string | null) — IP del último intento fallido
- avatar_url (string | null) — URL relativa del avatar actual

#### Scenario: Perfil con historial de logins
- **GIVEN** un usuario autenticado con historial de accesos
- **WHEN** realiza GET /v1/auth/me
- **THEN** recibe el perfil con los campos last_login_at, last_login_ip, last_failed_login_at, last_failed_login_ip y avatar_url

### Requirement: Endpoint GET /v1/auth/me/avatar
GET /v1/auth/me/avatar SHALL devolver la imagen de avatar del usuario autenticado o 404 si no existe.

#### Scenario: Avatar existente
- **GIVEN** un usuario con avatar subido
- **WHEN** realiza GET /v1/auth/me/avatar
- **THEN** recibe la imagen con el Content-Type correcto

### Requirement: Endpoint PATCH /v1/auth/me/avatar
PATCH /v1/auth/me/avatar recibe multipart/form-data con el archivo de imagen. Tras guardar, asocia la URL al user_id para que sea recuperable en sesiones futuras.

#### Scenario: Subida exitosa de avatar
- **GIVEN** un usuario autenticado con imagen válida (JPEG/PNG, máx 2MB)
- **WHEN** realiza PATCH /v1/auth/me/avatar
- **THEN** el avatar se guarda asociado a su user_id y la respuesta incluye avatar_url

### Requirement: Validación de archivos de avatar
Solo image/jpeg e image/png con máximo 2MB. Verificación por Magic Bytes, no solo extensión.

#### Scenario: Rechazo de archivo inválido
- **GIVEN** archivo con extensión .php o tipo incorrecto
- **WHEN** se intenta subir
- **THEN** responde 422 Unprocessable Entity
