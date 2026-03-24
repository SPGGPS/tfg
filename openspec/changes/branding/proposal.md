id: branding

# openspec/changes/branding/.openspec.yaml
schema: spec-driven
created: 2026-03-15

# Contexto: Identidad visual corporativa
context: |
  Feature: Branding corporativo Ayuntamiento de San Sebastián de los Reyes
  Domain: Identidad visual y nomenclatura de la aplicación.
  Referencia: https://www.ssreyes.org — web corporativa del Ayuntamiento.
  El sistema de inventario es una herramienta interna del Ayuntamiento, por lo que
  debe reflejar la identidad visual institucional: paleta de colores corporativa,
  logo oficial, y nombre que identifique el propósito real de la herramienta.

# Definición del Cambio
proposal: |
  Aplicar identidad visual corporativa del Ayuntamiento de San Sebastián de los Reyes:
  1. Nombre: sustituir "TFG CMDB" por "Inventario Centralizado" en toda la UI.
  2. Logo: mostrar el escudo/logo oficial del Ayuntamiento de San Sebastián de los Reyes
     en la esquina superior izquierda del sidebar. El logo se carga desde una URL pública
     de la web corporativa (https://www.ssreyes.org) o se almacena como asset estático.
  3. Paleta de colores: adoptar los colores corporativos de ssreyes.org como colores
     primarios de la aplicación, sustituyendo el indigo (#6366f1) actual.
  4. Tipografía y estilo general: alineado con el estilo institucional de la web de referencia.

# Reglas de implementación
rules:
  frontend_code:
    - Nombre de la app en sidebar, título del navegador (document.title), página de login
      y cualquier texto que diga "TFG CMDB" SHALL sustituirse por "Inventario Centralizado".
    - El header del sidebar SHALL mostrar: escudo (48×48px) + "Ayuntamiento de San Sebastián
      de los Reyes" (text-xs) + "Inventario Centralizado" (text-[10px] text-blue-200).
      Logo URL: https://www.ssreyes.org/o/ayto-ssreyes-theme/images/logo-ssreyes.png
      Alternativa estable: asset estático en frontend/public/logo-ssreyes.png.
      Fallback si no carga: SVG escudo inline en azul #003F7F y dorado #C8963E.
    - tailwind.config.js SHALL definir:
        primary: { DEFAULT:'#003F7F', hover:'#004F9F', dark:'#002B5C', light:'#E8F0FB' }
        corporate: { gold:'#C8963E', red:'#C0392B' }
    - index.css SHALL definir las CSS variables correspondientes.
    - Fondo del sidebar completo: #002B5C. Header del sidebar: #003F7F.
    - Item de nav activo: bg-white/20 + borde izquierdo 3px solid #C8963E.
    - Topbar: fondo #002B5C, borde inferior border-blue-800.
    - Página de login: fondo gradiente #001A3A → #002B5C, logo centrado 80×80px,
      texto institucional, botón azul corporativo.
    - Contraste WCAG AA (≥4.5:1) obligatorio en todos los textos sobre fondos azules.

# Dependencias
dependencies:
  - app-core  # afecta al scaffold base de la UI

# Desglose de tareas
tasks:
  - name: "Sustituir nombre TFG CMDB → Inventario Centralizado en toda la UI"
    hours: 0.5
  - name: "Añadir logo Ayuntamiento SSReyes en sidebar (con fallback a texto)"
    hours: 1
  - name: "Actualizar paleta primaria en tailwind.config.js y CSS variables"
    hours: 1
  - name: "Revisar contraste y legibilidad en modo oscuro con nueva paleta"
    hours: 1
