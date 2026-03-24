id: user-profile

context: |
  Feature: Perfil con avatar, datos de login y badge de rol

proposal: |
  1. UserProfile en BD: avatar_filename, last_login_at/ip, last_failed_login_at/ip
  2. PATCH /v1/auth/me/avatar: sube imagen con UUID, strip EXIF
  3. GET /v1/auth/me/avatar: sirve la imagen del usuario actual
  4. ProfilePage: muestra nombre, email, badge rol, historial logins, avatar

status: Implementado al 100%.
