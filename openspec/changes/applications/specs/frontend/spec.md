# Frontend Spec — Applications

## Estructura de la página ApplicationsPage

### Tabs
```jsx
[
  {to: "/applications",          label: "Servicios"},
  {to: "/applications/apps",     label: "Aplicaciones"},
  {to: "/applications/map",      label: "Mapa de Dependencias"}
]
```
Sidebar: "Servicios". Título página: "Gestión de Servicios".

### Panel de infraestructura
Botón "🏗 Infraestructura" en cada fila de aplicación.
Modal con lista de assets (checkboxes):
- Columnas: checkbox | Nombre | Tipo (AssetTypeBadge) | IP
- Al añadir: selector de binding_tier
- Al quitar: DELETE /v1/applications/{id}/infra-bindings/{bid}

### Mapa topológico SVG
- Layout por filas: `tier_order` determina fila (1=arriba)
- Separadores horizontales entre filas
- Etiquetas de capa a la izquierda (TIER_LABELS)
- Nodo con is_single_point_of_failure=true → borde rojo pulsante o icono ⚠️

### Tooltip flotante
Al hover sobre nodo muestra: nombre, criticidad, entorno, versión, tipo, IP, tier, localización, SPF.
Ajuste de posición para no salirse del SVG:
```js
// Si tooltip.x + width > svgWidth → tooltip.x = svgWidth - width
// Si tooltip.y + height > svgHeight → tooltip.y = svgHeight - height
```

---

## Campo de puerto en formulario de infra bindings

El modal de "🏗 Infraestructura" incluye el campo `communication_port` (Integer, nullable)
**visible en el formulario** antes del campo "Notas":

```jsx
<label>Puerto de comunicación</label>
<input type="number" placeholder="ej: 443, 5432, 8080, 6379…"
  value={form.communication_port || ''}
  onChange={e => setForm(p => ({...p, communication_port: e.target.value ? parseInt(e.target.value) : null}))}/>
```

El puerto también se muestra en la lista de bindings existentes como badge `mono`:
```jsx
{b.communication_port && <span className="text-[10px] font-mono bg-gray-100 px-1 py-0.5 rounded">:{b.communication_port}</span>}
```

En el grafo SVG, el puerto aparece en el label de la arista y en el tooltip del nodo:
- Arista: `"compute :5432"` (label + " :" + port)
- Tooltip: línea `"Puerto: 5432"` si communication_port está definido

---

## Badges de estado — mapas definitivos

```js
// STATUS_SVC — estados de servicio con contraste correcto
const STATUS_SVC = {
  active:      'bg-green-100 text-green-800 border border-green-500 font-semibold',
  degraded:    'bg-orange-100 text-orange-800 border border-orange-500 font-semibold',
  maintenance: 'bg-amber-100 text-amber-800 border border-amber-500 font-semibold',
  inactive:    'bg-gray-100 text-gray-700 border border-gray-400 font-semibold',
}
const STATUS_SVC_LABELS = {
  active: 'Activo', degraded: 'Degradado',
  maintenance: 'Mantenimiento', inactive: 'Inactivo',
}

// STATUS_APP — estados de aplicación
const STATUS_APP = {
  active:      'bg-green-100 text-green-800 border border-green-500 font-semibold',
  maintenance: 'bg-amber-100 text-amber-800 border border-amber-500 font-semibold',
  deprecated:  'bg-gray-100 text-gray-700 border border-gray-400 font-semibold',
  inactive:    'bg-gray-100 text-gray-700 border border-gray-400 font-semibold',
}
```

REGLA: Usar siempre `text-X-800 border border-X-500 font-semibold` para badges de estado.
NUNCA usar `text-X-700 border-X-300` — el contraste es insuficiente en tema claro.

## Localización en tablas de Aplicaciones y Servicios

### Application.to_dict() — campos añadidos
```python
"cell_name":      cell.name if cell else None,
"cell_full_path": cell.to_dict().get("full_path")  # "Zona › Site › Cell"
"environment":    str(self.environment).split(".")[-1]  # enum serializado
"status":         str(self.status).split(".")[-1]        # enum serializado
```

### Columna Localización en tabla de aplicaciones
```jsx
<td>
  {a.cell_full_path ? (
    <span className="inline-flex items-center gap-1 text-xs text-gray-700 bg-gray-50
                     border border-gray-200 rounded-full px-2 py-0.5">
      <span className="text-gray-400">📍</span>
      <span className="truncate max-w-[140px]" title={a.cell_full_path}>
        {a.cell_full_path}
      </span>
    </span>
  ) : <span className="text-xs text-gray-400">—</span>}
</td>
```

### Localización en componentes del detalle de servicio
En la tabla de componentes del panel de detalle, debajo del nombre de la aplicación
mostrar el `cell_full_path` en pequeño con icono 📍.

---

## Mapas de color definitivos — ApplicationsPage

Todos los badges deben usar el patrón: `bg-X-100 text-X-800 border border-X-400/500 font-semibold`
NUNCA usar `/60`, `/40`, `/20` ni `text-X-300` en tema claro.

```js
// ENV_COLORS
const ENV_COLORS = {
  production:  'bg-red-100 text-red-800 border border-red-400 font-semibold',
  staging:     'bg-orange-100 text-orange-800 border border-orange-400 font-semibold',
  development: 'bg-blue-100 text-blue-800 border border-blue-400 font-semibold',
  dr:          'bg-purple-100 text-purple-800 border border-purple-400 font-semibold',
}

// STATUS_APP + etiquetas traducidas
const STATUS_APP = {
  active:      'bg-green-100 text-green-800 border border-green-500 font-semibold',
  maintenance: 'bg-amber-100 text-amber-800 border border-amber-500 font-semibold',
  deprecated:  'bg-gray-100 text-gray-700 border border-gray-400 font-semibold',
  inactive:    'bg-gray-100 text-gray-700 border border-gray-400 font-semibold',
}
const STATUS_APP_LABELS = {
  active:'Activa', maintenance:'Mantenimiento', deprecated:'Deprecada', inactive:'Inactiva',
}

// STATUS_SVC + etiquetas traducidas
const STATUS_SVC = {
  active:      'bg-green-100 text-green-800 border border-green-500 font-semibold',
  degraded:    'bg-orange-100 text-orange-800 border border-orange-500 font-semibold',
  maintenance: 'bg-amber-100 text-amber-800 border border-amber-500 font-semibold',
  inactive:    'bg-gray-100 text-gray-700 border border-gray-400 font-semibold',
}
const STATUS_SVC_LABELS = {
  active:'Activo', degraded:'Degradado', maintenance:'Mantenimiento', inactive:'Inactivo',
}

// CRIT_COLORS
const CRIT_COLORS = {
  critical: 'bg-red-100 text-red-800 border border-red-500 font-bold',
  high:     'bg-orange-100 text-orange-800 border border-orange-400 font-semibold',
  medium:   'bg-yellow-100 text-yellow-800 border border-yellow-400 font-semibold',
  low:      'bg-gray-100 text-gray-700 border border-gray-300 font-semibold',
}

// ROLE_COLORS — todos en 100/800/400
const ROLE_COLORS = {
  frontend:       'bg-sky-100 text-sky-800 border border-sky-400',
  backend:        'bg-green-100 text-green-800 border border-green-400',
  api_gateway:    'bg-indigo-100 text-indigo-800 border border-indigo-400',
  auth:           'bg-orange-100 text-orange-800 border border-orange-400',
  worker:         'bg-yellow-100 text-yellow-800 border border-yellow-400',
  // ... resto igual
}

// BINDING_COLORS — todos en 100/800/400
const BINDING_COLORS = {
  runs_on:          'bg-slate-100 text-slate-700 border border-slate-400',
  hosted_on:        'bg-slate-100 text-slate-700 border border-slate-400',
  uses_database:    'bg-cyan-100 text-cyan-800 border border-cyan-400',
  proxied_by:       'bg-indigo-100 text-indigo-800 border border-indigo-400',
  // ... resto igual
}

// DEP_COLORS — todos en 100/800/400
const DEP_COLORS = {
  calls_api:        'bg-blue-100 text-blue-800 border border-blue-400',
  subscribes_to:    'bg-pink-100 text-pink-800 border border-pink-400',
  proxied_through:  'bg-indigo-100 text-indigo-800 border border-indigo-400',
  // ... resto igual
}
```

## REGLA GLOBAL para badges en tema claro
- ✓ `bg-X-100 text-X-800 border border-X-400 font-semibold`
- ✗ `bg-X-900/60`, `bg-X-900/40`, `text-X-300`, `text-X-200` — INVISIBLE en tema claro

## Bug: claves duplicadas en STATUS_APP
JS no da error cuando un objeto literal tiene claves duplicadas — la última gana.
Siempre verificar que no hay duplicados en los mapas de color.
```js
// ❌ BUG — 'deprecated' e 'inactive' declarados dos veces:
const STATUS_APP = {
  deprecated: 'bg-gray-100 text-gray-700 ...',  // primera (correcta)
  inactive:   'bg-gray-100 text-gray-700 ...',  // primera (correcta)
  deprecated: 'bg-gray-100 text-gray-600',       // segunda SOBREESCRIBE (incorrecta)
  inactive:   'bg-red-100 text-red-700 ...',     // segunda SOBREESCRIBE (incorrecta)
}
```

---

## Mapa: localización en nodos SVG

Los nodos con `location_name` tienen altura 72px (vs 60px normal) y muestran
📍 + nombre de la celda en verde menta (`#6ee7b7`) en la tercera línea.

```jsx
const hasLoc = !!n.location_name
const nodeH = hasLoc ? 72 : 60
// ...
{hasLoc && (
  <text x="90" y={56} fill="#6ee7b7" fontSize="8" textAnchor="middle" opacity="0.9">
    📍 {n.location_name.length>22 ? n.location_name.slice(0,20)+'…' : n.location_name}
  </text>
)}
```

## Mapa: NO usar placeholderData en el grafo

```jsx
// ❌ INCORRECTO — muestra el grafo anterior mientras carga el nuevo:
placeholderData: (prev) => prev

// ✅ CORRECTO — muestra spinner limpio al cambiar de servicio:
// (sin placeholderData)
```

---

## Contenedores de localización en el grafo SVG

Los activos físicos (`binding_tier` ∈ {compute,storage,network,data,cache})
que comparten la misma celda/rack se agrupan visualmente en un rectángulo
contenedor con esquinas redondeadas y borde semitransparente con `strokeDasharray`.

Colores por tipo de celda:
- rack → borde azul `rgba(96,165,250,0.3)`
- datacenter → borde índigo `rgba(99,102,241,0.3)`
- serverroom → borde cyan `rgba(34,211,238,0.25)`
- cabinet → borde violeta `rgba(167,139,250,0.3)`

Etiqueta con icono (▤ rack, ⬛ datacenter...) + zona › site nombre abreviado.
Backend devuelve `location_info` estructurado con cell_name, cell_type,
row_id, rack_unit, site_name, zone_name.
