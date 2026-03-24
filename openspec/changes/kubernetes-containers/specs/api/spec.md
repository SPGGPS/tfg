# API Spec: Kubernetes & Containers

## Endpoints

### GET /v1/cmdb/kubernetes
Lista clusters Kubernetes.

**Query params:**
- `provider` (optional): k3s, kubeadm, eks, gke, aks, rke2
- `k8s_version` (optional): filtro por versión
- `search` (optional): búsqueda en nombre, proveedor, versión
- `page` / `page_size` (1-200, default 50)

**Response 200:**
```json
{
  "data": [{
    "id": "uuid",
    "name": "k8s-prod-01",
    "type": "k8s_cluster",
    "k8s_version": "1.29.3",
    "k8s_provider": "k3s",
    "k8s_network_plugin": "cilium",
    "k8s_ingress_class": "traefik",
    "k8s_container_runtime": "containerd",
    "k8s_storage_class": "local-path",
    "k8s_control_plane_count": 1,
    "k8s_worker_count": 3,
    "k8s_nodes": [{"asset_id": "...", "name": "worker-01", "role": "worker", "status": "Ready", "version": "v1.29.3", "ips": ["10.10.0.11"]}],
    "k8s_namespaces": ["default", "kube-system"],
    "k8s_pods": [{"name": "app-xxx", "namespace": "default", "status": "Running", "images": ["nginx:1.25"], "node": "worker-01", "restarts": 0}],
    "k8s_deployments": [{"name": "app", "namespace": "default", "replicas": 2, "ready": 2, "image": "nginx:1.25"}],
    "k8s_helm_releases": [{"name": "app", "namespace": "default", "chart": "my-chart", "chart_version": "1.0.0", "app_version": "1.0.0", "status": "deployed"}],
    "tags": [],
    "exceptions": []
  }],
  "total": 2,
  "page": 1,
  "page_size": 50
}
```

### GET /v1/cmdb/containers
Lista contenedores Docker/OCI.

**Query params:**
- `runtime` (optional): docker, containerd, podman
- `status` (optional): running, stopped, exited, paused
- `host_asset_id` (optional): UUID del servidor host
- `search` (optional): búsqueda en nombre, imagen, compose project
- `page` / `page_size`

**Response 200:** igual que kubernetes pero con campos `container_*` en lugar de `k8s_*`.

## EOL Matching (producto: "kubernetes")
- `asset.type == "k8s_cluster"` AND `asset.k8s_version` → extrae ciclo X.Y → busca en eol_cycles del producto "kubernetes"
- Ejemplo: k8s_version="1.29.3" → ciclo="1.29" → eol_status="warning" (si < 1 año para EOL)
- Tags aplicadas automáticamente: EOL KO / EOL WARN / EOL OK
