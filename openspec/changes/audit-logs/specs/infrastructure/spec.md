# Infraestructura - Kubernetes / Persistencia

## ADDED Requirements

### Requirement: Despliegue en Kubernetes con configuración segura
El sistema SHALL desplegarse en Kubernetes usando manifests declarativos. Las credenciales sensibles (JWT secret, password de Postgres) SHALL almacenarse en Secret.

#### Scenario: Despliegue básico
- **GIVEN** un clúster Kubernetes
- **WHEN** se aplica el manifest `k8s/backend-deployment.yaml` y `k8s/postgres-deployment.yaml`
- **THEN** se crean los pods para la API y PostgreSQL con la configuración de secretos

### Requirement: Monitorización de salud (readiness/liveness)
La API SHALL exponer `/v1/healthz` para probes y los manifests deberán configurar probes para liveness/readiness.

#### Scenario: Health check probes
- **GIVEN** el servicio está desplegado en Kubernetes
- **WHEN** el kubelet ejecuta liveness/readiness probes contra `/v1/healthz`
- **THEN** el endpoint responde HTTP 200 y el pod se considera healthy

### Requirement: Retención de logs a 180 días
El sistema SHALL eliminar registros de auditoría mayores a 180 días.

#### Scenario: Retención automática
- **GIVEN** que existen registros de auditoría con timestamp > 180 días
- **WHEN** el CronJob de retención se ejecuta (diariamente)
- **THEN** esos registros se eliminan sin intervención manual

### Requirement: Acceso seguro en navegador (CORS)
El backend SHALL configurar CORS para permitir orígenes configurables mediante variable `CORS_ORIGINS` y prevenir CSRF en navegadores.

#### Scenario: Cross-Origin request
- **GIVEN** una aplicación frontend en `http://localhost:3000`
- **WHEN** hace llamada a la API de auditoría
- **THEN** el navegador no bloquea la respuesta si `CORS_ORIGINS` incluye ese origen
