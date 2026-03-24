# Tasks: App Core (Full Stack)

## 1. Backend (FastAPI)
- [ ] 1.1 Scaffold FastAPI project con OpenAPI (v1)
- [ ] 1.2 Implementar modelos DB: Asset (polimórfico), Tag, AuditLog
- [ ] 1.3 Implementar endpoints: `/v1/assets`, `/v1/tags`, `/v1/audit-logs`, `/v1/auth/oidc`
- [x] 1.4 Implementar historificación (`as_of`) y paginación
- [ ] 1.5 Integrar Keycloak (OpenID Connect) para auth + RBAC
- [x] 1.6 Implementar bulk import endpoint `/v1/assets/bulk-import` con validación JSON segura

## 2. Frontend (React)
- [ ] 2.1 Scaffold Vite + React + Tailwind
- [ ] 2.2 Implementar login OpenID (PKCE) y manejo de tokens en cookies
- [ ] 2.3 Implementar dashboard de inventario (tabla + filtros + ordenación)
- [ ] 2.4 Implementar selector histórico (Live / hora pasada)
- [ ] 2.5 Implementar UI de tags y compliance badges

## 3. Infraestructura
- [x] 3.1 Configurar Docker Compose / Helm Charts para backend + frontend + postgres + keycloak
- [x] 3.2 Configurar cronjobs para ingestión horaria y retención de logs
- [x] 3.3 Asegurar K8s NetworkPolicies (DB solo accesible desde backend)
