# Frontend - Branding Corporativo (Ayuntamiento SSReyes)

## ADDED Requirements

### Requirement: Nombre de la aplicación — "Inventario Centralizado"
Toda referencia al nombre "TFG CMDB" en la interfaz SHALL sustituirse por **"Inventario Centralizado"**. Esto incluye:
- Texto del sidebar (parte superior)
- `<title>` del documento HTML (`<title>Inventario Centralizado</title>`)
- Página de login
- Cualquier heading, tooltip o texto visible que mencione el nombre anterior

#### Scenario: Nombre correcto en todas las superficies
- **GIVEN** cualquier usuario que abre la aplicación
- **WHEN** visualiza la página de login, el sidebar o la pestaña del navegador
- **THEN** ve "Inventario Centralizado", nunca "TFG CMDB" ni "TFG"

---

### Requirement: Logo del Ayuntamiento de San Sebastián de los Reyes en el sidebar
El sidebar SHALL mostrar el logo/escudo oficial del Ayuntamiento de San Sebastián de los Reyes en su parte superior izquierda, encima del nombre "Inventario Centralizado".

Especificaciones:
- **Fuente del logo**: imagen estática almacenada como asset en `frontend/public/logo-ssreyes.png` (o SVG). El logo se obtiene de la web corporativa https://www.ssreyes.org — es el escudo municipal oficial.
- **Tamaño**: 40×40px, con `object-fit: contain`.
- **Fallback**: si la imagen no carga, mostrar únicamente el texto "Inventario Centralizado" sin romper el layout.
- **Alt text**: `"Escudo Ayuntamiento de San Sebastián de los Reyes"` para accesibilidad.

#### Scenario: Logo visible en sidebar
- **GIVEN** cualquier usuario autenticado
- **WHEN** visualiza el sidebar
- **THEN** ve el escudo del Ayuntamiento de SSReyes seguido del texto "Inventario Centralizado"

#### Scenario: Fallback cuando el logo no carga
- **GIVEN** la imagen del logo no está disponible
- **WHEN** se renderiza el sidebar
- **THEN** solo aparece el texto "Inventario Centralizado" sin ningún elemento roto

---

### Requirement: Paleta de colores corporativa del Ayuntamiento SSReyes
La paleta de colores primaria de la aplicación SHALL reflejar la identidad visual de https://www.ssreyes.org. Los colores corporativos son:

| Token | Color hex | Uso |
|-------|-----------|-----|
| `primary.DEFAULT` | `#003F7F` | Azul corporativo — botones primarios, links activos, focus rings |
| `primary.dark` | `#005BAA` | Hover de botones primarios |
| `primary.light` | `#E8F0FB` | Fondos sutiles en modo claro |
| `corporate.gold` | `#C8963E` | Acentos dorados — badge Admin, indicadores especiales |

La paleta de grises de fondo (gray-950, gray-900, gray-800…) se mantiene para preservar el modo oscuro. Solo se sustituye el color `primary` (actualmente indigo #6366f1).

#### Scenario: Botones primarios con azul corporativo
- **GIVEN** cualquier página de la aplicación
- **WHEN** un usuario visualiza un botón primario (Crear, Guardar, Asignar…)
- **THEN** el botón tiene el color azul corporativo #003F7F, no el indigo anterior

#### Scenario: Badge de rol "Admin" con dorado corporativo
- **GIVEN** un usuario con rol admin en el header o página de perfil
- **WHEN** se muestra el badge de rol
- **THEN** el badge "admin" usa el dorado corporativo #C8963E

#### Scenario: Links y elementos activos del sidebar
- **GIVEN** un usuario navegando por la aplicación
- **WHEN** un ítem del sidebar está activo
- **THEN** usa el azul corporativo #003F7F como color de resaltado

---

### Requirement: Coherencia visual con ssreyes.org
El estilo general de la UI (fondos, bordes, tipografía) SHALL mantener coherencia con la web institucional de referencia, dentro de las limitaciones del modo oscuro. Criterios:
- Tipografía: usar una fuente sans-serif limpia y legible (la actual es adecuada).
- Bordes y radios: conservativos, no excesivamente redondeados (el estilo institucional es formal).
- Lenguaje formal en todos los textos de la UI (ya cumplido al estar en español).

#### Scenario: Estilo formal institucional
- **GIVEN** cualquier página de la aplicación
- **WHEN** un usuario la visualiza
- **THEN** el estilo es formal, limpio y coherente con una aplicación corporativa municipal, no con una startup tech
