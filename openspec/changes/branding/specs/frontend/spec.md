# Frontend Spec — Branding

## Todos los tokens de color implementados

### tailwind.config.js
```js
colors: {
  primary: {
    DEFAULT: "#C8001D",
    hover:   "#A8001A",
    dark:    "#8B0016",
    light:   "#FDECEA",
  },
  corporate: {
    red:    "#C8001D",
    red2:   "#E8001F",
    cream:  "#FFF8F8",
    border: "#E5E7EB",
  },
  surface: {
    body:  "#F4F5F7",
    card:  "#FFFFFF",
    row:   "#F9FAFB",
    input: "#FFFFFF",
    hover: "#FFF1F2",
  }
}
```

### index.css — clases completas implementadas
Ver sección 03-FRONTEND.md del spec de referencia para el CSS exacto.
Lo importante: los gradientes de compliance son semánticos y NUNCA deben cambiarse.

### Regla para pedir cambios de color
Si se necesita cambiar el rojo corporativo al hex exacto de SSReyes:
1. Cambiar `primary.DEFAULT` en tailwind.config.js
2. Cambiar las ocurrencias de `#C8001D` en index.css
3. Todo lo demás usa los tokens y se actualiza automáticamente
---

## Reglas de contraste — obligatorias para tema claro

El tema es **claro** (#FDF7F7 body, cards blancas). Los colores dark-mode como
`text-gray-400`, `bg-gray-700`, `bg-gray-900/60` no tienen contraste suficiente.

### Escala de grises permitida
| Uso | Clase Tailwind | Hex |
|-----|---------------|-----|
| Texto principal | `text-gray-900` o `text-gray-800` | #111827 / #1F2937 |
| Texto secundario / labels | `text-gray-600` o `text-gray-700` | #4B5563 / #374151 |
| Texto terciario / placeholders | `text-gray-500` | #6B7280 |
| Bordes de cards/tablas | `border-gray-200` | #E5E7EB |
| Bordes de inputs | `border-gray-300` | #D1D5DB |
| Fondos sutiles | `bg-gray-50` | #F9FAFB |
| Hover de filas | `hover:bg-gray-100` | #F3F4F6 |

### NUNCA usar en este tema claro
- `text-gray-400` o más claro → usar `text-gray-600` mínimo
- `text-gray-300`, `text-gray-200`, `text-gray-100` → usar `text-gray-700+`
- `bg-gray-700`, `bg-gray-800`, `bg-gray-900` → usar `bg-gray-50` o `bg-gray-100`
- `border-gray-700`, `border-gray-600` → usar `border-gray-200` o `border-gray-300`

### Excepciones — colores semánticos (mantener oscuros)
Los badges de compliance usan fondos oscuros deliberadamente para contraste sobre blanco:
- `bg-green-900/60 text-green-300` → OK compliance
- `bg-red-900/60 text-red-300` → KO compliance
Estos NO se cambian.

## TagBadge — contraste con fondo blanco

El color del texto debe ser el `color_code` de la etiqueta (sólido, no transparente).
El fondo debe ser muy suave para no dominar pero sí visible.

```js
style = {
  backgroundColor: tag.color_code + "20",  // ~12% opacidad — visible pero suave
  color: tag.color_code,                    // texto sólido del color — máximo contraste
  borderColor: tag.color_code,              // borde sólido del color
  border: "1px solid",
  fontWeight: "600"                         // semi-bold para legibilidad
}
```

Si el color_code es muy claro (ej: #FFFF00), el texto puede ser invisible.
Recomendación: usar colores con luminosidad media/baja para etiquetas (evitar amarillos puros).

## TanStack Query v5 — keepPreviousData

En v4: `keepPreviousData: true`
En v5: `placeholderData: (prev) => prev`

Siempre usar la forma v5 en todos los useQuery:
```js
const { data } = useQuery({
  queryKey: [...],
  queryFn: ...,
  placeholderData: (prev) => prev,  // evita flash de loading al cambiar filtros
})
```

---

## TanStack Query v5 — invalidateQueries

En v4: `qc.invalidateQueries(['key'])`
En v5: `qc.invalidateQueries({queryKey: ['key']})`

Siempre usar la forma v5. Afecta a TODAS las páginas.

```js
// ❌ v4 — rompe en TanStack v5 (causa que la query no se refresque)
qc.invalidateQueries(['certificates'])
qc.invalidateQueries(['assets'])

// ✅ v5 — correcto
qc.invalidateQueries({queryKey: ['certificates']})
qc.invalidateQueries({queryKey: ['assets'], exact: false})
```

Esta fue la causa de que CertificatesPage no cargara tras crear/editar certificados.
Archivos afectados: CertificatesPage, ApplicationsPage, InventoryPage, TagsPage, DataSourcesPage, ProfilePage.

## TagBadge — texto oscurecido (contraste sobre fondo claro)

El `color_code` de la etiqueta puede ser claro (ej: #FFB3B3). Para garantizar contraste
se oscurece el color al 65% para el texto:

```js
const darken = (hex, factor=0.65) => {
  const [r,g,b] = [hex.slice(1,3), hex.slice(3,5), hex.slice(5,7)].map(x=>parseInt(x,16))
  return `rgb(${Math.round(r*factor)},${Math.round(g*factor)},${Math.round(b*factor)})`
}
style = {
  backgroundColor: clr + "25",     // ~15% opacidad — suave pero visible
  color: darken(clr, 0.65),         // oscurecido al 65% — buen contraste
  borderColor: clr + "99",          // ~60% opacidad
  border: "1px solid",
  fontWeight: "600"
}
```

---

## Bugs críticos resueltos — TanStack Query v5

### BUG: CertificatesPage no cargaba (TabBar definida dentro de JSX)
TabBar estaba definida DENTRO del bloque JSX del modal `detailCert`, pero se usaba
antes de esa definición. JavaScript no hace hoisting de funciones dentro de JSX.

**Solución:** mover TabBar como función de módulo, ANTES del componente que la usa:
```jsx
// ✅ CORRECTO — función de módulo, fuera de cualquier componente
function TabBar() {
  const location = useLocation()
  return (
    <div className="flex border-b mb-4">
      {tabs.map(tab => <Link key={tab.to} to={tab.to} .../>)}
    </div>
  )
}

export default function CertificatesPage() {
  // TabBar ya está disponible aquí
  return <div><TabBar/>...</div>
}

// ❌ INCORRECTO — definida dentro de JSX
return (
  <div>
    {someCondition && (() => {
      const TabBar = () => <div>...</div>  // NO disponible fuera de este bloque
      return <TabBar/>
    })()}
    <TabBar/>  // ReferenceError: TabBar is not defined
  </div>
)
```

### BUG: invalidateQueries con sintaxis v4 en CertificatesPage
TanStack Query v4: `qc.invalidateQueries(['certificates'])`
TanStack Query v5: `qc.invalidateQueries({queryKey: ['certificates']})`

Afectaba a: CertificatesPage, ApplicationsPage, InventoryPage, TagsPage, DataSourcesPage.

---

## Estilo unificado de badges de etiqueta (color dinámico)

Todos los badges con `color_code` dinámico deben usar la función `darken` para el texto,
garantizando contraste independientemente del color elegido.

**Implementación en TagBadge (components/ui/index.jsx):**
```jsx
const hexToRgb = (h) => [parseInt(h.slice(1,3),16), parseInt(h.slice(3,5),16), parseInt(h.slice(5,7),16)]
const darken = (h, f=0.6) => { const [r,g,b]=hexToRgb(h); return `rgb(${Math.round(r*f)},${Math.round(g*f)},${Math.round(b*f)})` }
const clr = tag.color_code?.startsWith('#') ? tag.color_code : '#666666'
const style = {
  backgroundColor: `${clr}25`,    // fondo: 15% opacidad — visible pero suave
  color: darken(clr, 0.65),        // texto: mismo tono al 65% — siempre legible
  borderColor: `${clr}99`,         // borde: 60% opacidad
  border: '1px solid',
  fontWeight: '600'
}
```

Este mismo patrón se aplica en todos los badges inline con `color_code` en InventoryPage.

---

## Función colorBadgeStyle — helper exportado (components/ui/index.jsx)

Para usar el mismo estilo de badge en toda la app, usar la función exportada:

```js
import { colorBadgeStyle } from '../components/ui/index.jsx'

// En cualquier badge con color dinámico:
<span className="badge border" style={colorBadgeStyle(tag.color_code)}>
  {tag.name}
</span>

// Implementación:
export const colorBadgeStyle = (colorCode) => {
  const clr = colorCode?.startsWith('#') ? colorCode : '#666666'
  return {
    backgroundColor: `${clr}25`,         // fondo 15% opacidad
    color: darkenColor(clr, 0.65),        // texto 65% del color — legible
    borderColor: `${clr}99`,             // borde 60% opacidad
    border: '1px solid',
    fontWeight: '600'
  }
}
```

Usar `colorBadgeStyle` siempre que un badge tenga color dinámico (color_code de BD).
Para badges con colores fijos, usar clases Tailwind con `text-X-800 border-X-400 font-semibold`.

---

## colorBadgeStyle v2 — fondo sólido con contraste automático

El estilo definitivo para TODAS las etiquetas de color dinámico:

```js
export const needsWhiteText = (hex) => {
  const [r,g,b] = hexToRgb(hex)
  const c = (v) => { const s=v/255; return s<=0.04045 ? s/12.92 : Math.pow((s+0.055)/1.055,2.4) }
  const L = 0.2126*c(r) + 0.7152*c(g) + 0.0722*c(b)
  return L < 0.35  // colores oscuros → texto blanco
}

export const colorBadgeStyle = (colorCode) => {
  const clr = colorCode?.startsWith('#') ? colorCode : '#666666'
  return {
    backgroundColor: clr,           // fondo sólido del color
    color: needsWhiteText(clr) ? '#ffffff' : '#1a1a1a',  // auto contraste
    border: `1px solid ${clr}`,
    fontWeight: '600',
  }
}
```

Umbrales de luminancia WCAG para colores de sistema:
- Virtual #8b5cf6 L=0.198 → texto blanco
- EDR Missing #dc2626 L=0.167 → texto blanco  
- Backup Cloud Missing #9f1239 L=0.081 → texto blanco
- Switch #0ea5e9 L=0.329 → texto oscuro
- Router #f59e0b L=0.439 → texto oscuro

## Regla: NUNCA usar colores dark-mode en el tema claro

El tema es claro (#FDF7F7). Estos colores son INVISIBLES:
- bg-red-900/30 → usar bg-red-50
- text-red-300 → usar text-red-700
- text-red-400 → usar text-red-700
- bg-yellow-900/60 → usar bg-yellow-100
- bg-gray-700 → usar bg-gray-100

---

## colorBadgeStyle v3 — estilo definitivo (fondo suave + texto oscurecido)

El estilo aprobado por el usuario es el de **TagsPage**: fondo muy suave del color,
texto oscurecido al 60%, borde semitransparente. NO fondo sólido.

```js
export const colorBadgeStyle = (colorCode) => {
  const clr = colorCode?.startsWith('#') ? colorCode : '#666666'
  const [r,g,b] = hexToRgb(clr)
  const textColor = `rgb(${Math.round(r*0.6)},${Math.round(g*0.6)},${Math.round(b*0.6)})`
  return {
    backgroundColor: clr + '20',   // 12.5% opacidad — fondo muy suave
    color: textColor,               // mismo tono al 60% — legible sobre blanco
    borderColor: clr + 'aa',        // borde 67% opacidad
    border: '1.5px solid',
    fontWeight: '700',
  }
}
```

Ejemplos de resultado:
- Backup Cloud Missing #9f1239 → fondo rosado muy suave + texto rgb(95,11,33) (bordo oscuro)
- EDR Missing #dc2626 → fondo rojo muy suave + texto rgb(132,22,22) (rojo oscuro)
- Cisco #1d4ed8 → fondo azul muy suave + texto rgb(17,47,130) (azul oscuro)
- Switch #0ea5e9 → fondo azul claro muy suave + texto rgb(8,99,139)
- Router #f59e0b → fondo ámbar muy suave + texto rgb(147,94,7)

## Colores de la página Localizaciones

La página de Localizaciones usaba dark-mode (`bg-blue-950/30`, `bg-gray-900/30`).
Corregida para usar el sistema de diseño corporativo:

| Elemento | Antes (INCORRECTO) | Después (CORRECTO) |
|---------|-------------------|-------------------|
| Zone header | `bg-blue-950/30` | gradient `#FFF0F0 → #FDE8E8` |
| Zone border | `border-gray-800` | `#EED8D8` |
| Zone badge | `bg-blue-900/40 text-blue-300` | bg `#C8001D20` text `#9B0016` |
| Site row | `bg-gray-900/30` | `#F9F0F0` |
| Site border | `border-gray-800` | `#EED8D8` |
| Cell card | `bg-gray-50 border-gray-200/40` | `#FFFFFF border #EED8D8` |
| Cell type badge | `bg-gray-100 text-gray-600` | `#F5EDED text #7A4040` |
| Delete button | `text-red-400 hover:text-red-300` | `text-red-600 hover:text-red-800` |

## Regla de diseño para páginas de árbol/jerarquía

Usar siempre tonos rosados/crema del sistema en vez de grises puros:
- Fondo nivel 1 (zona): gradient suave #FFF0F0 → #FDE8E8 con borde #EED8D8
- Fondo nivel 2 (site): sólido #F9F0F0 con borde #EED8D8
- Fondo nivel 3 (cell/item): blanco #FFFFFF con borde #EED8D8
- Badges de conteo: bg #F5EDED text #7A4040 border #DCC8C8

---

## colorBadgeStyle v4 — rgba() con borde sutil (versión definitiva)

Usar `rgba()` en lugar de hex+alpha para compatibilidad garantizada:

```js
export const colorBadgeStyle = (colorCode) => {
  const clr = colorCode?.startsWith('#') ? colorCode : '#666666'
  const [r,g,b] = hexToRgb(clr)
  return {
    backgroundColor: `rgba(${r},${g},${b},0.12)`,  // 12% opacidad — muy suave
    color: `rgb(${Math.round(r*0.62)},${Math.round(g*0.62)},${Math.round(b*0.62)})`, // 62% tono
    borderColor: `rgba(${r},${g},${b},0.45)`,        // 45% opacidad — sutil
    border: '1px solid',
    fontWeight: '600',
  }
}
```

Resultado para Backup Local Missing #b91c1c:
- bg: rgba(185,28,28,0.12) → rosado muy suave
- text: rgb(115,17,17) → bordo oscuro legible
- border: rgba(185,28,28,0.45) → borde rosado sutil

## Colores definitivos Localizaciones

| Nivel | Fondo | Borde |
|-------|-------|-------|
| Zone (nivel 1) | #FEF2F2 (rojo muy suave — identidad) | #FECACA |
| Site (nivel 2) | #F3F4F6 (gris neutro — como thead tablas) | #E5E7EB |
| Cell (nivel 3) | #FFFFFF (blanco) | #E5E7EB |
| Zone badge | rgba(#C8001D, 8%) text #9B0016 | #C8001D60 |
| Site/Cell badge | #F3F4F6 text #374151 | #D1D5DB |

## ExceptionsPage — banner info

```jsx
// ❌ ANTES (invisible en tema claro):
<div className="card p-4 border-blue-800 bg-blue-950/20 text-blue-300 ...">

// ✅ DESPUÉS (legible):
<div className="card p-4 ..." style={{backgroundColor:"#EFF6FF", border:"1px solid #BFDBFE"}}>
  <p className="font-medium text-blue-800">¿Para qué sirven...</p>
  <p className="text-xs text-blue-700">...</p>
```

## Regla: selector de indicador en ExceptionsPage

```jsx
className={`... ${indicator === ind
  ? 'bg-primary text-white border-primary'           // activo: fondo rojo + texto blanco
  : 'bg-white text-gray-700 border-gray-300 hover:border-primary hover:text-primary'  // inactivo
}`}
```

---

## Bug raíz del contraste de etiquetas — getBadgeClass dark-mode

**Causa encontrada:** `getTagComplianceClass()` en `ComplianceBadge.jsx` retorna clases
CSS de `getBadgeClass()`. Cuando estas clases no están vacías, el `style={colorBadgeStyle()}`
de `TagBadge` se ignora completamente (`style={complianceCls ? {} : style}`).
`getBadgeClass` usaba colores dark-mode invisibles en tema claro.

```js
// ❌ ANTES (invisible en tema claro):
if (state === 'ok')  return 'bg-green-900/60 text-green-300 border-green-700'
return 'bg-red-900/60 text-red-300 border-red-700'

// ✅ DESPUÉS (legible en tema claro):
if (state === 'ok')  return 'bg-green-100 text-green-800 border-green-500 font-semibold'
return 'bg-red-100 text-red-800 border-red-500 font-semibold'
```

Los gradientes de compliance semánticos (ok_with_exception, ko_with_exception)
se mantienen igual ya que usan `text-white` sobre gradiente oscuro — correcto.
