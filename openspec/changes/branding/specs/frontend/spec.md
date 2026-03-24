# Frontend — Branding Corporativo (Ayuntamiento SSReyes)

> **Color corporativo:** el Ayuntamiento de San Sebastián de los Reyes usa **rojo** como color principal, no azul. El branding anterior (azul `#003F7F`) era incorrecto.

---

### Requirement: Paleta de colores — rojo corporativo SSReyes

**`tailwind.config.js` — tokens exactos implementados:**

```js
primary: {
  DEFAULT: '#C8001D',   // rojo corporativo principal
  hover:   '#A8001A',   // hover
  dark:    '#8B0016',   // versión oscura
  light:   '#FDECEA',   // fondo tenue para selecciones
},
corporate: {
  red:    '#C8001D',
  red2:   '#E8001F',
  cream:  '#FFF8F8',
  border: '#E5E7EB',
},
surface: {
  body:   '#F4F5F7',    // fondo general
  card:   '#FFFFFF',    // cards
  row:    '#F9FAFB',    // filas alternas
  input:  '#FFFFFF',    // inputs
  hover:  '#FFF1F2',    // hover fila
}
```

---

### Requirement: index.css — reglas base implementadas

```css
body { background-color: #F4F5F7; color: #111827; }

/* Scrollbar */
::-webkit-scrollbar-track { background: #F4F5F7; }
::-webkit-scrollbar-thumb { background: #C8001D; }
::-webkit-scrollbar-thumb:hover { background: #A8001A; }

/* Botones */
.btn-primary         { background-color: #C8001D; color: white; }
.btn-primary:hover   { background-color: #A8001A; }
.btn-secondary       { background: #FFFFFF; border: 1px solid #D1D5DB; color: #374151; }
.btn-secondary:hover { background: #F9FAFB; }
.btn-danger          { background-color: red-700; }

/* Cards */
.card { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 0.75rem; }

/* Inputs */
.input { background: #FFFFFF; border: 1px solid #D1D5DB; color: #111827; }
.input:focus { border-color: #C8001D; box-shadow: 0 0 0 2px rgba(200,0,29,0.15); }

/* Sidebar */
.sidebar-item  { color: rgba(255,255,255,0.80); border-left: 3px solid transparent; }
.sidebar-item:hover { background: rgba(255,255,255,0.12); color: white; }
.sidebar-active { background: rgba(255,255,255,0.18); border-left: 3px solid #FFD6D6; color: white; }

/* Tablas */
.table-row-alt:nth-child(even) { background-color: #F9FAFB; }
.table-row-alt:hover           { background-color: #FFF1F2 !important; }
```

---

### Requirement: Sidebar y topbar — rojo corporativo

- Fondo: `#C8001D`
- Item activo: fondo `rgba(255,255,255,0.18)` + borde izquierdo `#FFD6D6`
- Texto items: `rgba(255,255,255,0.80)`

---

### Requirement: Tablas — filas alternas

- Filas pares: `#F9FAFB`
- Hover: `#FFF1F2` (tinte rojo muy suave)
- Clase: `.table-row-alt` con `:nth-child(even)` y `:hover`

---

### Requirement: Compliance — colores semánticos intactos

Los gradientes de compliance usan el rojo corporativo como color de excepción:

```css
/* OK + excepción: rojo corporativo → verde */
.compliance-gradient      { background: linear-gradient(135deg, #C8001D 50%, #1a6b3a 50%); }
/* KO + excepción: rojo corporativo → rojo oscuro */
.compliance-gradient-temp { background: linear-gradient(135deg, #C8001D 50%, #C0392B 50%); }
```

**4 estados de compliance:**
| Estado | Color | Condición |
|--------|-------|-----------|
| `ok` | Verde `bg-green-900/60` | Origen OK, sin excepción |
| `ok_with_exception` | Gradiente rojo→verde | Origen OK + excepción activa |
| `ko_with_exception` | Gradiente rojo→rojo oscuro | Origen KO + excepción justificada |
| `ko` | Rojo `bg-red-900/60` | Origen KO sin excepción |

Los badges de compliance (verde, rojo, gradientes) y los colores de servicios **NO se modifican** con el branding.

---

### Requirement: Logo SSReyes

- Archivo: `public/logo-ssreyes.png` — logo oficial del Ayuntamiento
- Aplicado con `filter: brightness(0) invert(1)` para que aparezca en blanco sobre el sidebar rojo

---

### Nota sobre el hex exacto

`#C8001D` es la aproximación al rojo corporativo. Para actualizarlo basta cambiar `primary.DEFAULT` en `tailwind.config.js` y `#C8001D` en `index.css`.
