id: login

# openspec/changes/login/.openspec.yaml
schema: spec-driven
created: 2026-03-14

# Contexto específico: Autenticación Delegada con RBAC
context: |
  Feature: OIDC Authentication with Keycloak & RBAC
  System: React (OIDC Client) <-> Keycloak (IdP) <-> FastAPI (Resource Server)
  Infrastructure: Keycloak en K8s con Postgres HA.
  Protocol: OpenID Connect (Authorization Code Flow with PKCE).
  Authorization: Roles de aplicación mapeados en el JWT (App Roles).

# Definición del Cambio (The "What")
proposal: |
  Sustituir la autenticación local por un flujo de identidad centralizado y enriquecido:
  1. Keycloak: Configurado como IdP con un Realm específico y "Client Scopes" para roles.
  2. Frontend: React gestiona el login y extrae los roles del token para renderizado condicional.
  3. Backend: FastAPI valida el JWT (RS256) y verifica los permisos basados en los roles del claim.
  4. Infra: Configuración de Keycloak Mappers para incluir roles en el ID Token y Access Token.

# Reglas de implementación actualizadas
rules:
  openapi_spec:
    - Definir 'securitySchemes' con tipo 'openIdConnect' apuntando a la URL del Realm.
    - Los scopes requeridos deben incluir: 'openid', 'profile', 'email' y 'roles'.
  backend_code:
    - No gestionar contraseñas; validación de firma mediante JWKS.
    - Implementar extractor de roles: buscar en 'resource_access.${client_id}.roles' o claim personalizado.
    - Middleware de autorización: Decoradores para proteger rutas según el rol (ej. @requires_role('admin')).
    - Verificación estricta de 'iss', 'aud' y 'azp' (authorized party).
  frontend_code:
    - Implementar flujo PKCE.
    - Login centralizado en SSO de Keycloak.
    - Protección de rutas en React: Componente <ProtectedRoute roles={['user', 'admin']} />.
    - Gestión de Silent Refresh para mantener la sesión activa.
  k8s_manifests:
    - Helm Chart: Incluir Client ID, Realm URL y Application Role Mappings en values.yaml.
    - NetworkPolicies: Permitir tráfico de salida del Backend a Keycloak para validación de certificados.

# Desglose de tareas técnicas
tasks:
  - name: "Configure Keycloak: Realm, Client (PKCE) and Role Mappers"
    hours: 3
  - name: "Update OpenSpec: Include OIDC Discovery and Role Scopes"
    hours: 1
  - name: "Implement FastAPI Middleware: JWT Validation + RBAC Role Checker"
    hours: 4
  - name: "React Integration: OIDC Context + Role-based Routing"
    hours: 3
  - name: "Helm Deployment: Keycloak HA + App Config with Role Vars"
    hours: 4
