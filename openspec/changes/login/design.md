# Design: Login OIDC con Keycloak

## Context

Sustituir auth local por Keycloak (IdP). Flujo Authorization Code + PKCE. Roles en JWT. React como cliente OIDC, FastAPI como Resource Server validando tokens.

## Goals / Non-Goals

**Goals:** Keycloak Realm + Client (PKCE), roles en token, FastAPI middleware JWT+RBAC, React ProtectedRoute, Silent Refresh.

**Non-Goals:** Gestión de contraseñas en backend, múltiples IdPs.

## Decisions

| Decisión | Rationale |
|----------|-----------|
| RS256 + JWKS | Validación sin compartir secret con backend |
| Roles en resource_access.${client_id}.roles | Estándar Keycloak; claim personalizado como fallback |
| Decorador @requires_role | Declarativo; middleware verifica antes de ejecutar ruta |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Token expirado en petición larga | Silent Refresh; retry con nuevo token |
| Keycloak caído | Healthcheck; mensaje claro en frontend |
