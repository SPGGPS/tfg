# Frontend Spec — Localizaciones físicas

## LocationsPage (pages/LocationsPage.jsx)

### Orden de botones (jerárquico, obligatorio)
```jsx
<button className="btn-primary text-xs"   onClick={() => setModal({type:"zone"})}>+ Zona</button>
<button className="btn-secondary text-xs" onClick={() => setModal({type:"site"})}>+ Localización</button>
<button className="btn-secondary text-xs" onClick={() => setModal({type:"cell"})}>+ Celda</button>
```

### Árbol visual
```
🗺 Zona — "Ayuntamiento SSReyes"         [Editar] [✕]
  🏛 Edificio Principal — Plaza...        [Editar] [✕]
    📦 Rack A · rack · Fila A · U1-U42  [🔗 Asignar] [✎] [✕]
    🖥 CPD Principal · datacenter         [🔗 Asignar] [✎] [✕]
```

### Mutaciones — regla obligatoria TanStack v5
Declarar cada mutación en nivel superior del componente (no dentro de objetos):
```jsx
const createZoneMut = useMutation({ mutationFn: locationsApi.createZone, ... })
const updateZoneMut = useMutation({ mutationFn: ({id,...d}) => locationsApi.updateZone(id,d), ... })
// Usar siempre con arrow function:
<ZoneForm onSubmit={d => createZoneMut.mutate(d)} />
```

### BulkAssignModal — siempre montado
```jsx
// En el JSX del componente principal:
<Modal open={modal?.type === "assign"} ...>
  <BulkAssignModal
    cell={modal?.data || {id: "__none__", name: ""}}
    onClose={() => setModal(null)}
  />
</Modal>

// Dentro de BulkAssignModal:
const isReal = cell?.id && cell.id !== "__none__"
const {data} = useQuery({ queryKey: ["cell-assets", cell.id], queryFn: ..., enabled: isReal })
if (!isReal) return null
```

### locationsApi completo en api.js
```js
export const locationsApi = {
  tree: () => req("/locations/tree"),
  listZones: () => req("/zones"),
  createZone: (d) => req("/zones", { method:"POST", body:JSON.stringify(d) }),
  updateZone: (id, d) => req(`/zones/${id}`, { method:"PUT", body:JSON.stringify(d) }),
  deleteZone: (id) => req(`/zones/${id}`, { method:"DELETE" }),
  listSites: (zone_id) => req(`/sites${zone_id?"?zone_id="+zone_id:""}`),
  createSite: (d) => req("/sites", { method:"POST", body:JSON.stringify(d) }),
  updateSite: (id, d) => req(`/sites/${id}`, { method:"PUT", body:JSON.stringify(d) }),
  deleteSite: (id) => req(`/sites/${id}`, { method:"DELETE" }),
  listCells: (site_id) => req(`/cells${site_id?"?site_id="+site_id:""}`),
  createCell: (d) => req("/cells", { method:"POST", body:JSON.stringify(d) }),
  updateCell: (id, d) => req(`/cells/${id}`, { method:"PUT", body:JSON.stringify(d) }),
  deleteCell: (id) => req(`/cells/${id}`, { method:"DELETE" }),
  cellAssets: (id) => req(`/cells/${id}/assets`),
  bulkAssign: (cell_id, asset_ids) => req("/cells/bulk-assign", {
    method:"POST", body:JSON.stringify({ cell_id, asset_ids })
  }),
}
```

---

## Colores del árbol jerárquico (Zone → Site → Cell)

```jsx
// Zone header
<div style={{background:"linear-gradient(135deg,#FFF0F0,#FDE8E8)", borderBottom:"2px solid #EED8D8"}}>

// Zone badge (conteo de sites)
<span style={{backgroundColor:"#C8001D20", color:"#9B0016", borderColor:"#C8001D60", border:"1px solid"}}>

// Site row  
<div style={{backgroundColor:"#F9F0F0", borderBottom:"1px solid #EED8D8"}}>

// Site border wrapper
<div className="border-b last:border-0" style={{borderColor:"#EED8D8"}}>

// Cell card
<div style={{backgroundColor:"#FFFFFF", border:"1px solid #EED8D8"}}>

// Cell type badge y site badge de conteo
<span style={{backgroundColor:"#F5EDED", color:"#7A4040", border:"1px solid #DCC8C8"}}>

// Delete button
<button className="text-red-600 hover:text-red-800 text-xs px-1 font-semibold">
```

NO usar: bg-blue-950, bg-gray-900, border-gray-800, text-blue-300, text-red-400 (en tema claro)
