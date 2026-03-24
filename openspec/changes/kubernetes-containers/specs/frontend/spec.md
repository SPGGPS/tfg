# Frontend Spec: Kubernetes & Containers

## Ruta
`/cmdb/kubernetes` → `KubernetesPage.jsx`

## Sidebar
Bajo "Inventario" (submenu), añadir:
```
☸ Contenedores  →  /cmdb/kubernetes
```

## KubernetesPage.jsx — estructura

### Tab "Clusters K8s"
Tabla con columnas:
- Nombre + descripción (truncada)
- Proveedor (badge color: k3s=amber, kubeadm=blue, eks=orange, gke=green, aks=indigo, rke2=purple)
- Versión K8s (badge monospace azul)
- Nodos: badges `🎛 N CP` (indigo) + `⚙ N W` (blue) + `✕ N NotReady` (red, si hay)
- Pods: total + "(N crash)" en rojo si hay CrashLoopBackOff
- Helm releases: conteo
- Plugin de red: texto
- Acciones: "Ver activo →" navega a /assets/:id

Click en fila → modal `ClusterDetail`.

### Modal ClusterDetail — 5 tabs

**Nodos:**
- Nombre (monospace), Rol (Control Plane=indigo, Worker=blue), Estado (Ready=green, NotReady=red), Versión, IPs
- Filas CP con fondo indigo-50/20

**Pods:**
- Nombre (truncado), Namespace (monospace badge gris), Estado (Running=green, CrashLoopBackOff=red bold, Pending=amber, Completed=gris), Imagen(es), Nodo, Reinicios (>5=rojo, >0=amber)

**Deployments:**
- Nombre, Namespace, Réplicas "ready/total" (rojo si ready < replicas), Imagen

**Helm releases:**
- Release name, Namespace, Chart, Chart version, App version, Estado (deployed=green, failed=red, otros=amber)

**Info:**
- Grid 2 columnas con: Proveedor, Versión, Plugin red, Ingress, Container runtime, Storage class, IPs, Descripción

### Tab "Contenedores Docker"
Tabla con columnas:
- Nombre + descripción
- Imagen:tag (monospace)
- Estado (running=green, stopped=gray, exited=red, paused=amber)
- Runtime
- Host (link clickable a /assets/:host_asset_id)
- Puertos (max 3 badges monospace, "+N más")
- Compose project/service (monospace)
- Acciones: "Ver →"

## API
```javascript
cmdbApi.kubernetes(params) → GET /v1/cmdb/kubernetes
cmdbApi.containers(params) → GET /v1/cmdb/containers
```

## InventoryPage
Añadir `'k8s_cluster'` y `'container'` a `ASSET_TYPES`.
