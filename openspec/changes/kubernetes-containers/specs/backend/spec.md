# Backend Spec: Kubernetes & Containers

## Modelo Asset — nuevos tipos y campos

### AssetType (enum)
```python
k8s_cluster = "k8s_cluster"  # Cluster Kubernetes completo
container   = "container"    # Contenedor Docker/OCI standalone
```

### Campos k8s_cluster
Todos nullable. Añadidos a la tabla `assets` (mismo patrón polimórfico).

```python
k8s_version           = Column(String(20),  nullable=True)
k8s_provider          = Column(String(50),  nullable=True)
k8s_network_plugin    = Column(String(50),  nullable=True)
k8s_ingress_class     = Column(String(50),  nullable=True)
k8s_container_runtime = Column(String(50),  nullable=True)
k8s_storage_class     = Column(String(100), nullable=True)
k8s_control_plane_count = Column(Integer,  nullable=True)
k8s_worker_count      = Column(Integer,    nullable=True)
k8s_nodes             = Column(JSON,        nullable=True)
k8s_namespaces        = Column(JSON,        nullable=True)
k8s_pods              = Column(JSON,        nullable=True)
k8s_deployments       = Column(JSON,        nullable=True)
k8s_helm_releases     = Column(JSON,        nullable=True)
```

### Campos container
```python
container_runtime         = Column(String(50),  nullable=True)
container_image           = Column(String(500), nullable=True)
container_image_tag       = Column(String(100), nullable=True)
container_status          = Column(String(20),  nullable=True)
container_ports           = Column(JSON,        nullable=True)
container_network         = Column(String(100), nullable=True)
container_volumes         = Column(JSON,        nullable=True)
container_compose_project = Column(String(100), nullable=True)
container_compose_service = Column(String(100), nullable=True)
# host: usa host_asset_id ya existente en Asset
```

## Tagging automático
```python
SYSTEM_TAGS["Kubernetes"] = "#326CE5"
SYSTEM_TAGS["Container"]  = "#0db7ed"

type_map[AssetType.k8s_cluster] = "Kubernetes"
type_map[AssetType.container]   = "Container"
```

## EOL matching
```python
# apply_eol_tags: añadir candidato kubernetes
k8s_ver = getattr(asset, 'k8s_version', None)
if k8s_ver and asset_type_str == 'k8s_cluster':
    m = re.search(r"(\d+\.\d+)", k8s_ver)
    if m:
        candidates.append(("kubernetes", m.group(1)))

# _asset_matches_product: reconocer kubernetes
if product_id == "kubernetes":
    if getattr(asset, 'k8s_version', None) and asset_type_str == 'k8s_cluster':
        return True
```

## CMDB Endpoints
```
GET /v1/cmdb/kubernetes  → list_kubernetes()
GET /v1/cmdb/containers  → list_containers()
```
Ambos usan `_enrich(assets, db)` igual que los otros endpoints CMDB.
