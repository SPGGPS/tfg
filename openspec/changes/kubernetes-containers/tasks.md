# Tareas: Kubernetes Containers

## Backend (8h)
- [x] Añadir AssetType.k8s_cluster y AssetType.container al enum
- [x] Añadir campos k8s_* y container_* al modelo Asset
- [x] Actualizar to_dict() para incluir nuevos campos
- [x] Actualizar apply_auto_tags() para nuevos tipos ("Kubernetes", "Container")
- [x] Actualizar apply_eol_tags() para k8s_version → kubernetes
- [x] Actualizar _asset_matches_product() en eol.py para kubernetes
- [x] Actualizar _eol_status_for_asset_and_product() en eol.py para k8s_version
- [x] Añadir GET /v1/cmdb/kubernetes
- [x] Añadir GET /v1/cmdb/containers
- [x] Seed enriquecido: 3 clusters + 5 contenedores (ver sección Datos de ejemplo)
- [x] Actualizar check seed_if_empty para detectar ausencia de k8s_cluster/container

## Frontend (12h)
- [x] Crear KubernetesPage.jsx con tabs Clusters/Contenedores
- [x] Tab Clusters: tabla con nodos (CP+workers), pods, helm, red
- [x] Modal detalle cluster con 5 tabs (Nodos, Pods, Deployments, Helm, Info)
- [x] Tab Contenedores: tabla con imagen, estado, host, puertos, compose
- [x] Añadir "Contenedores" al sidebar bajo Inventario
- [x] Añadir ruta /cmdb/kubernetes en main.jsx
- [x] Añadir cmdbApi.kubernetes() y cmdbApi.containers() en api.js
- [x] Actualizar ASSET_TYPES en InventoryPage.jsx

## EOL (2h)
- [x] Añadir producto "kubernetes" a endoflife.date (manual desde UI EOL)
- [x] Verificar matching k8s_version → ciclo "1.29" → eol_status
- [x] Cluster legacy EOL KO (1.26 fuera de soporte) visible en UI

## OpenSpec (2h)
- [x] Crear change kubernetes-containers en changes-v2/
- [x] Mover de changes/ a changes-v2/ (schema openspec/v2)

---

## Datos de ejemplo implementados

### Clusters Kubernetes

| ID | Nombre | Proveedor | Versión | CPs | Workers | EOL |
|----|--------|-----------|---------|-----|---------|-----|
| asset-k8s-prod   | k8s-ssreyes-prod | k3s     | 1.29.3  | 1 | 3 | OK   |
| asset-k8s-dev    | k8s-ssreyes-dev  | kubeadm | 1.28.7  | 1 | 2 | WARN |
| asset-k8s-legacy | k8s-legacy-erp   | kubeadm | 1.26.12 | 3 | 5 | KO   |

**k8s-ssreyes-prod** (k3s 1.29, cilium, traefik, longhorn):
- 14 pods: inventario ×2 backend/frontend, postgres, redis, keycloak, prometheus, grafana, alertmanager, traefik, cert-manager, longhorn ×2
- 5 deployments, 7 helm releases (inventario, kube-prometheus, traefik, cert-manager, longhorn, keycloak, redis)
- 1 worker NotReady (worker-03)

**k8s-ssreyes-dev** (kubeadm 1.28, calico, nginx):
- 6 pods: dev/staging inventario, postgres-dev, gitlab-runner
- 1 pod CrashLoopBackOff (inventario-stg-backend, 18 reinicios)
- 1 pod Pending (inventario-stg-frontend, sin recursos disponibles)
- Helm release inventario-staging con status "failed"

**k8s-legacy-erp** (kubeadm 1.26 HA 3 CPs, flannel, nginx, nfs-client):
- 3 control-planes + 5 workers (1 NotReady, versión v1.26.11 desactualizada)
- 8 pods: SAP connector ×2, ERP API, Hacienda, Padrón ×2, Velero backup
- 4 deployments, 5 helm releases

### Contenedores Docker

| ID | Nombre | Imagen | Estado | Host |
|----|--------|--------|--------|------|
| asset-ct-nginx-gw      | nginx-gateway-prod         | nginx:1.25.4                  | running | vm-proxy-prod-01  |
| asset-ct-portainer     | portainer-mgmt             | portainer/portainer-ce:2.20.3 | running | vm-monitoring-01  |
| asset-ct-redis         | redis-cache-prod           | redis:7.2.4-alpine            | running | vm-api-prod-01    |
| asset-ct-zabbix-proxy  | zabbix-proxy-anexo         | zabbix-proxy-sqlite3:6.4      | stopped | vm-monitoring-01  |
| asset-ct-keycloak-old  | keycloak-standalone-legacy | keycloak/keycloak:22.0.5      | exited  | vm-sso-01         |

Los contenedores `stopped` y `exited` ilustran el estado real de infraestructura: el Zabbix Proxy está caído por pérdida de conectividad y el Keycloak legacy fue migrado al cluster k8s-prod pero el contenedor persiste sin limpiar.
