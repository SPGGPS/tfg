# Tasks: User Profile

## 1. Backend

- [ ] 1.1 Crear modelo UserProfile (user_id PK, avatar_filename, last_login_at, last_login_ip, last_failed_login_at, last_failed_login_ip)
- [ ] 1.2 Upsert en user_profiles al validar JWT exitosamente (last_login_at, last_login_ip)
- [ ] 1.3 Registrar last_failed_login_at/ip cuando el middleware rechaza un JWT
- [ ] 1.4 Actualizar GET /v1/auth/me para incluir datos de user_profiles y avatar_url
- [ ] 1.5 Endpoint PATCH /v1/auth/me/avatar: guardar con UUID, strip EXIF, asociar filename a user_id en user_profiles
- [ ] 1.6 Endpoint GET /v1/auth/me/avatar: servir imagen por user_id (no por filename en URL)
- [ ] 1.7 Validar tipo (jpeg/png) por Magic Bytes y tamaño (2MB)

## 2. Frontend

- [ ] 2.1 Página de perfil: mostrar Nombre, Email, Role Badge
- [ ] 2.2 Sección "Seguridad de acceso": último login exitoso (fecha + IP) y último intento fallido (fecha + IP o "Ninguno")
- [ ] 2.3 Componente Avatar: cargar desde GET /v1/auth/me/avatar al montar; fallback a iniciales
- [ ] 2.4 Upload con previsualización, validación client-side (tipo + tamaño) y spinner durante la carga
- [ ] 2.5 Mostrar avatar actualizado en header sin recargar la página tras subida exitosa
