# Tasks: Infrastructure

## 1. Docker Compose
- [x] 1.1 PostgreSQL 16-alpine, puerto externo 5433 (evita conflicto con Postgres local)
- [x] 1.2 Backend con SKIP_AUTH=true, healthcheck, espera a postgres
- [x] 1.3 Frontend con VITE_SKIP_AUTH=true, multi-stage build

## 2. Helm Chart
- [x] 2.1 backend.yaml: Deployment + Service + ConfigMap + Secret
- [x] 2.2 frontend.yaml: Deployment + Service + Ingress Traefik
- [x] 2.3 postgres.yaml: StatefulSet + PVC + Service
- [x] 2.4 hpa.yaml: backend max 3 replicas, frontend max 2
- [x] 2.5 network-policies.yaml: deny-all + allows explícitos Cilium
- [x] 2.6 cronjobs.yaml: snapshot horario + purgas

## 3. NetworkPolicies (Cilium)
Regla: declarar puertos en AMBOS sentidos (egress origen + ingress destino)
| Origen | Destino | Puerto |
|--------|---------|--------|
| frontend | backend | 8000 |
| backend | postgres | 5432 |
| backend | keycloak | 8080/443 |
| traefik | frontend | 8080 |

## 4. Bugs conocidos
- BUG: Puerto 5432 ocupado → usar puerto externo 5433 en docker-compose
- BUG: Caché Docker → siempre usar --no-cache: docker compose build --no-cache
