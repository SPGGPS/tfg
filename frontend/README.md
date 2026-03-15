# TFG Frontend (React + Vite + Tailwind)

Aplicación React para gestión de inventario y auditoría.

## Características

- **Dashboard de Inventario**: Vista de activos con filtros y historificación
- **Gestión de Etiquetas**: CRUD de etiquetas con asignación masiva
- **Auditoría**: Panel admin-only para revisar logs de auditoría con filtros
- **Autenticación**: Login simulado con roles (admin/editor/viewer)

## Requisitos

- Node.js 18+

## Instalación

```bash
cd frontend
npm install
```

## Ejecución

```bash
npm run dev
```

## Variables de entorno

Crear `.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

## Rutas

- `/` - Dashboard de inventario
- `/audit` - Panel de auditoría (solo admin)
- `/login` - Página de login

- App: http://localhost:5173
- El proxy envía `/v1/*` al backend en http://localhost:8000

## Próximos pasos

- Integrar Keycloak (OIDC + PKCE)
- Tokens en cookie HttpOnly/Secure
- Dashboard de inventario con tabla y filtros
- Selector histórico (Live / hora pasada)
- UI de etiquetas y badges de compliance
