id: user-profile

# openspec/changes/user-profile/.openspec.yaml
schema: spec-driven
created: 2026-03-14

# Contexto: Gestión de Perfil, Sesión y Avatar
context: |
  Feature: User Profile & Session Management
  Domain: Identidad de usuario y personalización.
  Security: Información extraída de Keycloak + Almacenamiento de avatar local/S3.
  Roles: admin, editor, viewer.

# Definición del Cambio
proposal: |
  Implementar la gestión de perfil de usuario incluyendo personalización de imagen:
  1. Perfil: Vista de datos (Nombre, Email) y Role Badge.
  2. Avatar: Permitir al usuario subir una imagen personalizada o usar la de Keycloak.
  3. Logout: Cierre de sesión seguro y limpieza de tokens.

# Reglas de implementación
rules:
  openapi_spec:
    - Endpoint 'PATCH /v1/auth/me/avatar': Recibe un archivo de imagen (multipart/form-data).
    - Validar tipos de archivo: solo image/jpeg, image/png y un tamaño máximo de 2MB.
  backend_code:
    - Seguridad de Archivos: Renombrar el archivo a un UUID para evitar 'Path Traversal'.
    - Sanitización: Eliminar metadatos EXIF de las imágenes para proteger la privacidad.
    - Almacenamiento: Guardar en un PersistentVolumeClaim (PVC) de K8s o compatible con S3.
  frontend_code:
    - Componente Avatar: Usar iniciales del usuario como fallback (Shadcn/UI Avatar).
    - Upload UX: Previsualización de la imagen antes de subir y barra de progreso.
    - Notificaciones: Feedback visual tras actualizar la imagen correctamente.
  k8s_manifests:
    - Definir un PVC para el almacenamiento de avatares si no se usa un servicio externo.

# Desglose de tareas
tasks:
  - name: "API: Implement Avatar upload with security sanitization"
    hours: 3
  - name: "Frontend: Profile page with Avatar upload and Preview"
    hours: 3
  - name: "Backend: Integration with S3 or K8s Storage for assets"
    hours: 2
