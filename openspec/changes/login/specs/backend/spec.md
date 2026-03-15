# Backend - Auth (Keycloak / JWT Validation)

## ADDED Requirements

### Requirement: Validación de JWT RS256
El backend SHALL validar JWT firmados con RS256 usando la JWKS de Keycloak.

#### Scenario: JWT válido
- **GIVEN** un token JWT válido firmado por Keycloak
- **WHEN** el backend recibe una petición con Authorization: Bearer
- **THEN** la petición se autoriza y se extraen roles

#### Scenario: JWT inválido o expirado
- **GIVEN** un token JWT expirado o manipulado
- **WHEN** se usa para acceder a un endpoint protegido
- **THEN** el backend responde 401 Unauthorized

### Requirement: Endpoints de token / sesión
El backend SHALL exponer un endpoint para refrescar tokens (refresh) y obtener datos del usuario.

#### Scenario: Refresh token
- **GIVEN** un refresh token válido
- **WHEN** el cliente solicita refresh
- **THEN** el backend devuelve nuevos tokens de acceso y refresh
