id: login

context: |
  Feature: OIDC Authentication con Keycloak + RBAC
  Flujo: Authorization Code + PKCE
  En desarrollo: SKIP_AUTH=true inyecta usuario admin sin Keycloak

proposal: |
  1. Keycloak como IdP: Realm + Client PKCE + Role Mappers
  2. Backend: middleware JWT RS256 (JWKS), dependencias require_editor/require_admin
  3. Frontend: AuthContext con user, isAdmin, isEditor, isViewer
  4. SKIP_AUTH=true: inyecta {"sub":"dev-user","name":"Dev Admin","roles":["admin"]}

status: Implementado (SKIP_AUTH en docker-compose para dev)
