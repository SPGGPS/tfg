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
    - El logo del Ayuntamiento SHALL mostrarse en la parte superior izquierda del sidebar,
      encima del nombre "Inventario Centralizado". Tamaño aproximado 40×40px. Si el logo
      externo no carga, mostrar solo el texto como fallback.
    - La paleta primaria SHALL actualizarse a los colores corporativos de ssreyes.org:
        * Azul corporativo principal: #003F7F (azul oscuro institucional)
        * Azul secundario / hover: #005BAA
        * Dorado/ámbar corporativo (acentos): #C8963E
        * Texto sobre fondo oscuro: conservar la legibilidad con fondos gray-900/950
    - El color `primary` en tailwind.config.js SHALL apuntar al azul corporativo #003F7F.
    - Los badges de rol "admin" pueden usar el dorado corporativo en lugar del rojo.

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
