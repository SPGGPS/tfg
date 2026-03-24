# Infraestructura - Kubernetes / Persistencia

## ADDED Requirements

### Requirement: Despliegue en Kubernetes con Helm Chart
El sistema SHALL desplegarse en Kubernetes usando el Helm Chart `inventario-centralizado`. Todos los recursos SHALL pertenecer al namespace `inventory-ssreyes`. Las credenciales sensibles (DATABASE_URL, JWT_SECRET) SHALL almacenarse en un Secret de Kubernetes. La configuración no sensible (KEYCLOAK_URL, CORS_ORIGINS, SKIP_AUTH) SHALL almacenarse en un ConfigMap.

#### Scenario: Despliegue con Helm
- **GIVEN** un clúster k3s con Traefik y Cilium
- **WHEN** se ejecuta `helm install inventario ./helm/inventario-centralizado -n inventory-ssreyes --create-namespace`
- **THEN** se crean todos los pods en el namespace `inventory-ssreyes` con la configuración de secretos

---

### Requirement: Ingress con Traefik (k3s nativo)
El frontend SHALL ser accesible externamente a través del IngressController Traefik que viene preinstalado en k3s. Se usará un recurso `Ingress` estándar de Kubernetes con `ingressClassName: traefik`. No se requiere instalar ningún IngressController adicional.

#### Scenario: Acceso al frontend vía Traefik
- **GIVEN** k3s con Traefik instalado
- **WHEN** se aplica el Ingress con host configurado en values.yaml
- **THEN** el frontend es accesible en `http://<host>` sin configuración adicional

---

### Requirement: NetworkPolicies con Cilium — puertos explícitos en ambos sentidos
Cilium actúa como CNI y como motor de NetworkPolicy. Las políticas deben declarar los puertos **en ambos lados** (ingress del destino Y egress del origen) para que Cilium las aplique correctamente.

Política base: deny-all en el namespace `inventory-ssreyes`.

Allows explícitos requeridos:

| Origen | Destino | Puerto | Protocolo |
|--------|---------|--------|-----------|
| Traefik (kube-system) | frontend pod | 80 | TCP |
| frontend pod | backend pod | 8000 | TCP |
| backend pod | postgres pod | 5432 | TCP |
| backend pod | keycloak pod | 8080 | TCP |
| CronJob pods | backend pod | 8000 | TCP |
| CronJob pods | postgres pod | 5432 | TCP |
| backend pod | DNS (kube-system) | 53 | UDP |
| todos los pods | kube-apiserver | 443 | TCP |

Cada NetworkPolicy SHALL declarar:
- `podSelector` con etiqueta del pod destino
- `ingress.from` con `podSelector` o `namespaceSelector` del origen
- `ingress.ports` con el puerto y protocolo exactos
- La política de egress del pod origen SHALL incluir el puerto destino en `egress.ports`

#### Scenario: Backend puede conectar a Postgres
- **GIVEN** Cilium aplicando deny-all en inventory-ssreyes
- **WHEN** el pod backend intenta conectar al pod postgres en puerto 5432
- **THEN** la conexión es permitida porque existe NetworkPolicy con egress en backend (5432) e ingress en postgres (5432 from backend)

#### Scenario: Frontend no puede conectar a Postgres directamente
- **GIVEN** Cilium aplicando las NetworkPolicies
- **WHEN** el pod frontend intenta conectar al pod postgres en puerto 5432
- **THEN** la conexión es denegada por no existir allow entre frontend y postgres

---

### Requirement: Monitorización de salud (readiness/liveness)
La API SHALL exponer `/v1/healthz` para probes. Los Deployments de backend SHALL configurar liveness y readiness probes contra ese endpoint.

#### Scenario: Health check probes
- **GIVEN** el backend desplegado en Kubernetes
- **WHEN** el kubelet ejecuta liveness/readiness probes
- **THEN** el endpoint `/v1/healthz` responde HTTP 200

---

### Requirement: CronJobs en namespace inventory-ssreyes
Los CronJobs SHALL desplegarse en el mismo namespace `inventory-ssreyes` con sus propias NetworkPolicies que permitan acceso a backend (8000) y postgres (5432) según necesidad.

| CronJob | Schedule | Acceso necesario |
|---------|----------|-----------------|
| snapshot-history | `0 * * * *` | backend:8000 |
| purge-audit | `0 2 * * *` | postgres:5432 |
| purge-history | `0 3 * * *` | postgres:5432 |
| expire-exceptions | `0 1 * * *` | postgres:5432 |

---

### Requirement: Retención de logs a 180 días
El CronJob `purge-audit` eliminará registros de audit_logs mayores de 180 días diariamente a las 02:00.

---

### Requirement: PVC para avatares
El backend SHALL montar un PersistentVolumeClaim `avatars-pvc` en `/tmp/avatars` para que los avatares de usuario persistan entre reinicios del pod.

---

### Requirement: Acceso CORS
El backend SHALL configurar CORS con los orígenes definidos en ConfigMap (`CORS_ORIGINS`). En k3s local el valor por defecto será el host configurado en el Ingress de Traefik.

---

### Requirement: docker-compose.yml — puerto externo PostgreSQL en 5433

El `docker-compose.yml` usa `ports: ["5433:5432"]` para el contenedor de PostgreSQL. El puerto externo es `5433` (no `5432`) para evitar conflicto con instalaciones locales de PostgreSQL en la máquina del desarrollador (`Bind for 0.0.0.0:5432 failed: port is already allocated`).

La comunicación interna entre contenedores sigue usando `postgres:5432` — solo cambia el binding del host.

```yaml
postgres:
  ports: ["5433:5432"]  # ← 5433 externo para evitar conflicto
```

Para conectar con cliente externo: `localhost:5433`, usuario `inventario`, password `inventario_secret`, db `inventario`.

#### Scenario: Arranque sin conflicto de puerto
- **GIVEN** el host tiene PostgreSQL local corriendo en 5432
- **WHEN** `docker-compose up`
- **THEN** el contenedor postgres arranca correctamente usando el puerto externo 5433
