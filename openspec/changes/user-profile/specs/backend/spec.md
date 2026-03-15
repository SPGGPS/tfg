# Backend - Perfil de usuario

## ADDED Requirements

### Requirement: Modelo UserProfile para persistencia de avatar y login history
El backend SHALL mantener una tabla `user_profiles` con:
- user_id (string PK) — sub del JWT
- avatar_filename (string | null) — nombre UUID del archivo de avatar
- last_login_at (datetime | null)
- last_login_ip (string | null)
- last_failed_login_at (datetime | null)
- last_failed_login_ip (string | null)
- created_at, updated_at

Esta tabla se crea o actualiza (upsert por user_id) en cada autenticación y en cada subida de avatar.

#### Scenario: Upsert en login
- **GIVEN** un usuario que completa el flujo OIDC exitosamente
- **WHEN** el backend valida el JWT
- **THEN** actualiza user_profiles con last_login_at y last_login_ip del request

#### Scenario: Registro de intento fallido
- **GIVEN** una petición con JWT inválido o expirado
- **WHEN** el middleware de auth rechaza el token
- **THEN** registra last_failed_login_at y last_failed_login_ip en user_profiles

### Requirement: Endpoint de perfil enriquecido
GET /v1/auth/me SHALL combinar datos del JWT con datos de user_profiles para devolver el perfil completo incluyendo last_login_at, last_login_ip, last_failed_login_at, last_failed_login_ip y avatar_url.

### Requirement: Avatar asociado a user_id
El avatar subido SHALL guardarse con nombre UUID y la referencia (filename) SHALL almacenarse en user_profiles.avatar_filename asociada al user_id del JWT. De este modo el avatar persiste entre sesiones.

#### Scenario: Avatar persistente entre sesiones
- **GIVEN** un usuario que sube un avatar en una sesión
- **WHEN** inicia una nueva sesión
- **THEN** GET /v1/auth/me devuelve avatar_url con la URL del avatar guardado

### Requirement: Validación de archivos
Magic Bytes check obligatorio. Renombrado a UUID. Strip de metadatos EXIF con Pillow. Tipos permitidos: image/jpeg, image/png. Máximo 2MB.

#### Scenario: Rechazo por Magic Bytes
- **GIVEN** archivo con extensión .jpg pero Magic Bytes de ejecutable
- **WHEN** se sube
- **THEN** backend responde 422
