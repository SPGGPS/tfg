# OpenSpec v2 — Inventario Centralizado SSReyes

Documentación técnica reproducible del proyecto CMDB del Ayuntamiento de San Sebastián de los Reyes.
Versión: 1.0.0 · Estado: released · Fecha: 2026-03-22

---

## ¿Qué es OpenSpec?

Cada *change* describe una funcionalidad del sistema en tres capas:
- `specs/api/spec.md` — contratos de la API REST (endpoints, request/response)
- `specs/backend/spec.md` — modelos SQLAlchemy, lógica de negocio, servicios
- `specs/frontend/spec.md` — componentes React, estados, colores, interacciones

Esto hace cada feature reproducible desde cero.

---

## Changes implementados (v1.0)

| Change | Estado | Descripción |
|--------|--------|-------------|
| `inventory-master` | ✅ | Módulo principal de inventario: listado, filtros, compliance badges, etiquetas |
| `branding` | ✅ | Tema corporativo SSReyes: rojo #C8001D, paleta cálida, colorBadgeStyle |
| `certificates` | ✅ | Gestión TLS/SSL: estados, caducidades, banner de alerta |
| `applications` | ✅ | Aplicaciones, servicios, mapa de dependencias SVG |
| `exceptions` | ✅ | Excepciones de compliance: creación, revocación, auditoría |
| `locations` | ✅ | Árbol jerárquico Zona→Site→Celda, asignación de activos |
| `tags-management` | ✅ | Etiquetas sistema y manuales, asignación/eliminación masiva |
| `eol` | ✅ | End of Life: sync endoflife.date, ciclos, etiquetas EOL KO/WARN/OK, matching OS/DB/firmware |
| `dashboard` | ✅ | Dashboard con gráficos SVG, filtros URL, bloque servicios |
| `audit-logs` | ✅ | Log de auditoría con filtros |
| `data-sources` | ✅ | Fuentes de datos con badges visuales |
| `login` | ✅ | Auth Keycloak OIDC+PKCE / SKIP_AUTH para dev |
| `user-profile` | ✅ | Perfil de usuario, preferencias |
| `infrastructure` | ✅ | Bindings infraestructura app-asset con tipo y puerto |
| `unit-tests` | ✅ | 58 tests integración OK · E2E marcados v2.0 (requieren CI) |

---

## Reglas de diseño consolidadas

### Backend
- Enums siempre serializados: `str(self.x).split(".")[-1]`
- IntegrityError → 409 (nunca 500)
- Rutas estáticas ANTES de rutas dinámicas en FastAPI (`/expiry-summary` antes de `/{id}`)
- `Query` de FastAPI debe importarse explícitamente: `from fastapi import ..., Query`

### Frontend — badges
```js
// Patrón obligatorio para todos los badges en tema claro:
'bg-X-100 text-X-800 border border-X-400/500 font-semibold'

// NUNCA:
'bg-X-900/60 text-X-300'  // dark-mode invisible
'bg-X-900/40 text-X-200'  // dark-mode invisible
```

### colorBadgeStyle (etiquetas dinámicas)
```js
export const colorBadgeStyle = (colorCode) => {
  const [r,g,b] = hexToRgb(clr)
  return {
    backgroundColor: `rgba(${r},${g},${b},0.12)`,
    color: `rgb(${Math.round(r*0.62)},${Math.round(g*0.62)},${Math.round(b*0.62)})`,
    borderColor: `rgba(${r},${g},${b},0.45)`,
    border: '1px solid', fontWeight: '600',
  }
}
```

### Compliance badge states
- `ok` → verde · `ok_with_exception` → gradiente azul/verde · `ko_with_exception` → gradiente rojo/azul · `ko` → rojo
- El texto del badge `ko_with_exception` es **KO** (no EXC)

### Colores del dashboard
- EOL: `#dc2626` KO · `#d97706` WARN · `#16a34a` OK · `#cbd5e1` Sin datos
- Compliance: `#16a34a` ok · `#1d4ed8` ok_exc · `#7c3aed` ko_exc · `#ef4444` ko
- Servicios: `#16a34a` activo · `#f97316` degradado · `#d97706` mantenimiento · `#94a3b8` inactivo

### Rutas frontend
- `/dashboard` → página de inicio (index)
- `/inventario` → inventario de activos (con soporte ?search=X&type=Y)
- `/certificates` → certificados TLS
- `/applications` → servicios + apps + mapa (con ?tab=mapa&service_id=UUID)

### Swagger UI (/docs)
El middleware `SecureHeadersMiddleware` aplica CSP relajado para `/docs`, `/redoc` y `/v1/openapi.json`,
permitiendo los scripts inline y CDN necesarios para Swagger UI.

---

## Bugs críticos corregidos (v1.1 → v1.2)

### asset.py — to_dict() retornaba None
`_get_cell_full_path()` se insertó en medio de `to_dict()` rompiendo el `return d`.
Todos los endpoints que usaban `to_dict()` fallaban silenciosamente.
**Fix**: `_get_cell_full_path` es ahora un método separado después de `to_dict`.

### EolPage — badge EOL OK no clickable
El badge "✓ N OK" era un `<span>` sin `onClick`. Los badges KO y WARN sí eran `<button>`.
**Fix**: convertido a `<button>` con `setAssetsModal({..., status:'ok'})`.

### main.py — NameError: app/Depends no definidos
El endpoint `@app.post("/v1/admin/reseed")` se añadió antes de `app = FastAPI()`
y sin importar `Depends` y `HTTPException`.
**Fix**: movido al final del archivo + imports añadidos.

### _build_graph — AppEnvironment.production en nodos
`str(app.environment)` devolvía `"AppEnvironment.production"` en los nodos del grafo.
**Fix**: `str(app.environment).split(".")[-1]` en todos los campos enum.

### dashboard.py — total_services hardcodeado a 0
**Fix**: `len(db.query(Service).all())` calculado en cada request.

## Convenciones establecidas (NO romper)

```python
# Enums SIEMPRE con split:
str(self.x).split(".")[-1]

# Métodos auxiliares SIEMPRE fuera de to_dict:
def to_dict(self):
    d = {...}
    return d           # ← return ANTES del siguiente método

def _helper(self):     # ← método separado
    ...
```
