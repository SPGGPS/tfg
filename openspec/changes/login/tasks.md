# Tasks: Login

## 1. Keycloak (pendiente en producción)
- [ ] 1.1 Configurar Realm, Client PKCE, Role Mappers
- [ ] 1.2 Roles en ID Token y Access Token

## 2. Backend
- [x] 2.1 middleware/auth.py: valida JWT RS256 con JWKS si SKIP_AUTH=false
- [x] 2.2 Con SKIP_AUTH=true: inyecta usuario ficticio admin
- [x] 2.3 require_editor y require_admin como dependencias FastAPI

## 3. Frontend
- [x] 3.1 AuthContext.jsx: user, isAdmin, isEditor, isViewer
- [x] 3.2 Rutas del sidebar filtradas por rol
- [x] 3.3 Con VITE_SKIP_AUTH=true: usuario ficticio en contexto

## 4. Infra
- [x] 4.1 SKIP_AUTH=true en docker-compose.yml (desarrollo)
- [ ] 4.2 Helm: Keycloak HA, Client ID, Realm URL en values
