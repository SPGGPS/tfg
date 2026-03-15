# Auth - OIDC y Keycloak

## ADDED Requirements

### Requirement: Autenticación OIDC con Keycloak

El sistema SHALL utilizar OpenID Connect (Authorization Code Flow con PKCE) con Keycloak como IdP.

#### Scenario: Redirección a Keycloak para login
- **GIVEN** un usuario no autenticado
- **WHEN** intenta acceder a una ruta protegida
- **THEN** es redirigido al login de Keycloak

### Requirement: Roles en JWT

El backend SHALL validar el JWT (RS256) y extraer los roles del claim para autorización.

#### Scenario: Middleware de autorización por rol
- **GIVEN** un JWT con rol 'admin'
- **WHEN** el usuario accede a una ruta que requiere rol admin
- **THEN** la petición es autorizada

#### Scenario: Acceso denegado por rol insuficiente
- **GIVEN** un JWT con rol 'viewer'
- **WHEN** el usuario intenta una acción que requiere rol 'admin'
- **THEN** la petición recibe 403 Forbidden

### Requirement: Protección de rutas en React

El frontend SHALL usar un componente ProtectedRoute que verifique roles antes de renderizar.

#### Scenario: Renderizado condicional por rol
- **GIVEN** un usuario con rol 'editor'
- **WHEN** la ruta requiere roles ['admin', 'editor']
- **THEN** el contenido se renderiza correctamente
