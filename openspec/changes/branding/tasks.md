# Tasks: Branding Corporativo

## 1. Nomenclatura

- [ ] 1.1 Sustituir "TFG CMDB" por "Inventario Centralizado" en Layout.jsx (sidebar)
- [ ] 1.2 Actualizar `<title>` en index.html: `<title>Inventario Centralizado</title>`
- [ ] 1.3 Sustituir en la página de login (LoginPage en main.jsx)
- [ ] 1.4 Buscar y reemplazar cualquier otra ocurrencia en el código frontend

## 2. Logo

- [ ] 2.1 Descargar el escudo oficial del Ayuntamiento de SSReyes y guardarlo en `frontend/public/logo-ssreyes.png`
- [ ] 2.2 Mostrar el logo en la parte superior del sidebar con `<img>` y alt text accesible
- [ ] 2.3 Implementar fallback: si la imagen falla (`onError`), ocultar el `<img>` sin romper el layout

## 3. Paleta de colores

- [ ] 3.1 Actualizar `tailwind.config.js`: `primary: { DEFAULT: '#003F7F', dark: '#005BAA' }`
- [ ] 3.2 Añadir `corporate: { gold: '#C8963E' }` en la paleta de Tailwind
- [ ] 3.3 Actualizar badge de rol "admin" para usar el dorado corporativo
- [ ] 3.4 Revisar contraste en modo oscuro: verificar que el azul #003F7F es legible sobre gray-800/900
- [ ] 3.5 Ajustar `focus:ring-primary` y `bg-primary/20` con el nuevo color para que los fondos semi-transparentes sigan siendo sutiles
