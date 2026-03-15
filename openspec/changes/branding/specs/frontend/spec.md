# Frontend - Branding Corporativo (Ayuntamiento SSReyes)

## ADDED Requirements

### Requirement: Nombre de la aplicación — "Inventario Centralizado"
Toda referencia al nombre "TFG CMDB" en la interfaz SHALL sustituirse por **"Inventario Centralizado"**. Esto incluye:
- Texto del sidebar (parte superior)
- `<title>` del documento HTML (`<title>Inventario Centralizado — Ayuntamiento de San Sebastián de los Reyes</title>`)
- Página de login
- Cualquier heading, tooltip o texto visible que mencione el nombre anterior

#### Scenario: Nombre correcto en todas las superficies
- **GIVEN** cualquier usuario que abre la aplicación
- **WHEN** visualiza la página de login, el sidebar o la pestaña del navegador
- **THEN** ve "Inventario Centralizado", nunca "TFG CMDB" ni "TFG"

---

### Requirement: Logo y cabecera del sidebar — estilo ssreyes.org
El sidebar SHALL mostrar en su parte superior el logo oficial del Ayuntamiento de San Sebastián de los Reyes con un estilo consistente con la web corporativa.

**Estructura del header del sidebar:**
```
┌────────────────────────────────────────┐
│  [ESCUDO]  Ayuntamiento de             │
│            San Sebastián de los Reyes  │
│  ──────────────────────────────────    │
│  Inventario Centralizado               │
└────────────────────────────────────────┘
```

**Logo / Escudo:**
- URL pública del logo: `https://www.ssreyes.org/o/ayto-ssreyes-theme/images/logo-ssreyes.png` (o URL equivalente de la web corporativa). Si la URL falla, usar el SVG embebido del escudo heráldico como fallback (ver abajo).
- Como alternativa estable, almacenar el logo como asset estático en `frontend/public/logo-ssreyes.png`.
- Tamaño: 48×48px, `object-fit: contain`.
- Alt text: `"Escudo Ayuntamiento de San Sebastián de los Reyes"`.

**SVG fallback del escudo** (para cuando no carga la imagen): un escudo heráldico simplificado con corona, en azul corporativo `#003F7F` y dorado `#C8963E`. Mínimo reconocible como escudo municipal.

**Texto junto al logo:**
- Línea 1: `"Ayuntamiento de San Sebastián de los Reyes"` — `text-xs font-semibold text-white leading-tight`
- Línea 2: `"Inventario Centralizado"` — `text-[10px] text-blue-200 opacity-80`

**Fondo del header del sidebar:**
- Color de fondo: `#003F7F` (azul corporativo). El sidebar usa este azul en la cabecera, con el resto del sidebar en `#002B5C` (azul más oscuro).
- Separador inferior: línea `border-b border-blue-800`.

#### Scenario: Logo visible en sidebar
- **GIVEN** cualquier usuario autenticado
- **WHEN** visualiza el sidebar
- **THEN** ve el escudo del Ayuntamiento, "Ayuntamiento de San Sebastián de los Reyes" e "Inventario Centralizado"

#### Scenario: Fallback cuando el logo no carga
- **GIVEN** la imagen del logo no está disponible
- **WHEN** se renderiza el sidebar
- **THEN** aparece el SVG fallback del escudo o solo el texto, sin ningún elemento roto

---

### Requirement: Paleta de colores corporativa del Ayuntamiento SSReyes
La paleta de la aplicación SHALL reflejar fielmente la identidad visual de https://www.ssreyes.org.

**Colores principales extraídos de ssreyes.org:**

| Token Tailwind | Hex | Uso |
|----------------|-----|-----|
| `primary` (DEFAULT) | `#003F7F` | Azul corporativo — botones primarios, sidebar header, focus rings |
| `primary.hover` | `#004F9F` | Hover de botones y elementos interactivos primarios |
| `primary.dark` | `#002B5C` | Azul oscuro — fondo principal del sidebar, topbar |
| `primary.light` | `#E8F0FB` | Fondos sutiles azul claro (en modo claro) |
| `corporate.gold` | `#C8963E` | Dorado corporativo — badge Admin, acentos heráldicos |
| `corporate.red` | `#C0392B` | Rojo de acento institucional (usado en web ssreyes.org) |

**`tailwind.config.js`** — sección colors a añadir:
```js
primary: {
  DEFAULT: '#003F7F',
  hover:   '#004F9F',
  dark:    '#002B5C',
  light:   '#E8F0FB',
},
corporate: {
  gold: '#C8963E',
  red:  '#C0392B',
}
```

**CSS variables** en `index.css`:
```css
:root {
  --color-primary:       #003F7F;
  --color-primary-hover: #004F9F;
  --color-primary-dark:  #002B5C;
  --color-corporate-gold: #C8963E;
}
```

La paleta de grises de fondo (`gray-950`, `gray-900`, `gray-800`) se **mantiene** para el modo oscuro del contenido principal. Solo el sidebar y los elementos de marca usan los azules corporativos.

#### Scenario: Botones primarios con azul corporativo
- **GIVEN** cualquier página de la aplicación
- **WHEN** un usuario visualiza un botón primario (Crear, Guardar, Asignar…)
- **THEN** el botón tiene el color azul corporativo `#003F7F`, no el indigo anterior

#### Scenario: Sidebar con azules institucionales
- **GIVEN** un usuario autenticado en la aplicación
- **WHEN** visualiza el sidebar
- **THEN** el header del sidebar tiene fondo `#003F7F`, el resto del sidebar `#002B5C`, con texto blanco

#### Scenario: Badge de rol "Admin" con dorado corporativo
- **GIVEN** un usuario con rol admin
- **WHEN** se muestra el badge de rol en header o perfil
- **THEN** el badge "admin" usa el dorado corporativo `#C8963E`

---

### Requirement: Estilo del sidebar alineado con ssreyes.org
El sidebar SHALL tener un aspecto institucional alineado con la web del Ayuntamiento:

- **Fondo sidebar completo**: `#002B5C` (azul muy oscuro corporativo)
- **Items de navegación inactivos**: texto `text-blue-100 opacity-70`, hover `bg-white/10 opacity-100`
- **Item activo**: `bg-white/20 text-white font-semibold`, con borde izquierdo de 3px en dorado `#C8963E`
- **Separadores** entre secciones del nav: `border-blue-800/50`
- **Topbar**: fondo `#002B5C`, borde inferior `border-blue-800`

Esto reemplaza el esquema gris oscuro actual (`gray-900`, `gray-800`) en el sidebar por el azul institucional.

#### Scenario: Item activo con borde dorado
- **GIVEN** un usuario en la página de Inventario
- **WHEN** visualiza el sidebar
- **THEN** el ítem "Inventario" tiene fondo azul claro semitransparente y un borde izquierdo dorado de 3px

#### Scenario: Contraste WCAG en sidebar azul
- **GIVEN** texto blanco sobre fondo `#002B5C`
- **WHEN** se evalúa el contraste
- **THEN** el ratio de contraste es ≥ 4.5:1 (AA), cumpliendo WCAG 2.1

---

### Requirement: Página de login con identidad corporativa
La página de login SHALL mostrar:
- Logo/escudo del Ayuntamiento centrado, tamaño 80×80px
- Título: "Ayuntamiento de San Sebastián de los Reyes" en azul corporativo o blanco según el fondo
- Subtítulo: "Inventario Centralizado"
- Botón "Iniciar sesión" con azul corporativo `#003F7F`
- Texto legal mínimo: "Acceso restringido a personal autorizado del Ayuntamiento"
- Fondo de la página: degradado sutil de `#001A3A` a `#002B5C` (azules corporativos oscuros)

#### Scenario: Login con branding corporativo
- **GIVEN** un usuario no autenticado que accede a la aplicación
- **WHEN** se carga la página de login
- **THEN** ve el escudo del Ayuntamiento, el nombre institucional y el botón de acceso en azul corporativo

