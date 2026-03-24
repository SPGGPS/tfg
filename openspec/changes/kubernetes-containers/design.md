# Diseño: Kubernetes Containers

## Objetivo
Implementar visibilidad completa de la infraestructura de contenedores (Kubernetes + Docker) en el Inventario Centralizado, consistente con el modelo polimórfico existente.

## Decisiones de diseño

### 1. Modelo polimórfico (no tabla separada)
**Decisión:** Los clusters K8s y contenedores son nuevos valores del enum `AssetType` en el modelo `Asset` existente, con campos específicos añadidos a la misma tabla.
**Alternativa descartada:** Tablas separadas `k8s_clusters`, `k8s_nodes`, `containers`.
**Motivo:** Consistencia con el patrón ya establecido (database, web_server, firewall). Permite usar el mismo endpoint `/v1/assets`, filtros, etiquetas, compliance, excepciones y auditoría sin cambios en la infraestructura.

### 2. Nodos como JSON (no FK relacional)
**Decisión:** `k8s_nodes` es un campo JSON con `{asset_id, name, role, status, version, ips}`. El `asset_id` referencia a assets existentes pero NO es una FK en base de datos.
**Alternativa descartada:** Tabla `k8s_node_assignments(cluster_id, asset_id, role)`.
**Motivo:** La arquitectura actual usa este patrón (lb_pool_members, k8s_helm_releases). Evita complejidad de migración y joins. El asset_id puede usarse en el frontend para navegar al activo.

### 3. Pods/Deployments/Helm como snapshots JSON
**Decisión:** Campos JSON actualizados en cada ingest, no entidades propias.
**Motivo:** Los pods son efímeros. No necesitan historial propio - el historial de cambios está en el snapshot del cluster (AssetHistory). Simplifica enormemente el modelo.

### 4. EOL para Kubernetes
**Decisión:** `k8s_version` (ej: "1.29.3") extrae "1.29" para buscar en ciclos del producto "kubernetes" de endoflife.date.
**Motivo:** Kubernetes tiene ciclo de vida estricto (N-3 minor versions soportadas, ~14 meses por versión). Es crítico saber si el cluster está en una versión EOL.

## Campos K8s Cluster
| Campo | Tipo | Descripción |
|-------|------|-------------|
| k8s_version | String(20) | Versión del cluster ("1.29.3") |
| k8s_provider | String(50) | kubeadm, k3s, eks, gke, aks, rke2, rancher |
| k8s_network_plugin | String(50) | cilium, calico, flannel, weave |
| k8s_ingress_class | String(50) | traefik, nginx, haproxy |
| k8s_container_runtime | String(50) | containerd, docker, cri-o |
| k8s_storage_class | String(100) | local-path, standard, longhorn |
| k8s_control_plane_count | Integer | Número de nodos control-plane |
| k8s_worker_count | Integer | Número de nodos worker |
| k8s_nodes | JSON | [{asset_id, name, role, status, version, ips}] |
| k8s_namespaces | JSON | ["default", "kube-system", ...] |
| k8s_pods | JSON | [{name, namespace, status, images, node, restarts}] |
| k8s_deployments | JSON | [{name, namespace, replicas, ready, image}] |
| k8s_helm_releases | JSON | [{name, namespace, chart, chart_version, app_version, status}] |

## Campos Container
| Campo | Tipo | Descripción |
|-------|------|-------------|
| container_runtime | String(50) | docker, containerd, podman |
| container_image | String(500) | Nombre de la imagen |
| container_image_tag | String(100) | Tag/versión ("1.25.3", "latest") |
| container_status | String(20) | running, stopped, exited, paused |
| container_ports | JSON | [{host_port, container_port, protocol}] |
| container_network | String(100) | bridge, host, overlay, none |
| container_volumes | JSON | [{source, target, type}] |
| container_compose_project | String(100) | Proyecto Docker Compose |
| container_compose_service | String(100) | Servicio en Docker Compose |
| host_asset_id | String (FK) | Servidor host (ya existente) |

## Riesgos
- Los snapshots JSON de pods/deployments quedan obsoletos si no se actualiza vía ingest automático
- Los asset_id en k8s_nodes pueden referir a assets que no existen (validación soft en UI)
