# Propuesta: Gestión de Contenedores Kubernetes y Docker

## ¿Qué?
Añadir soporte para dos nuevos tipos de activo en el inventario:
- **`k8s_cluster`** — Cluster Kubernetes con sus nodos (control-plane y workers), pods, deployments y releases Helm
- **`container`** — Contenedor Docker/OCI corriendo en una máquina física o virtual

## ¿Por qué?
El inventario actual cubre servidores, red, BBDD y aplicaciones, pero carece de visibilidad sobre la infraestructura de contenedores. En el Ayuntamiento de SSReyes se utiliza k3s en producción para el despliegue del Inventario Centralizado y otros servicios, así como contenedores Docker standalone en máquinas de gestión. Sin esta visibilidad, no se puede:
- Controlar qué versión de Kubernetes está en cada cluster y si está en EOL
- Saber qué contenedores corren en qué máquinas
- Gestionar el ciclo de vida (EOL) de la versión de Kubernetes

## Reglas de implementación

### Backend
- `k8s_cluster` es un nuevo AssetType con campos específicos en el modelo Asset (mismo patrón polimórfico que `database`, `web_server`, etc.)
- Los nodos del cluster se almacenan como JSON en `k8s_nodes`: `[{asset_id, name, role, status, version, ips}]`. El `asset_id` referencia assets existentes (server_physical o server_virtual).
- `k8s_pods`, `k8s_deployments`, `k8s_helm_releases` son snapshots JSON actualizables vía ingest
- EOL: `k8s_version` (ej: "1.29.3") matchea el producto `kubernetes` de endoflife.date usando ciclos X.Y (ej: "1.29")
- `container` usa el campo `host_asset_id` ya existente para referenciar el servidor host
- Nuevos endpoints CMDB: `GET /v1/cmdb/kubernetes` y `GET /v1/cmdb/containers`
- Tags automáticas: "Kubernetes" (#326CE5), "Container" (#0db7ed)

### Frontend
- Nueva página `/cmdb/kubernetes` con dos tabs: "Clusters K8s" y "Contenedores Docker"
- Los clusters muestran en tabla: nombre, proveedor (k3s/kubeadm/eks/gke/aks), versión K8s, conteo de nodos (CP + workers), pods, releases Helm, plugin de red
- Click en fila de cluster abre modal de detalle con 5 tabs: Nodos, Pods, Deployments, Helm releases, Info
- En la tab "Nodos": distingue visualmente control-plane (indigo) vs worker (azul), con estado (Ready/NotReady)
- En la tab "Helm": nombre release, namespace, chart, versiones, estado
- Contenedores muestran: nombre, imagen:tag, estado (running/stopped/exited/paused), runtime, host, puertos, compose project/service
- Sidebar: entrada "Contenedores" bajo "Inventario" (submenu)

### EOL
- Añadir producto `kubernetes` a la lista de seguimiento EOL
- Matching: `asset.k8s_version` → ciclo X.Y → producto "kubernetes" en endoflife.date
- Tags aplicadas: EOL KO (rojo), EOL WARN (naranja), EOL OK (verde) igual que el resto
- Endoflife.date tiene ciclos de Kubernetes con fechas de fin de soporte estándar (N-3 versiones soportadas)
