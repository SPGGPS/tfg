# Design: User Profile y Avatar

## Context

Perfil con Nombre, Email, Role Badge. Avatar subible (JPEG/PNG, 2MB). Almacenamiento local o S3.

## Goals / Non-Goals

**Goals:** PATCH /v1/auth/me/avatar, sanitización EXIF, fallback a iniciales, previsualización antes de subir.

**Non-Goals:** Edición de nombre/email (vienen de Keycloak), múltiples avatares.

## Decisions

| Decisión | Rationale |
|----------|-----------|
| UUID como nombre de archivo | Evitar Path Traversal |
| Magic Bytes check | Rechazar archivos disfrazados (ej. .php.jpg) |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Archivos maliciosos | Magic Bytes, tipos MIME estrictos |
| Privacidad EXIF | Eliminar metadatos antes de guardar |
