# Frontend — Localizaciones físicas (Zone → Site → Cell)

## ADDED Requirements

---

### Requirement: Página /locations — árbol jerárquico Zone → Site → Cell

Ruta `/locations`, accesible solo para rol `admin`, en el sidebar entre Etiquetas y Fuentes de Datos.

**Estructura visual:**

```
🗺 ZONA — "Ayuntamiento SSReyes"          [Editar] [✕]
  🏛 Edificio Principal — Plaza...         [Editar] [✕]
    [ 📦 Rack A · rack · Fila A · U1-U42  [Asignar assets] [✎] [✕] ]
    [ 🖥 CPD Principal · datacenter        [Asignar assets] [✎] [✕] ]
  🏛 Edificio Anexo — C/ Cervantes         [Editar] [✕]
    [ 🖥 CPD Backup · datacenter            [Asignar assets] [✎] [✕] ]
```

Las celdas se muestran en una grid de 2 columnas dentro de cada site.

**Iconos por cell_type:**
- `datacenter` → 🖥 CPD / Datacenter
- `serverroom` → 🚪 Sala de Servidores
- `rack` → 📦 Rack
- `cabinet` → 🗄 Armario
- `floor` → 🏢 Planta
- `zone` → 🗺 Zona técnica
- `other` → 📍 Otro

**Botones de creación** (editor+) en la cabecera:
- `+ Zona` — nivel superior
- `+ Localización` — site dentro de una zona
- `+ Celda` — cell dentro de un site

**Llamadas a la API:**
- `GET /v1/locations/tree` — carga todo el árbol en una sola llamada
- `GET /v1/zones` — para el selector del formulario de Site
- `GET /v1/sites` — para el selector del formulario de Cell y bulk assign

---

### Requirement: Formularios de creación/edición (modales)

**Formulario Zona:**
- `name` (input, obligatorio)
- `description` (textarea, opcional)

**Formulario Site (Localización física):**
- `zone_id` (select con lista de zonas, obligatorio)
- `name` (input, obligatorio)
- `address` (input, opcional)
- `description` (textarea, opcional)

**Formulario Cell (Celda / CPD / Rack):**
- `site_id` (select con lista de sites mostrando `{zone_name} › {site_name}`, obligatorio)
- `name` (input, obligatorio)
- `cell_type` (select con opciones tipadas, opcional)
- `row_id` (input, opcional) — placeholder: "Fila A, Pasillo Frío…"
- `rack_unit` (input, opcional) — placeholder: "U1-U42, U12…"
- `description` (textarea, opcional)

---

### Requirement: Modal "Asignar assets" — bulk assign desde la celda

Cada celda tiene un botón **"Asignar assets"** que abre un modal con dos secciones:

**Sección 1 — Assets ya asignados a esta celda:**
- Lista con nombre, tipo y botón "Desvincular" por asset
- Vacía si no hay ninguno

**Sección 2 — Añadir assets del inventario:**
- Input de búsqueda (llama a `GET /v1/assets?search=…&page_size=50`)
- Lista de assets NO asignados a esta celda (filtrada client-side)
- Checkbox en cada item para selección múltiple
- Botón "Asignar (N)" — llama a `POST /v1/cells/bulk-assign` con los IDs seleccionados
- La lista se refresca automáticamente tras asignar

**Invalidaciones tras asignar:**
- `queryKey: ['cell-assets', cell.id]` — refresca assets de la celda
- No invalida el inventario global (operación no cambia compliance)

#### Scenario: Asignación masiva desde el modal
- **GIVEN** la celda "Rack A" sin assets asignados
- **WHEN** el admin busca "web", selecciona "web-prod-01" y "web-prod-02", pulsa "Asignar (2)"
- **THEN** POST /v1/cells/bulk-assign con asset_ids=[id1,id2] y cell_id="cell-rack-a"
- **THEN** el toast muestra "2 assets asignados a 'Rack A'"
- **THEN** los 2 assets aparecen en la sección "Assets ya asignados"

#### Scenario: Desvincular un asset individual
- **GIVEN** "web-prod-01" asignado a "Rack A"
- **WHEN** el admin pulsa "Desvincular" en ese asset
- **THEN** POST /v1/cells/bulk-assign con asset_ids=[id1] y cell_id=null
- **THEN** el asset desaparece de la sección "Assets ya asignados"

---

### Requirement: Selector de celda en formulario de Aplicación

El formulario de crear/editar Application incluye un campo **"Celda / Ubicación física"** (select opcional):
- Carga `GET /v1/cells` al montarse
- Muestra `full_path` de cada celda: "Ayuntamiento SSReyes › Edificio Principal › Rack A"
- Opción vacía "— Sin asignar —"
- Guarda `cell_id` en el campo correspondiente de la aplicación

**Query key:** `['cells']` — se cachea para no repetir la llamada en cada modal.

---

### Requirement: locationsApi en api.js

```javascript
export const locationsApi = {
  tree: () => req('/locations/tree'),
  listZones: () => req('/zones'),
  createZone: (d) => req('/zones', { method: 'POST', body: JSON.stringify(d) }),
  updateZone: (id, d) => req(`/zones/${id}`, { method: 'PUT', body: JSON.stringify(d) }),
  deleteZone: (id) => req(`/zones/${id}`, { method: 'DELETE' }),
  listSites: (zone_id?) => req(`/sites${zone_id ? '?zone_id='+zone_id : ''}`),
  createSite: (d) => req('/sites', { method: 'POST', body: JSON.stringify(d) }),
  updateSite: (id, d) => req(`/sites/${id}`, { method: 'PUT', body: JSON.stringify(d) }),
  deleteSite: (id) => req(`/sites/${id}`, { method: 'DELETE' }),
  listCells: (site_id?) => req(`/cells${site_id ? '?site_id='+site_id : ''}`),
  createCell: (d) => req('/cells', { method: 'POST', body: JSON.stringify(d) }),
  updateCell: (id, d) => req(`/cells/${id}`, { method: 'PUT', body: JSON.stringify(d) }),
  deleteCell: (id) => req(`/cells/${id}`, { method: 'DELETE' }),
  cellAssets: (id) => req(`/cells/${id}/assets`),
  bulkAssign: (cell_id, asset_ids) => req('/cells/bulk-assign', {
    method: 'POST', body: JSON.stringify({ cell_id, asset_ids })
  }),
}
```

---

### Requirement: Tooltip del mapa — mostrar localización de la aplicación

Si una aplicación tiene `location_path` (calculado del `cell._full_path()`), el tooltip del nodo en el mapa de dependencias muestra `📍 {location_path}`.

#### Scenario: Tooltip con localización
- **GIVEN** la aplicación "sede-api" con cell_id asignado
- **WHEN** hover sobre su nodo en el mapa
- **THEN** el tooltip muestra "📍 Ayuntamiento SSReyes › Edificio Principal › Rack A"

#### Scenario: AppForm con celda — crash evitado
- La query `useQuery(['cells'], locationsApi.listCells)` se declara **dentro** del componente `AppForm`, no en su padre
- Si se declara fuera, `locList`/`cells` no está en scope y la pantalla queda en negro (crash de React)
- El campo `initial` NO usa default destructuring `{ initial={} }` — usar `const initVal = initial || {}`

---

### Requirement: Orden de botones de creación

Los botones en la cabecera de la página muestran el nivel más alto a la derecha como primario:

```
[ + Celda ]  [ + Localización ]  [ + Zona (btn-primary) ]
```

El botón `+ Zona` es `btn-primary` (rojo) por ser el elemento raíz. Los demás son `btn-secondary`.

---

### Requirement: BulkAssignModal — renderizado condicional

`BulkAssignModal` se renderiza condicionalmente dentro del Modal:

```jsx
<Modal open={modal?.type==='assign'} ...>
  {modal?.data && <BulkAssignModal cell={modal.data} onClose={...}/>}
</Modal>
```

**Problema conocido:** en TanStack Query v5, si el componente se monta/desmonta al alternar entre distintos tipos de modal, puede producir el error "No mutationFn found". Si esto ocurre, la solución es siempre montar el componente con un cell dummy y usar `enabled: isReal` en los queries.
Esta regla aplica a TODAS las mutaciones pasadas como prop `onSubmit`, `onClick`, etc. en todo el proyecto.
---

### Requirement: locationsApi en api.js — métodos Zone/Site/Cell obligatorios

El objeto `locationsApi` en `services/api.js` **debe contener todos los métodos** para Zone, Site y Cell. Si `locationsApi.createZone` es `undefined`, TanStack Query lanza "No mutationFn found" al intentar mutar.

**Causa raíz del error "No mutationFn found":** el archivo `api.js` tenía la versión antigua del objeto `locationsApi` (modelo `Location` autorreferenciado) sin los métodos del nuevo modelo `Zone/Site/Cell`. `useMutation({ mutationFn: undefined })` produce este error.

```javascript
export const locationsApi = {
  tree: () => req('/locations/tree'),

  // Zones
  listZones:  ()       => req('/zones'),
  createZone: (d)      => req('/zones', { method:'POST', body:JSON.stringify(d) }),
  updateZone: (id, d)  => req(`/zones/${id}`, { method:'PUT', body:JSON.stringify(d) }),
  deleteZone: (id)     => req(`/zones/${id}`, { method:'DELETE' }),

  // Sites
  listSites:  (zone_id) => req(`/sites${zone_id?'?zone_id='+zone_id:''}`),
  createSite: (d)       => req('/sites', { method:'POST', body:JSON.stringify(d) }),
  updateSite: (id, d)   => req(`/sites/${id}`, { method:'PUT', body:JSON.stringify(d) }),
  deleteSite: (id)      => req(`/sites/${id}`, { method:'DELETE' }),

  // Cells
  listCells:  (site_id) => req(`/cells${site_id?'?site_id='+site_id:''}`),
  createCell: (d)       => req('/cells', { method:'POST', body:JSON.stringify(d) }),
  updateCell: (id, d)   => req(`/cells/${id}`, { method:'PUT', body:JSON.stringify(d) }),
  deleteCell: (id)      => req(`/cells/${id}`, { method:'DELETE' }),
  cellAssets: (id)      => req(`/cells/${id}/assets`),

  bulkAssign: (cell_id, asset_ids) => req('/cells/bulk-assign', {
    method:'POST', body:JSON.stringify({ cell_id, asset_ids })
  }),
}
```

**Regla general:** cuando se refactoriza un modelo de backend (ej. `Location` → `Zone/Site/Cell`), hay que actualizar `api.js` en el mismo commit. Si el objeto de API no se actualiza, todas las mutaciones que referencien los métodos nuevos fallarán silenciosamente con "No mutationFn found".

#### Scenario: Error al crear zona por api.js desactualizado
- **GIVEN** `locationsApi` en `api.js` tiene la versión antigua (sin `createZone`)
- **WHEN** el usuario pulsa "Crear zona" en el modal
- **THEN** TanStack Query lanza "No mutationFn found" porque `mutationFn` es `undefined`
- **FIX** actualizar `api.js` con `createZone: (d) => req('/zones', { method:'POST', ... })`

---

### Requirement: Orden de botones — Zona primero

```
[ + Zona (btn-primary) ]  [ + Localización ]  [ + Celda ]
```

El botón de nivel más alto (Zona) es `btn-primary` rojo. Los otros son `btn-secondary`.

---

### Requirement: Orden definitivo de botones de creación

Los botones en la cabecera de la página SHALL aparecer en orden jerárquico:

```
[ + Zona (btn-primary) ]  [ + Localización (btn-secondary) ]  [ + Celda (btn-secondary) ]
```

Este orden refleja la jerarquía del modelo — siempre se crea primero la Zona (nivel más alto), luego la Localización dentro de ella, luego la Celda dentro de la Localización. El botón `+ Zona` usa `btn-primary` para destacar que es el punto de entrada.
