# Tasks: Applications, Services & Infrastructure Topology

## 1. Modelos y DB
- [x] 1.1 Enums: AppEnvironment, AppStatus, ServiceStatus, ServiceCriticality,
           ServiceCategory, ComponentRole, BindingTier, DepType, EndpointType
- [x] 1.2 TIER_ORDER dict y TIER_LABELS dict
- [x] 1.3 Modelo Application: name(unique), description, version, repo_url, docs_url,
           tech_stack(JSON), owner_team, environment, status, cell_id FK
- [x] 1.4 Modelo Service: name(unique), category, status, criticality, owner_team
- [x] 1.5 Modelo ServiceEndpoint: service_id FK, url, type, is_primary, certificate_id FK
           tls_status calculado consultando el Certificate
- [x] 1.6 Modelo ServiceComponent: service_id FK, application_id FK, role, order_index
- [x] 1.7 Modelo AppInfraBinding: communication_port (Integer, nullable) añadido. application_id FK, asset_id FK SET NULL,
           binding_tier, tier_order_override, is_critical, is_single_point_of_failure,
           redundancy_group, notes
           tier_order_effective = override ?? TIER_ORDER[binding_tier]
- [x] 1.8 Modelo AppDependency: source_app_id FK, target_app_id FK,
           CheckConstraint(source != target), dep_type, is_critical

## 2. Backend
- [x] 2.1 CRUD /v1/applications con search, status, environment
- [x] 2.2 POST/DELETE /v1/applications/{id}/infra-bindings
- [x] 2.3 POST/DELETE /v1/applications/{id}/dependencies
- [x] 2.4 CRUD /v1/services con endpoints y components
- [x] 2.5 GET /v1/services/{id}/dependency-graph y GET /v1/dependency-graph
- [x] 2.6 _build_graph(): nodos + aristas en cascada (tier ordenado secuencial)
- [x] 2.7 Aristas en cascada: App→Tier1→Tier2→Tier3 (no todas desde App)

## 3. Frontend
- [x] 3.1 ApplicationsPage con 3 tabs: Servicios | Aplicaciones | Mapa de Dependencias
         (Sidebar: "Servicios", título página: "Gestión de Servicios")
- [x] 3.2 CRUD Servicios y Aplicaciones en sus respectivos tabs
- [x] 3.3 Panel infraestructura: botón "🏗 Infraestructura" por fila → modal tabla-checklist
           Columnas: checkbox, nombre asset, tipo, IP, selector binding_tier
- [x] 3.4 Mapa SVG: layout por filas (tier_order), tooltip flotante en hover
           Tooltip: nombre, criticidad, entorno, versión, IP, tier, localización, SPF
           Tooltip ajustado para no salirse del SVG
- [x] 3.5 Tabs con texto negro: activo border-red-600 text-red-700, inactivo text-gray-500

## 5. Bugs resueltos

### BUG: CertificatesPage no cargaba (keepPreviousData)
TanStack Query v5 eliminó `keepPreviousData`. Sustituir por `placeholderData: (prev) => prev`.
Afectaba a: CertificatesPage.jsx, ApplicationsPage.jsx, InventoryPage.jsx

## 6. Seed de aplicaciones y servicios (init_db.py)

### Aplicaciones (6)
- [x] app-portal:  Portal Ciudadano Web (React+Nginx, producción, cell-rack-a)
- [x] app-api:     API Gateway Ciudadano (FastAPI, producción, cell-rack-a)
- [x] app-auth:    Keycloak SSO (Java+Keycloak, producción, cell-cpd-main)
- [x] app-erp:     ERP Municipal SAP S/4HANA (producción, cell-rack-a)
- [x] app-padron:  Padrón Municipal (Java+Spring Boot, producción, cell-rack-a)
- [x] app-staging: Portal Staging (React, staging, cell-cpd-main)

### Servicios (4) con endpoints y componentes
- [x] svc-portal: Portal Web Ciudadano — crítico — endpoints: www.ssreyes.org, portal.ssreyes.org (cert-001)
- [x] svc-sede:   Sede Electrónica — crítico — endpoint: sede.ssreyes.es (cert-002, CRÍTICO)
- [x] svc-erp:    ERP y Gestión Interna — alto — apps: ERP+Padrón
- [x] svc-infra:  Infraestructura Común — crítico — app: Keycloak (endpoint: keycloak.ssreyes.lan, cert expirado)

### Infra bindings con puertos (9 bindings)
- app-portal → router-edge-01 (entry_point, :443) → core-switch-01 (gateway, :443) → web-prod-01 (compute, :80)
- app-api    → api-vm-prod-01 (compute, :8000) → postgres-prod-01 (data, :5432)
- app-auth   → app-vm-staging-01 (compute, :8080) → postgres-prod-01 (data, :5432)
- app-erp    → db-prod-01 (compute, :443) → sqlserver-erp-01 (data, :1433)

### App dependencies (4)
- portal → api (calls_api), portal → auth (authenticates_via),
  api → auth (authenticates_via), padron → auth (authenticates_via)

## Bugs v1.0 — corregidos

### ServicesTab: ReferenceError services not defined
```jsx
// ❌ INCORRECTO: useEffect usa `services` antes de que esté definido
function ServicesTab() {
  const [detailSvc, setDetailSvc] = useState(null)
  useEffect(() => {
    if (services?.length) ...  // services no existe aún
  }, [services])
  const services = svcs?.data || []  // se define aquí, después del useEffect

// ✅ CORRECTO: definir services ANTES del useEffect
  const services = svcs?.data || []  // primero
  useEffect(() => {
    if (services.length) ...  // ahora sí existe
  }, [services.length])
```

### Aristas tier-to-tier especulativas eliminadas
Las líneas grises que conectaban assets entre sí de forma especulativa
(conectando al nodo más cercano del tier anterior) se eliminaron.
Ahora solo se renderizan las aristas reales del array `edges` del backend
(COMPOSED_OF, DEPENDS_ON, HOSTED_ON). Esto evita líneas incorrectas
cuando se filtra por un solo servicio.

## Fixes UI v1.1

### Bug: AppEnvironment.production en nodos del grafo
```python
# ❌ ANTES:
"environment": str(app.environment)  # → "AppEnvironment.production"
# ✅ DESPUÉS:
"environment": str(app.environment).split(".")[-1]  # → "production"
```
Afectaba al subText del nodo: mostraba "AppEnvironment.production · v2.1.0".

### Colores de capas de localización en el mapa SVG
Paleta rediseñada con colores vivos y distintos entre sí:
- rack → cian #06b6d4 (fill rgba(6,182,212,0.08))
- datacenter → naranja #f97316 (fill rgba(249,115,22,0.08))
- serverroom → esmeralda #10b981 (fill rgba(16,185,129,0.08))
- cabinet → violeta #8b5cf6 (fill rgba(139,92,246,0.08))

Los iconos en el selector de celda del formulario de apps coinciden:
▤ = rack, ⬜ = datacenter, ▦ = serverroom, ▣ = cabinet

### Dashboard: excepciones morado → azul
- ko_with_exception: #7c3aed → #0369a1 (azul océano)
- ok_with_exception: #1d4ed8 → #2563eb (azul brillante)
- KpiCard excepciones: #7c3aed → #2563eb
- Toda la app unificada en tonos azules para excepciones

## Fixes v1.2 — Paleta definitiva del mapa de dependencias

### Colores NODE_STYLES — versión definitiva con hues radicalmente distintos

Cada tier usa un HUE completamente diferente para máxima diferenciación visual:

```js
const NODE_STYLES = {
  service:     { fill:'#1e3a8a', border:'#93c5fd', label:'#bfdbfe' },  // azul rey
  application: { fill:'#064e3b', border:'#6ee7b7', label:'#a7f3d0' },  // esmeralda
  compute:     { fill:'#7c2d12', border:'#fb923c', label:'#fed7aa' },  // naranja quemado
  data:        { fill:'#164e63', border:'#22d3ee', label:'#a5f3fc' },  // cian
  cache:       { fill:'#713f12', border:'#fbbf24', label:'#fef08a' },  // ámbar
  storage:     { fill:'#500724', border:'#f472b6', label:'#fbcfe8' },  // rosa/fucsia
  network:     { fill:'#14532d', border:'#84cc16', label:'#d9f99d' },  // lima
  auth:        { fill:'#3b0764', border:'#c084fc', label:'#e9d5ff' },  // violeta
  default:     { fill:'#1e293b', border:'#94a3b8', label:'#cbd5e1' },  // slate
}
```

Cada nodo tiene además una **franja de acento superior** (8px) con el color del borde
para reforzar la identidad visual del tier incluso a pequeño tamaño.

El subtítulo del nodo usa el color `label` del tier (tono pastel) en lugar de blanco,
proporcionando contexto visual sin competir con el nombre principal.

### Labels de localización — legibilidad mejorada
Fondo de etiquetas: `rgba(0,0,0,0.6)` (antes 0.4)  
Texto: `white` a 9px (antes color del tier a 7.5px)  
Mayor contraste → legible sobre cualquier fondo de contenedor.

## Edición de infra-bindings v1.3

### PUT /v1/applications/{app_id}/infra-bindings/{bid}

Nuevo endpoint para editar un binding existente sin borrarlo y recrearlo.

```python
class BindingUpdate(BaseModel):
    binding_tier: Optional[BindingTier] = None
    tier_order_override: Optional[int] = None
    is_critical: Optional[bool] = None
    is_single_point_of_failure: Optional[bool] = None
    redundancy_group: Optional[str] = None
    communication_port: Optional[int] = None
    notes: Optional[str] = None
```

Solo se actualizan los campos enviados. `asset_id` no es editable (borrar y recrear si se cambia el asset).

### Frontend — modal de edición de binding

Botón ✎ (lápiz) en cada chip de binding, visible en hover solo para editor/admin.
Al pulsar abre modal con: selector de tier (mismos chips del formulario de creación),
campo de puerto, grupo de redundancia, orden en tier, checkboxes is_critical/SPF, notas.

### communication_port en el mapa de dependencias

**Nodo del asset**: el subText muestra `tier · IP :puerto` (ej: `compute · 10.0.1.50 :5432`)

**Arista HOSTED_ON**: el label incluye el puerto si existe (ej: `hosted on :5432`)

**Nodo en el grafo** recibe campos adicionales: `communication_port`, `notes`, `redundancy_group`

### Capa de red — fila separada

La capa `network` (switches, routers) ahora ocupa la fila 8 en el layout del grafo,
separada de `storage` (fila 7). Así los contenedores de localización pueden
envolver los activos de red correctamente sin solaparse con storage.

Label: "Red · Switches" (antes compartía "Almacenamiento · Red")
