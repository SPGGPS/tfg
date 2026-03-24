# Backend - FastAPI (Audit Logs)

## ADDED Requirements

### Requirement: API REST en FastAPI con RBAC admin
El backend SHALL exponer una API REST en FastAPI que permita acceder a los logs de auditoría solo a usuarios con rol `admin`.

#### Scenario: Endpoint protegido
- **GIVEN** un token JWT válido con rol `admin`
- **WHEN** realiza GET /v1/audit-logs con filtros válidos
- **THEN** recibe HTTP 200 con los registros solicitados

#### Scenario: Acceso denegado sin rol admin
- **GIVEN** un token JWT válido sin rol `admin`
- **WHEN** realiza GET /v1/audit-logs
- **THEN** recibe HTTP 403 Forbidden

### Requirement: CORS seguro y configurable
El backend SHALL usar CORS configurable mediante la variable de entorno `CORS_ORIGINS` y permitir solicitudes desde el frontend.

#### Scenario: Petición CORS desde frontend
- **GIVEN** `CORS_ORIGINS` incluye `http://localhost:3000`
- **WHEN** el navegador hace una petición desde ese origen
- **THEN** la respuesta incluye los encabezados CORS necesarios y el navegador la acepta

### Requirement: Health check para probes
El backend SHALL exponer el endpoint `/v1/healthz` para liveness/readiness probes en Kubernetes.

#### Scenario: Health check
- **GIVEN** el servicio está activo
- **WHEN** se solicita GET /v1/healthz
- **THEN** responde HTTP 200 con JSON `{ "status": "ok" }`

### Requirement: Inmutabilidad de logs
Los registros de auditoría SHALL ser inmutables: no se expone ningún endpoint PUT/DELETE que modifique o elimine registros.

#### Scenario: No existe PUT/DELETE
- **GIVEN** la API está desplegada
- **WHEN** un cliente intenta usar PUT o DELETE sobre `/v1/audit-logs` o `/v1/audit-logs/{id}`
- **THEN** la API devuelve 405 Method Not Allowed o no expone esos endpoints

### Requirement: Secure Headers en respuestas HTTP
El backend SHALL incluir en todas las respuestas HTTP los headers de seguridad: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security` (cuando se sirva por HTTPS) y, si aplica, `Content-Security-Policy`.

#### Scenario: Respuesta con Secure Headers
- **GIVEN** un cliente que realiza cualquier petición a la API
- **WHEN** recibe la respuesta
- **THEN** los headers incluyen al menos X-Content-Type-Options y X-Frame-Options
