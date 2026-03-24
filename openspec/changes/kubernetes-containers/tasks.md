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
- [x] Añadir datos de ejemplo en seed_assets.py (2 clusters + 2 contenedores)

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

## OpenSpec (2h)
- [x] Crear change kubernetes-containers con proposal, design, tasks, specs
