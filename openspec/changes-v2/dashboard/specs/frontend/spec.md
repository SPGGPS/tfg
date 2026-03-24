# Frontend Spec — Dashboard

## Ruta y sidebar
- Ruta: /dashboard (index de la app)
- Sidebar: primer item "Dashboard" con icono
- Redirigir / → /dashboard, /inventario → /inventario

## Componente PieChart (reutilizable)

```jsx
<PieChart
  data={[
    { label: "EOL KO",   count: 3, color: "#dc2626", items: [{id, name, type},...] },
    { label: "EOL OK",   count: 7, color: "#16a34a", items: [...] },
  ]}
  title="Servidores físicos"
  onSegmentClick={(segment) => navigate(`/inventario?tag=EOL+KO`)}
  size={160}
/>
```

### Implementación SVG
```jsx
// Calcular arcos SVG
function polarToXY(cx, cy, r, angleDeg) {
  const rad = (angleDeg - 90) * Math.PI / 180
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
}
function describeArc(cx, cy, r, startAngle, endAngle) {
  const s = polarToXY(cx, cy, r, startAngle)
  const e = polarToXY(cx, cy, r, endAngle)
  const large = endAngle - startAngle > 180 ? 1 : 0
  return `M ${cx} ${cy} L ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y} Z`
}
```

### Tooltip
Al hover, mostrar un div flotante (fixed, z-50) con:
- Título del sector (label + count)
- Lista de hasta 8 elementos (nombre + tipo o estado)
- Enlace "Ver todos →" si hay más de 8

### Click → filtro URL
Cada sector construye una URL de filtro:
- Assets EOL: /inventario?tag_name=EOL+KO
- Compliance KO: /inventario?compliance_filter=edr_ko
- Backup missing: /inventario?backup_local=missing
- Certificados: /certificates?status=expired

## Layout de bloques
```jsx
// Bloque: título + grid de gráficos
<DashboardBlock title="End of Life por tipo de activo">
  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
    {eolByType.map(group => <PieChart key={group.type} .../>)}
  </div>
</DashboardBlock>
```

## api.js
```js
export const dashboardApi = {
  get: () => req('/dashboard'),
}
```

---

## Fixes aplicados

### Navegación correcta
- Ruta inventario: `/inventario` (no `/inventory` ni `/`)
- Sidebar: Dashboard en `/dashboard`, Inventario en `/inventario`
- Click en sector → `navigate('/inventario?search=TAG+NAME')` inmediato, sin segundo click

### Tooltip fixed al viewport
```jsx
// Usar coordenadas del evento de ratón (clientX/Y) — fijas al viewport
const handleMove = (e, slice) => setTooltip({ x: e.clientX, y: e.clientY, slice })

// El componente Tooltip usa position:fixed
<div style={{ position:'fixed', left, top, zIndex: 9999, pointerEvents:'none' }}>
```
No usar coordenadas relativas al contenedor (getBoundingClientRect) — 
el contenedor puede estar en cualquier posición en el scroll.

### Click directo en sector SVG
El click en el path SVG llama directamente a `onSliceClick(slice)` que navega.
No hay popup intermedio — el tooltip es solo informativo (pointerEvents:none).

### Mapeo de filtros
| Bloque | Filtro URL | Parámetro |
|--------|-----------|-----------|
| EOL | /inventario?type=X&search=EOL+KO | search por tag name |
| Compliance | /inventario?search=EDR+Missing | search por tag de sistema |
| Backup | /inventario?search=Backup+Local+OK | search por tag de sistema |
| Certificados | /certificates?status=expired | status filter |

---

## URL params: filtros desde Dashboard

### InventoryPage — lee ?search=X&type=Y al montar
```jsx
const [urlParams] = useSearchParams()
const [search, setSearch] = useState(() => urlParams.get('search') || '')
const [typeFilter, setType] = useState(() => urlParams.get('type') || '')

useEffect(() => {
  setSearch(urlParams.get('search') || '')
  setType(urlParams.get('type') || '')
  setPage(1)
}, [urlParams.toString()])
```

### ApplicationsPage — lee ?tab=X&service_id=Y al montar
```jsx
useEffect(() => {
  const tab = urlParams.get('tab')
  if (tab === 'mapa') setActiveTab('Mapa de Dependencias')
  else if (tab === 'servicios') setActiveTab('Servicios')
}, [urlParams.toString()])
```

ServicesTab también lee service_id y auto-abre el drawer de detalle.

### Dashboard → Inventario: tabla de filtros
| Sector | URL generada |
|--------|-------------|
| EOL KO de Servers | /inventario?type=server_physical&search=EOL+KO |
| EDR Missing | /inventario?search=EDR+Missing |
| Backup Local Missing | /inventario?search=Backup+Local+Missing |
| Expirado cert | /certificates?status=expired |
| Mapa servicio X | /applications?tab=mapa&service_id=UUID |
| Estado activo svcs | /applications?tab=servicios&status=active |

## Bloque Servicios en Dashboard

Gráfico de sectores + tabla de servicios inline:
- Sectores: colores = badges de estado (verde/naranja/ámbar/gris)
- Tabla: nombre, badge estado, badge criticidad, equipo, botón "🗺 Mapa"
- Click sector → /applications?tab=servicios&status=X
- Click "🗺 Mapa" → /applications?tab=mapa&service_id=UUID (abre el drawer del servicio)

## Colores coherentes con badges

EOL:        eol_ko=#dc2626, eol_warn=#d97706, eol_ok=#16a34a, no_data=#cbd5e1
Compliance: ok=#16a34a, ok_with_exception=#1d4ed8, ko_with_exception=#7c3aed, ko=#ef4444
Backup:     ok=#16a34a, missing=#ef4444
Certs:      valid=#16a34a, expiring=#d97706, critical=#f97316, expired=#ef4444
Servicios:  active=#16a34a, degraded=#f97316, maintenance=#d97706, inactive=#94a3b8
