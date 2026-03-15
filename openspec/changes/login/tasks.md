# Tasks: Login

## 1. Keycloak

- [ ] 1.1 Configurar Realm, Client (PKCE) y Role Mappers
- [ ] 1.2 Mappers: roles en ID Token y Access Token

## 2. Backend

- [ ] 2.1 Middleware JWT: validar firma (JWKS), iss, aud, azp
- [ ] 2.2 Extractor de roles y decorador @requires_role

## 3. Frontend

- [ ] 3.1 Flujo PKCE y login centralizado en Keycloak
- [ ] 3.2 Componente ProtectedRoute y routing por roles
- [ ] 3.3 Silent Refresh para sesión activa

## 4. Infra

- [ ] 4.1 Helm: Keycloak HA, Client ID, Realm URL en values
- [ ] 4.2 NetworkPolicies: Backend → Keycloak para JWKS
