# Frontend - Auth UI (React + Keycloak)

## ADDED Requirements

### Requirement: Componente de login con Keycloak
El frontend SHALL implementar el flujo OpenID Connect Authorization Code + PKCE usando Keycloak.

#### Scenario: Login exitoso
- **GIVEN** un usuario con credenciales válidas
- **WHEN** completa el login en Keycloak
- **THEN** la app recibe tokens y redirige al dashboard

### Requirement: Manejo seguro de tokens
El frontend SHALL almacenar tokens en cookie HttpOnly/Secure y usar refresh token para renovar acceso.

#### Scenario: Refresh automático
- **GIVEN** un token de acceso cercano a expirar
- **WHEN** la aplicación detecta expiración
- **THEN** utiliza el refresh token para obtener uno nuevo sin pedir login al usuario
