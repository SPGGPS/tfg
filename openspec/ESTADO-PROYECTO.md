# Estado del proyecto — Inventario Centralizado (CMDB)
**Última actualización:** 2026-03-25 (Sophos EDR integration)
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
- Tipos: `server_physical`, `server_virtual`, `workstation`, `vcenter`, `switch`, `router`, `firewall`, `load_balancer`, `ap`, `storage_array`, `database`, `web_server`, `k8s_cluster`, `container`
- Compliance: `edr_installed`, `monitored`, `siem_enabled`, `logs_enabled`, `last_backup_local`, `last_backup_cloud`
- FK: `cell_id` → Cell (localización física)
- `source`: origen del asset (`vmware-vcenter`, `sophos-edr`, `veeam`, `manual`, etc.)
- `created_by`: nombre del usuario que dio de alta el asset (solo `source='manual'`)
- **Backup (Veeam):** `backup_job_name`, `backup_last_status` (Success/Warning/Failed), `backup_restore_points`
- **EDR (Sophos):** `edr_endpoint_id`, `edr_health` (good/suspicious/bad/unknown), `edr_last_seen`, `edr_tamper_protected`, `detected_services` (JSON: web_servers, databases, web_ports, db_ports)

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
| `/inventario` | InventoryPage (tabs: Inventario / Certificados) | viewer |
| `/certificates` | CertificatesPage | viewer |
| `/assets/:id` | AssetDetailPage | viewer |
| `/cmdb/servers` | ServersPage — físicos/virtuales/vCenters con modal de relaciones | viewer |
| `/cmdb/network` | NetworkPage — switches/routers/firewalls/LBs/APs con tabs por tipo | viewer |
| `/cmdb/databases` | DatabasesPage — instancias DB con barra de conexiones y HA | viewer |
| `/cmdb/web-servers` | WebServersPage — web servers con virtual hosts y SSL | viewer |
| `/cmdb/kubernetes` | KubernetesPage — clusters K8s y contenedores Docker | viewer |
| `/applications` | Gestión de Servicios (tabs: Servicios / Aplicaciones / Mapa) | viewer |
| `/tags` | TagsPage | admin |
| `/locations` | LocationsPage (Zona→Site→Cell + bulk assign) | admin |
| `/data-sources` | DataSourcesPage | admin |
| `/exceptions` | ExceptionsPage (bulk select + sort) | admin |
| `/audit` | AuditPage | admin |
| `/profile` | ProfilePage | viewer |

### InventoryPage — funcionalidades de gestión manual
- **Alta manual**: botón "+ Nuevo activo" (editor/admin) → modal con campos por tipo + validación IP en tiempo real
- **Baja manual**: icono papelera en columna de acciones → solo para `source='manual'`, pide confirmación
- **Identificación visual**: badge ámbar "MANUAL" junto al nombre + SourceBadge ámbar con ✏️
- **Última sync**: para assets manuales muestra "✏️ \<usuario\>" en lugar de fecha de sincronización

---

## API endpoints principales

```
GET                 /v1/assets                    — lista paginada con filtros y ordenación
GET                 /v1/assets/{id}               — detalle (detail=True)
POST                /v1/assets/ingest             — bulk upsert (admin); auto-rellena created_by si manual
DELETE              /v1/assets/{id}               — eliminar asset (solo source='manual', editor+)
POST                /v1/assets/bulk-tags          — asignación masiva de etiquetas
POST                /v1/assets/bulk-untag         — quitar etiquetas de assets
GET                 /v1/assets/history/snapshots  — snapshots históricos (hourly, 365d retención)
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

## Data Integrations (`/Desktop/data-integrations/`)

Repositorio separado con scripts de extracción de datos de fuentes externas. Cada integración tiene su propio directorio con script, `requirements.txt`, `config.example.env` y `openspec/tasks.md`.

### Integración VMware vSphere 8 (`vmware-vcenter/`)
- **`vmware_extract.py`** — pyVmomi: extrae vCenter + ESX hosts + VMs → CMDB
- ID estable: `vc-<host>`, `host-<fqdn>`, `vm-<moId>`
- Campos: vendor, model, serial, CPU, RAM, IPs, OS, datacenter, cluster, VM power state, tools version, datastore, folder
- Airflow DAG: `vmware_vcenter_sync` → `0 */4 * * *`

### Integración Veeam B&R 13 (`veeam-backup/`)
- **`veeam_extract.ps1`** — PowerShell en el servidor Veeam: extrae jobs + restore points + estado última sesión → JSON
- **`veeam_push.py`** — Python: lee el JSON y actualiza `last_backup_local`, `backup_job_name`, `backup_last_status`, `backup_restore_points` en CMDB
- Airflow DAG: `veeam_backup_sync` → `30 */4 * * *` (SSHOperator + PythonOperator)

### Integración Sophos Central EDR (`sophos-edr/`)
- **`sophos_extract.py`** — OAuth2 + Endpoint API + Live Discover (osquery):
  - GET `/endpoint/v1/endpoints` → todos los endpoints EDR
  - Live Discover query 1: `system_info` → cpu_count, ram_gb
  - Live Discover query 2: `processes` (web) → detecta nginx, apache, IIS, tomcat...
  - Live Discover query 3: `processes` (DB) → detecta postgresql, mysql, mssql, oracle, mongodb...
  - Live Discover query 4: `listening_ports` → puertos web/DB abiertos
  - Resultado: campo `detected_services` JSON por asset
- Airflow DAG: `sophos_edr_sync` → `15 */4 * * *` (entre VMware :00 y Veeam :30)

### Airflow DAGs (`airflow/dags/`)
| DAG | Schedule | Descripción |
|-----|----------|-------------|
| `vmware_vcenter_sync` | `0 */4 * * *`  | Extrae vCenter+ESX+VMs |
| `sophos_edr_sync`     | `15 */4 * * *` | Extrae endpoints EDR + detecta servicios |
| `veeam_backup_sync`   | `30 */4 * * *` | Extrae estado backups Veeam |

---

## Pendiente

- [ ] Backend: tests unitarios (change `unit-test`)
- [ ] Frontend: conectar CertificatesPage y InfraBindings con backend cuando esté completo
- [ ] Apache Flow: sincronización automática de datos PKI
- [ ] Mapa topología: Layered View (carriles horizontales por tier)
- [ ] Confirmar hex exacto del rojo corporativo SSReyes (actualmente `#C8001D` por aproximación)
- [ ] Integración Zabbix (monitorización) — DAG pendiente
- [ ] Integración CrowdStrike / SentinelOne — DAG pendiente

---

## Reglas de desarrollo (no romper)

1. **Enums SQLAlchemy** → siempre serializar con `str(val).split(".")[-1]` en `to_dict()`
2. **TanStack v5 mutations** → nunca pasar `.mutate` directamente como prop; envolver en `d => mut.mutate(d)`
3. **Rules of Hooks** → nunca dentro de objetos `{}`, condiciones `&&`, o bucles
4. **Rutas FastAPI** → rutas estáticas ANTES de rutas con parámetro (ej. `/cells/bulk-assign` antes de `/cells/{id}`)
5. **invalidateQueries** → usar `{queryKey:[...], exact:false}` para invalidar queries con params
6. **Compliance colors** → los 4 estados y sus gradientes son semánticos, NO modificar con branding
7. **api.js** → actualizar siempre que se refactorice un modelo de backend
