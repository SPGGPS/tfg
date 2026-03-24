# Estado del proyecto — Inventario Centralizado (CMDB)
**Última actualización:** 2026-03-17  
**Código:** `tfg4/` | **Specs:** `openspec/changes/`

---

## Stack
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL (Python 3.11)
- **Frontend:** React 18 + Vite + Tailwind CSS + TanStack Query v5
- **Auth:** Keycloak OIDC+PKCE (`SKIP_AUTH=true` para dev)
- **Infra:** Docker Compose / Kubernetes Helm

## Arranque
```bash
cd tfg4 && docker-compose down -v && docker-compose up --build
# Frontend: http://localhost:5173 | Backend: http://localhost:8000/docs
```

---

## Modelos de datos

### Asset
- Tipos: `server_physical`, `server_virtual`, `switch`, `router`, `ap`, `database`
- Compliance: `edr_installed`, `monitored`, `siem_enabled`, `logs_enabled`, `last_backup_local`, `last_backup_cloud`
- FK: `cell_id` → Cell (localización física)

### Certificate (PKI)
- Campos: common_name, san_domains, expires_at (INDEX), ca_type, key_type, wildcard, auto_renew
- Estado calculado: `valid / expiring (≤30d) / critical (≤7d) / expired`

### Application → Service → ServiceEndpoint
- Application: `cell_id`, `location_path` (calculado), `tech_stack`, `owner_team`
- AppInfraBinding: `binding_tier` (10 tiers: entry_point→network), `is_critical`, `is_single_point_of_failure`, `redundancy_group`
- ServiceEndpoint: `certificate_id`, `tls_status` (calculado)

### Localizaciones (Zone → Site → Cell)
- **Zone:** agrupación lógica (ej. "Ayuntamiento SSReyes")
- **Site:** edificio/campus con dirección (ej. "Edificio Principal")
- **Cell:** CPD/rack/sala donde se asignan assets (ej. "Rack A", `cell_type`, `row_id`, `rack_unit`)
- Assets y Applications tienen FK `cell_id` → Cell

### ComplianceException
- `reason_code` (enum, serializar como string con `.split(".")[-1]`)
- `expires_at` nullable (null = permanente)

---

## Sistema de compliance — 4 estados

| Estado | CSS | Condición |
|--------|-----|-----------|
| `ok` | `bg-green-900/60 text-green-300` | Origen OK, sin excepción |
| `ok_with_exception` | `compliance-gradient` (azul→verde) | Origen OK + excepción activa |
| `ko_with_exception` | `compliance-gradient-temp` (azul→rojo) | Origen KO + excepción justificada |
| `ko` | `bg-red-900/60 text-red-300` | Origen KO sin excepción |

**Los gradientes usan azul semántico `#1d4ed8` — NO modificar con branding corporativo.**

---

## Branding SSReyes

| Token | Hex | Uso |
|-------|-----|-----|
| `primary` | `#C8001D` | Sidebar, topbar, botones primarios, scrollbar |
| `primary.hover` | `#A8001A` | Hover botones, topbar |
| Fondo body | `#FDF7F7` | Blanco rosado muy suave |
| Cards | `#FFFFFF` borde `#EED8D8` | Tarjetas y paneles |
| Filas alternas | `#FFF8F8` / hover `#FFEEEE` | Tablas |
| Btn secondary | `#FFF0F0` borde `#F0CCCC` | Botones secundarios |

**Logo:** `public/logo-ssreyes.png` con `filter: brightness(0) invert(1)` (blanco sobre sidebar rojo)

---

## Rutas frontend

| Ruta | Página | Rol |
|------|--------|-----|
| `/` | InventoryPage (tabs: Inventario / Certificados) | viewer |
| `/certificates` | CertificatesPage | viewer |
| `/assets/:id` | AssetDetailPage | viewer |
| `/applications` | Gestión de Servicios (tabs: Servicios / Aplicaciones / Mapa) | viewer |
| `/tags` | TagsPage | admin |
| `/locations` | LocationsPage (Zona→Site→Cell + bulk assign) | admin |
| `/data-sources` | DataSourcesPage | admin |
| `/exceptions` | ExceptionsPage (bulk select + sort) | admin |
| `/audit` | AuditPage | admin |
| `/profile` | ProfilePage | viewer |

---

## API endpoints principales

```
GET/POST/PUT/DELETE /v1/assets
GET                 /v1/assets/:id/impact
GET/POST/PUT/DELETE /v1/certificates
GET                 /v1/certificates/expiry-summary
GET/POST/PUT/DELETE /v1/applications
POST                /v1/applications/:id/infra-bindings
GET/POST/PUT/DELETE /v1/services
GET                 /v1/services/:id/dependency-graph
GET                 /v1/dependency-graph
GET/POST/PUT/DELETE /v1/zones | /v1/sites | /v1/cells
POST                /v1/cells/bulk-assign   ← ANTES de /v1/cells/{id} en el router
GET                 /v1/cells/:id/assets
GET                 /v1/locations/tree
GET/POST/PUT/DELETE /v1/exceptions
POST                /v1/exceptions (bulk: asset_ids[])
POST                /v1/exceptions/:id/revoke
GET/POST/PUT/DELETE /v1/tags
GET/POST/PUT/DELETE /v1/data-sources
GET                 /v1/audit-logs
```

---

## Bugs resueltos (referencia rápida)

| Bug | Causa | Fix |
|-----|-------|-----|
| "No mutationFn found" zonas | `api.js` tenía `locationsApi` con modelo antiguo (sin `createZone`) | Actualizar `api.js` con métodos Zone/Site/Cell |
| JSX build error `}}">"` | Sustitución masiva de colores generó comilla extra | Regex para limpiar `}}">`→`}}>` |
| JSX `className` duplicado | Sustitución parcial dejó `style={{...}} className="tracking-wider">` | Eliminar className extra tras style |
| Badge rojo en lugar de azul-rojo | `reason_code` devuelto como `"ExceptionReasonCode.foo"` en lugar de `"foo"` | `.split(".")[-1]` en todos los `to_dict()` |
| Tab Aplicaciones negro | `locList` no definido en scope de `AppForm` — query fuera del componente | Mover `useQuery` dentro de `AppForm` |
| Tab /certificates no navega | Ruta `certificates` faltaba en el Layout en `main.jsx` | Añadir `<Route path="certificates">` dentro del Layout |
| Grafo SVG vacío | `_build_graph` usaba `b.binding_type` (campo eliminado) | Cambiar a `b.binding_tier` |
| invalidateQueries no refresca | `invalidateQueries(['assets'])` no matchea `['assets', params]` | Usar `{queryKey:['assets'], exact:false}` |
| "No mutation found" en objetos | `useMutation` dentro de objeto literal `{create: useMutation(...)}` | Declarar cada mutación en nivel superior del componente |
| `useMutation` condicional | Componente con hooks dentro de `{condition && <Comp/>}` | Siempre montar el componente, guard con `enabled:false` |

---

## Pendiente

- [ ] Backend: tests unitarios (change `unit-test`)
- [ ] Frontend: conectar CertificatesPage y InfraBindings con backend cuando esté completo
- [ ] Apache Flow: sincronización automática de datos PKI
- [ ] Mapa topología: Layered View (carriles horizontales por tier)
- [ ] Confirmar hex exacto del rojo corporativo SSReyes (actualmente `#C8001D` por aproximación)

---

## Reglas de desarrollo (no romper)

1. **Enums SQLAlchemy** → siempre serializar con `str(val).split(".")[-1]` en `to_dict()`
2. **TanStack v5 mutations** → nunca pasar `.mutate` directamente como prop; envolver en `d => mut.mutate(d)`
3. **Rules of Hooks** → nunca dentro de objetos `{}`, condiciones `&&`, o bucles
4. **Rutas FastAPI** → rutas estáticas ANTES de rutas con parámetro (ej. `/cells/bulk-assign` antes de `/cells/{id}`)
5. **invalidateQueries** → usar `{queryKey:[...], exact:false}` para invalidar queries con params
6. **Compliance colors** → los 4 estados y sus gradientes son semánticos, NO modificar con branding
7. **api.js** → actualizar siempre que se refactorice un modelo de backend
