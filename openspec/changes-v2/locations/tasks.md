# Tasks: Localizaciones físicas

## 1. Modelos y DB
- [x] 1.1 Modelo Zone: id, name, description, created_at, updated_at
- [x] 1.2 Modelo Site: id, zone_id FK CASCADE, name, address, description
- [x] 1.3 Modelo Cell: id, site_id FK CASCADE, name, cell_type, row_id, rack_unit, description
- [x] 1.4 Cell.to_dict() incluye full_path: "Zona › Site › Cell"
- [x] 1.5 FK cell_id en Asset (SET NULL)
- [x] 1.6 FK cell_id en Application (SET NULL)

## 2. Backend
- [x] 2.1 GET /v1/locations/tree — árbol completo anidado
- [x] 2.2 CRUD /v1/zones — GET, POST, PUT/{id}, DELETE/{id}
- [x] 2.3 CRUD /v1/sites — GET?zone_id=, POST, PUT/{id}, DELETE/{id}
- [x] 2.4 CRUD /v1/cells — GET?site_id=, POST, PUT/{id}, DELETE/{id}
- [x] 2.5 GET /v1/cells/{id}/assets — activos asignados a esta celda
- [x] 2.6 POST /v1/cells/bulk-assign — DECLARADO ANTES DE /{cell_id} en el router
- [x] 2.7 IntegrityError → HTTP 409 con mensaje legible (no 500)
- [x] 2.8 Validar que zone_id y site_id existan → 404 si no

## 3. Frontend
- [x] 3.1 LocationsPage /locations — solo admin
- [x] 3.2 Árbol visual: Zone > Site > Cell con iconos y contadores
- [x] 3.3 Botones en cabecera: [+ Zona (btn-primary)] [+ Localización] [+ Celda]
- [x] 3.4 CRUD modal para cada nivel con sus formularios
- [x] 3.5 BulkAssignModal: lista de assets con checkboxes, búsqueda, desvincular individual
- [x] 3.6 locationsApi en api.js con métodos: listZones, createZone, updateZone, deleteZone,
           listSites, createSite, updateSite, deleteSite, listCells, createCell, updateCell,
           deleteCell, cellAssets, bulkAssign

## 4. Bugs resueltos en este change

### BUG: "No mutationFn found" al crear zona
Causa: api.js tenía la versión antigua de locationsApi (modelo Location autorreferenciado).
locationsApi.createZone era undefined → useMutation({ mutationFn: undefined }) falla en v5.
Solución: reescribir locationsApi con todos los métodos Zone/Site/Cell.

### BUG: "No mutationFn found" secundario (TanStack v5)
Pasar .mutate directamente como prop pierde el contexto en v5.
```jsx
// ❌
<Form onSubmit={createZoneMut.mutate}/>
// ✅
<Form onSubmit={d => createZoneMut.mutate(d)}/>
```

### BUG: BulkAssignModal con hooks inestables
Renderizar condicionalmente {modal?.data && <BulkAssignModal/>} viola Rules of Hooks
cuando React alterna entre distintos tipos de modal.
Solución: siempre montar el componente con cell dummy + guard isReal:
```jsx
<BulkAssignModal cell={modal?.data || {id: "__none__", name: ""}} onClose={...}/>
// Dentro:
const isReal = cell?.id && cell.id !== "__none__"
useQuery({ ..., enabled: isReal })
if (!isReal) return null
```

## 5. Seed de localizaciones (init_db.py)

- [x] 5.1 Zona: "Ayuntamiento San Sebastián de los Reyes"
- [x] 5.2 Site: "Edificio Principal" (Plaza de la Constitución s/n)
           Cells: CPD Principal (datacenter), Rack A (rack, Fila A, U1-U42), Rack Red (rack, Fila B, U1-U24)
- [x] 5.3 Site: "Edificio Anexo" (C/ Cervantes 12)
           Cell: CPD Backup (datacenter)
- [x] 5.4 Todos los assets tienen cell_id asignado en el seed (no null)

### Seed confirmado — assets asignados a cells
- cell-rack-a:    web-prod-01, db-prod-01, api-vm-prod-01, postgres-prod-01, sqlserver-erp-01
- cell-rack-b:    core-switch-01, access-switch-02, router-edge-01
- cell-cpd-main:  app-vm-staging-01, ap-office-floor2

## 6. Mapa de servicios — contenedores jerárquicos Zona > CPD > Rack

El componente SVG del mapa de dependencias renderiza 3 capas de contenedores:

**Layer 1 (cell)** — Rack/datacenter individual
- rx=10, strokeDasharray="5,3"
- Colores: rack=azul #3b82f6, datacenter=índigo #6366f1, serverroom=cyan #06b6d4
- Etiqueta: icono + cell_name · row_id · rack_unit (si existen)

**Layer 2 (site)** — Edificio / CPD
- rx=14, strokeDasharray="8,4", stroke=#334155 muy sutil
- Etiqueta: 🏢 + site_name

**Layer 3 (zone)** — Zona municipal / organización
- rx=18, strokeDasharray="10,6", stroke=#1e293b casi invisible
- Solo si hay >1 asset con localización
- Etiqueta: 🌐 + zone_name

Los contenedores se dibujan ANTES de los nodos (SVG painters algorithm)
para que los nodos queden encima. Padding: rack=14px, site=28px, zone=42px.

Solo se pintan para assets con binding_tier ∈ {compute, storage, network, data, cache}.
