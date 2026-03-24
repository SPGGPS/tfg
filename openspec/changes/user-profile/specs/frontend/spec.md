# Frontend - Perfil de usuario

## ADDED Requirements

### Requirement: Vista de perfil con datos del usuario
La página de perfil SHALL mostrar Nombre, Email y Role Badge del usuario extraídos del JWT.

#### Scenario: Visualización de perfil
- **GIVEN** un usuario autenticado
- **WHEN** accede a /profile
- **THEN** ve su nombre, email y badge con su rol (admin/editor/viewer)

### Requirement: Avatar persistente por usuario
El componente Avatar SHALL mostrar la imagen subida por el usuario si existe. La URL del avatar SHALL persistirse en backend asociada al user_id del JWT. Al cargar la página de perfil, el frontend SHALL llamar a GET /v1/auth/me/avatar para obtener la URL actual. Si no hay avatar guardado, muestra las iniciales del usuario.

#### Scenario: Avatar guardado mostrado en perfil y header
- **GIVEN** un usuario que ha subido un avatar previamente
- **WHEN** abre la aplicación en una nueva sesión
- **THEN** su avatar aparece tanto en el header como en la página de perfil

#### Scenario: Fallback a iniciales
- **GIVEN** un usuario sin avatar subido
- **WHEN** se renderiza el Avatar
- **THEN** se muestran las iniciales del nombre del usuario

### Requirement: Previsualización antes de subir avatar
La UI SHALL mostrar previsualización de la imagen seleccionada antes de confirmar la subida con barra de progreso o spinner durante la carga.

#### Scenario: Previsualización de imagen
- **GIVEN** un usuario que selecciona un archivo de imagen válido
- **WHEN** el archivo pasa validación de tipo y tamaño
- **THEN** se muestra una previsualización antes del botón de confirmar subida

### Requirement: Último login correcto e incorrecto
La página de perfil SHALL mostrar:
- **Último acceso exitoso**: fecha, hora e IP del último login correcto
- **Último intento fallido**: fecha, hora e IP del último intento de login fallido (si existe)

Esta información se obtiene de GET /v1/auth/me que incluirá los campos last_login_at, last_login_ip, last_failed_login_at, last_failed_login_ip.

#### Scenario: Visualización de último login
- **GIVEN** un usuario autenticado con historial de logins
- **WHEN** accede a su página de perfil
- **THEN** ve la fecha/hora/IP del último acceso exitoso y del último intento fallido (si lo hay)

#### Scenario: Sin intentos fallidos
- **GIVEN** un usuario sin intentos de login fallidos registrados
- **WHEN** accede a su perfil
- **THEN** el campo "Último intento fallido" muestra "Ninguno registrado"
