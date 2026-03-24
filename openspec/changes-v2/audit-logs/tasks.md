# Tasks: Audit Logs

## 1. DB y Backend
- [x] 1.1 Modelo AuditLog: timestamp, user_id, user_name, activity_type,
           entity_id, entity_type, changes (JSON), ip_address
- [x] 1.2 audit_service.py: función log_action() llamada desde routers clave
- [x] 1.3 GET /v1/audit-logs: solo admin, filtros activity_type/user_id/date_range
- [x] 1.4 GET /v1/audit-logs/{id}: detalle con diff completo

## 2. Frontend
- [x] 2.1 AuditPage /audit: solo visible para admin en sidebar
- [x] 2.2 Tabla con filtros y paginación
- [x] 2.3 Modal de detalle con diff JSON formateado

## 3. Infra
- [x] 3.1 CronJob Helm: purga audit_logs > 180 días

## Cobertura de auditoría v1.2 — completa

### Nuevos ActivityType añadidos

```python
# Auth
LOGIN_FAIL       # intento de login fallido

# EOL
EOL_SYNC         # sync de un producto desde endoflife.date
EOL_SYNC_ALL     # sync de todos los productos
EOL_OVERRIDE     # sobrescritura de fecha EOL (custom_eol_date)
EOL_RETAG        # recálculo manual de etiquetas EOL

# Localización
LOCATION_ASSIGN  # asignar assets a celda (bulk-assign)

# Componentes de servicio
COMPONENT_ADD    COMPONENT_REMOVE
ENDPOINT_ADD     ENDPOINT_REMOVE

# Infraestructura
INFRA_BIND       INFRA_UNBIND

# Dependencias
DEPENDENCY_ADD   DEPENDENCY_REMOVE

# Excepciones
EXCEPTION_REVOKE  # más descriptivo que DELETE
```

### Cobertura por router

| Router | Operaciones auditadas |
|--------|----------------------|
| `assets.py` | CREATE, TAG_ASSIGN, TAG_REMOVE, INGEST |
| `eol.py` | CREATE, UPDATE, DELETE, EOL_SYNC, EOL_SYNC_ALL, EOL_OVERRIDE, EOL_RETAG |
| `certificates.py` | CREATE, UPDATE, DELETE |
| `locations.py` | CREATE, UPDATE, DELETE (zone/site/cell), LOCATION_ASSIGN |
| `applications.py` | CREATE, UPDATE, DELETE (app/service), COMPONENT_ADD/REMOVE, ENDPOINT_ADD/REMOVE, INFRA_BIND/UNBIND, DEPENDENCY_ADD/REMOVE |
| `tags.py` | CREATE, UPDATE, DELETE |
| `data_sources.py` | CREATE, UPDATE, DELETE |
| `exceptions.py` | CREATE, EXCEPTION_REVOKE |
| `middleware/auth.py` | LOGIN, LOGIN_FAIL |

### Frontend AuditPage
- Selector de tipo con labels en español (23 tipos)
- Selector de entidad (asset, tag, certificate, service, eol_product, etc.)
- Colores semánticos en tema claro para cada tipo
- `activity_type` serializado como string plano (sin prefijo enum)

### Propagación tras override EOL
Al guardar `custom_eol_date` en un ciclo:
1. Se registra `EOL_OVERRIDE` con `entity_type=eol_cycle`
2. Se recalculan etiquetas de assets del producto → registra `apply_eol_tags` internamente
3. El frontend invalida `['assets']` y `['dashboard']` inmediatamente

## Mejoras UX v1.3 — AuditPage legible

### Problemas corregidos
1. `<pre>` con fondo negro + texto oscuro → ilegible
2. `activity_type` en bruto en tabla (ej: "INFRA_BIND") sin label
3. Changes mostraban solo IDs sin nombres (asset_id sin asset_name)
4. Sin descripción en lenguaje natural de qué ocurrió

### Soluciones

#### Frontend — AuditPage.jsx reescrita
- **Tabla**: columna "Descripción" con `describeAction(log)` en lenguaje natural
- **Tipo de acción**: label español ("Vincular infra") en lugar de raw ("INFRA_BIND")  
- **Iconos por entidad**: 🧩 application, ⚙ service, 🖥 asset, 🏷 tag...
- **Modal detalle**:
  - Cabecera con grid limpio sobre fondo gris claro
  - Sección "¿Qué ocurrió?" en azul con descripción natural
  - `ChangesView` según tipo:
    - UPDATE → tabla before/after por campo con colores rojo/verde
    - CREATE/DELETE → grid de campos del objeto creado/eliminado
    - INFRA_BIND/COMPONENT_ADD/etc. → secciones before/after legibles

#### Backend — enriquecimiento de changes
- `INFRA_BIND`: incluye `asset_name` además de `asset_id`
- `COMPONENT_ADD`: incluye `application_name` además de `application_id`
- `DEPENDENCY_ADD`: incluye `target_app_name` además de `target_app_id`

#### audit_service._diff mejorado
```python
return {"changed": {field: {"before": v_b, "after": v_a}}, "before": ..., "after": ...}
```
- Clave `changed` para acceso directo a campos modificados
- Excluye campos ruidosos: `updated_at`, `last_sync`, `tags`, `exceptions`
- El frontend usa `ch.changed` para renderizar la tabla before/after de UPDATE

#### describeAction(log) — ejemplos
| Tipo | Descripción generada |
|------|---------------------|
| INFRA_BIND | `Se vinculó infraestructura "nginx-portal-prod-01" como capa "compute" a application "Portal Ciudadano Web"` |
| COMPONENT_ADD | `Se añadió aplicación "API Gateway Ciudadano" como componente "backend" del servicio "Portal Web Ciudadano"` |
| UPDATE | `Se modificó application "Portal Ciudadano Web" — campos: version, status` |
| EOL_OVERRIDE | `Sobrescritura de fecha EOL en ciclo "ubuntu/22.04" — 3 activos recalculados` |
| LOGIN_FAIL | `⚠ Intento de login fallido desde 192.168.1.1` |

## Cobertura completa v1.4 — 23/23 ActivityType

### describeAction() — cobertura total

Todos los 23 tipos cubiertos con descripción en lenguaje natural
usando los campos exactos que guarda cada router:

| ActivityType | Descripción generada (ejemplo) |
|-------------|-------------------------------|
| CREATE | `Se creó Aplicación "Portal Ciudadano Web"` |
| UPDATE | `Se modificó Servicio "Portal Web" — campos: status, description` |
| DELETE | `Se eliminó Producto EOL "ubuntu"` |
| TAG_ASSIGN | `Etiqueta(s) "Producción", "Crítico" asignada(s) al activo "vm-web-prod-01"` |
| TAG_REMOVE | `Etiqueta(s) "En migración" quitada(s) del activo "vm-urbanismo-01"` |
| LOGIN | `✅ devuser inició sesión desde 192.168.1.1` |
| LOGIN_FAIL | `⚠️ Intento de login fallido desde 10.0.0.5 — usuario: unknown` |
| LOGOUT | `devuser cerró sesión` |
| INGEST | `Ingesta desde "VMware" — activo "vm-api-prod-01" actualizado` |
| EOL_SYNC | `Sincronización EOL para producto "ubuntu" — 8 ciclos nuevos, 2 actualizados` |
| EOL_SYNC_ALL | `Sincronización EOL completa — 6 productos, 42 ciclos nuevos` |
| EOL_OVERRIDE | `Fecha EOL sobrescrita en ciclo "ubuntu/20.04" → 2026-04-02 — 1 activo recalculado` |
| EOL_RETAG | `Recálculo manual de etiquetas EOL — 12 activos actualizados` |
| LOCATION_ASSIGN | `3 activos asignados a la ubicación "Rack A"` |
| INFRA_BIND | `Infraestructura "nginx-portal-prod-01" vinculada a "Portal Ciudadano Web" como capa "compute" (puerto :80) ⚡ crítico` |
| INFRA_UNBIND | `Infraestructura "asset-vm-001" desvinculada de "Portal Ciudadano Web"` |
| COMPONENT_ADD | `Aplicación "API Gateway Ciudadano" añadida como componente "backend" al servicio "Portal Web Ciudadano"` |
| COMPONENT_REMOVE | `Componente (app "app-auth") eliminado del servicio "Portal Web"` |
| ENDPOINT_ADD | `Endpoint "https://www.ssreyes.org" (public) añadido al servicio "Portal Web Ciudadano"` |
| ENDPOINT_REMOVE | `Endpoint "https://staging.ssreyes.lan" eliminado del servicio "Portal Staging"` |
| DEPENDENCY_ADD | `Dependencia "uses": "Portal Ciudadano Web" → "Keycloak SSO"` |
| DEPENDENCY_REMOVE | `Dependencia con "app-auth" eliminada de "Portal Ciudadano Web"` |
| EXCEPTION_REVOKE | `Excepción de "edr" revocada para activo "vm-urbanismo-01"` |

### Mejoras en los changes del backend

- `TAG_ASSIGN`: `{tags_added: ["Producción","Crítico"], tag_count: 5}`
- `TAG_REMOVE`: `{before: {tags_removed: ["En migración"]}}`
- `INFRA_BIND`: incluye `asset_name`, `communication_port`, `is_critical`
- `COMPONENT_ADD`: incluye `application_name`
- `DEPENDENCY_ADD`: incluye `target_app_name`
- `UPDATE`: `{changed: {status: {before: "active", after: "maintenance"}}, before: {...}, after: {...}}`
- `audit_service._diff`: excluye `updated_at`, `last_sync`, `tags`, `exceptions` (ruido)

### Acción auditada faltante corregida
`EOL_SYNC` individual (sync de un único producto) no tenía `audit_service.record` — añadido.
`update_product` en EOL no tenía auditoría — añadida con before/after.
`bulk_untag` usaba `TAG_ASSIGN` en lugar de `TAG_REMOVE` — corregido.
