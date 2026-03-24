# Tasks: User Profile

## 1. Backend
- [x] 1.1 Modelo UserProfile: user_id PK, avatar_filename, last_login_at/ip,
           last_failed_login_at/ip
- [x] 1.2 Upsert UserProfile en cada autenticación exitosa
- [x] 1.3 PATCH /v1/auth/me/avatar: guarda con UUID, strip EXIF, 2MB max
- [x] 1.4 GET /v1/auth/me/avatar: sirve imagen por user_id
- [x] 1.5 GET /v1/auth/me: incluye datos de UserProfile + avatar_url

## 2. Frontend
- [x] 2.1 ProfilePage /profile: nombre, email, Role Badge, historial logins
- [x] 2.2 Avatar.jsx: muestra imagen o iniciales como fallback
- [x] 2.3 Upload avatar con previsualización antes de confirmar
- [x] 2.4 Avatar en topbar (esquina superior derecha)
