id: app-core

# openspec/changes/app-core/.openspec.yaml
schema: spec-driven
created: 2026-03-15

# Contexto: Plataforma Full-Stack para Inventario y Cumplimiento
context: |
  Feature: Aplicación integral para gestión de inventario y cumplimiento de seguridad.
  Domain: CMDB centralizada con visibilidad de backups, EDR, monitorización y auditoría.
  Stack: React (Vite) + FastAPI + PostgreSQL + Keycloak (OpenID Connect).

# Definición del Cambio
proposal: |
  Construir la aplicación principal (backend + frontend) que soporte:
  1. Inventario de activos (servidores físicos/virtuales, switches, routers, AP) con sincronización horaria (Veeam, monitorización, EDR).
  2. UI React con login OpenID (PKCE), tabla de activos, filtros, ordenación, historificación, y gestión de etiquetas.
  3. Backend FastAPI con API REST (OpenAPI) que expone assets, etiquetas, auditoría y endpoints de ingestión.
  4. Seguridad: OpenID Connect, RBAC por roles (admin/editor/viewer), validación de entrada y protección contra inyección.

# Reglas de implementación
rules:
  openapi_spec:
    - Todos los endpoints SHALL documentarse con OpenAPI 3.1 y anotar roles permitidos con `x-required-roles`.
    - El modelo Asset SHALL ser polimórfico (discriminador `type`) y contener compliance fields (`edr_installed`, `last_backup`, `monitored`, `logs_enabled`, `last_sync`).
    - Endpoint `/v1/assets` SHALL soportar query params para historificación (`as_of` o `at`) y paginación.
    - Endpoint `/v1/auth/token` o `/v1/auth/oidc` SHALL soportar OpenID Connect Authorization Code + PKCE.

  backend_code:
    - Usar ORM con inyecciones parametrizadas para evitar SQLi.
    - Implementar caching ligero para datos de inventario que cambian cada hora.
    - Registrar auditoría de cambios importantes (tag, activos, login) usando el motor de audit-logs.

  frontend_code:
    - La UI debe manejar tokens OIDC en cookie HttpOnly/Secure y refrescar automáticamente con refresh token.
    - Garantizar accesibilidad (A11y) en tablas y modales.
    - Mostrar indicadores visuales (badge verde/rojo) para estado de compliance (EDR/monitorización/backup).

# Desglose de tareas
tasks:
  - name: "Backend: OpenAPI + FastAPI scaffold para assets, tags, audit, auth"
    hours: 4
  - name: "Frontend: React scaffold + login OpenID + dashboard de inventario"
    hours: 5
  - name: "DB: Modelos para assets, tags, audit y versionado histórico"
    hours: 3
  - name: "Infra: Dev setup con Docker/K8s y configuración Keycloak"
    hours: 3
