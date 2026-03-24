# Tasks: End of Life

## 1. Modelos y DB
- [x] 1.1 EolSyncStatus enum: synced / unsynced
- [x] 1.2 EolProduct: product_id(unique), display_name, category, notes,
           sync_status, last_synced_at, created_at, updated_at
- [x] 1.3 EolCycle: product_id(index), cycle, release_date, eol_date, eol_boolean,
           support_end, lts, latest, link, custom_eol_date, custom_notes,
           sync_status, last_synced_at, raw_data(JSON)
           Index compuesto: (product_id, cycle)
- [x] 1.4 EolCycle.effective_eol_date = custom_eol_date ?? eol_date
- [x] 1.5 EolCycle.eol_status: eol / warning / ok / unknown (calculado)
- [x] 1.6 Importar modelos en app/models/__init__.py

## 2. Backend
- [x] 2.1 GET /v1/eol/all-products — proxy a endoflife.date/api/all.json (sin BD)
- [x] 2.2 GET /v1/eol/products — lista productos en BD con cycle_count, eol_count, warning_count
- [x] 2.3 POST /v1/eol/products/{product_id} — añadir producto + primera sync automática
- [x] 2.4 PUT /v1/eol/products/{product_id} — editar display_name, category, notes
- [x] 2.5 DELETE /v1/eol/products/{product_id} — eliminar producto y sus ciclos
- [x] 2.6 POST /v1/eol/products/{product_id}/sync — sync manual de un producto
- [x] 2.7 POST /v1/eol/sync-all — sync todos los productos (usado por CronJob)
- [x] 2.8 GET /v1/eol/products/{product_id}/cycles — ciclos de un producto
- [x] 2.9 PUT /v1/eol/products/{product_id}/cycles/{cycle_id} — editar custom_eol_date y custom_notes
- [x] 2.10 GET /v1/eol/asset-status — crossing assets × ciclos EOL
- [x] 2.11 _sync_product(): upsert ciclos, marcar unsynced los que desaparecen, NO borrar
- [x] 2.12 Fix: imports Optional y re al inicio del archivo (no al final)

## 3. Servicios
- [x] 3.1 apply_eol_tags(db, asset) en tagging_service.py
           Busca OS y db_engine del asset en EolCycle
           Asigna etiqueta de sistema según eol_status peor encontrado
- [x] 3.2 Etiquetas EOL: "EOL"(rojo #dc2626), "EOL Próximo"(amarillo #d97706), "EOL OK"(verde #16a34a)

## 4. Frontend (EolPage.jsx)
- [x] 4.1 EolStatusBadge: eol/warning/ok/unknown con colores consistentes
- [x] 4.2 SyncBadge: synced verde con fecha | unsynced rojo
- [x] 4.3 EolDaysCell: días restantes con colores semánticos
- [x] 4.4 ProductDetail: tabla de ciclos con edición inline custom_eol_date
- [x] 4.5 AddProductModal: búsqueda en catálogo endoflife.date (radio list) + metadatos
- [x] 4.6 EolPage principal: tabla de productos, resumen, filtros, botones sync
- [x] 4.7 Fila unsynced: fondo bg-red-50/60 + badge rojo
- [x] 4.8 Botón "🔄 Sync todo" y botón "🔄" por fila (solo admin)
- [x] 4.9 Sidebar: entrada "End of Life" con ShieldIcon, visible a todos los roles
- [x] 4.10 Ruta /eol en main.jsx

## 5. Infra
- [x] 5.1 CronJob Helm: eol-sync-daily — schedule "0 3 * * *"
           Descarga y ejecuta sync-all contra el backend interno
- [x] 5.2 Seed en init_db.py: ubuntu(4 ciclos), rhel(3), postgresql(3), python(3)

## 6. API externa
URL base: https://endoflife.date/api
- GET /all.json → lista de todos los slugs de productos
- GET /{product}.json → array de ciclos del producto
Campos por ciclo: cycle, eol (fecha|bool), support/supportedUntil, releaseDate, lts, latest, link

## 6. Integración etiquetas EOL con inventario — implementado

### Etiquetas del sistema (SYSTEM_TAGS)
```python
"EOL KO":   "#dc2626"  # rojo   — sin soporte (eol_status="eol")
"EOL WARN": "#d97706"  # ámbar  — ≤1 año para EOL (eol_status="warning")
"EOL OK":   "#16a34a"  # verde  — >2 años en soporte (eol_status="ok")
```

### Flujo de asignación automática
1. Sync de producto EOL → `_sync_product()` → llama `apply_eol_tags()` en TODOS los assets
2. Seed (`init_db.py`) → llama `apply_eol_tags()` tras cargar ciclos EOL
3. Botón manual "🏷 Recalcular etiquetas" en EolPage → POST /v1/eol/recalculate-tags

### Lógica de matching en apply_eol_tags()
- asset.os → busca slug (ubuntu/debian/rhel/centos/windows-server)
- asset.db_engine → busca slug (postgresql/mssqlserver/mysql/mariadb)
- Versión extraída con regex `\b{cycle}\b` del campo os o db_version
- Si hay ciclo exacto → calcula eol_status → asigna etiqueta del sistema
- Peor estado gana (eol > warning > ok)
- Limpia etiquetas EOL viejas antes de reasignar (incluyendo nombres legacy)

### POST /v1/eol/recalculate-tags
Requiere admin. Recalcula etiquetas EOL en todos los assets. Devuelve:
`{"updated": N, "message": "Etiquetas EOL recalculadas en N activos"}`

### Nombres históricos (legacy) que se limpian automáticamente
"EOL", "EOL Próximo" → sustituidos por "EOL KO", "EOL WARN", "EOL OK"

## 7. Estado actual completamente implementado
- [x] Nombres: EOL KO (rojo), EOL WARN (ámbar), EOL OK (verde)
- [x] Matching por: asset.os, asset.db_engine+db_version, vendor+firmware_version
- [x] Fallback versión X.Y → X (major)
- [x] apply_eol_tags() llamada desde: _sync_product(), init_db, POST /recalculate-tags
- [x] POST /v1/eol/recalculate-tags — recalcula todas las etiquetas EOL
- [x] Botón "🏷 Recalcular etiquetas" en EolPage
- [x] Productos a cargar para cubrir seed: ubuntu, rhel, postgresql, mssqlserver, windows-server

## 8. EOL — etiqueta OK con matching por versión exacta

### Problema detectado
El listado de productos (`GET /v1/eol/products`) mostraba los mismos badges
para todos los productos porque buscaba assets con tag "EOL KO/WARN/OK" globalmente.

### Solución implementada
Matching real por producto + versión: se replica la lógica de `apply_eol_tags`:
1. Cargar ciclos del producto: `{cycle_name → eol_status}`
2. Para cada asset: extraer versión con mismo regex del tagging_service
3. Match exacto en product_cycles → fallback major version
4. Resultado: solo assets cuya versión específica coincide con un ciclo de ESTE producto

Ejemplo: ubuntu 22.04 → ciclo "22.04" del producto "ubuntu" → eol_date=2027 → "ok"
→ aparece en columna EOL OK de Ubuntu pero NO en PostgreSQL

### Init DB — asegurar EOL OK
Para que ubuntu 22.04 (eol 2027) aparezca en EOL OK:
1. El seed crea ubuntu + ciclos incluyendo "22.04" (eol_date=2027-04-21)
2. apply_eol_tags se llama tras crear assets Y ciclos (ambos con db.flush() antes)
3. web-prod-01 (os="Ubuntu 22.04 LTS") → tag "EOL OK" asignada

Para verificar: POST /v1/eol/recalculate-tags tras el seed.

## 9. Refactoring: funciones helper reutilizables

### _asset_matches_product(asset, product_id) → bool
Verifica si el OS/DB/firmware del asset corresponde al product_id.
Reutilizada en list_products y product_eol_assets.

### _eol_status_for_asset_and_product(asset, product_cycles) → str|None
Extrae versión del asset con regex, busca en product_cycles con fallback major.
Retorna eol_status ('eol'|'warning'|'ok') o None si no hay match.

### GET /v1/eol/products/{id}/assets — reescrito
Ahora usa las funciones helper para matching real producto+versión.
Filtra: (1) asset corresponde al producto, (2) tiene el eol_status solicitado.
Incluye campo `eol_status` en cada asset de la respuesta.

### Tests añadidos
- TestEolProductAssets.test_ubuntu_ok_assets — web-prod-01 en ubuntu OK
- TestEolProductAssets.test_ubuntu_assets_not_shared_with_postgresql — no overlap
- TestEolProductAssets.test_postgresql_assets_correct — postgres-prod-01 en postgresql
- TestEolProductAssets.test_mssqlserver_assets_correct — sqlserver-erp-01 en mssqlserver
- TestEolProductAssets.test_eol_assets_have_eol_status_field — campo eol_status presente

## 10. Fix: badge EOL OK no clickable

### Problema
En la lista de productos (`EolPage`), el badge "✓ N OK" era un `<span>` sin `onClick`.
Los badges EOL KO y EOL WARN sí eran `<button>`, pero OK no.
Resultado: pulsar OK no abría el modal de assets.

### Solución
```jsx
// ❌ ANTES — no clickable:
<span className="badge bg-green-100 ...">✓ {p.asset_eol_ok} OK</span>

// ✅ DESPUÉS — clickable:
<button onClick={() => setAssetsModal({productId:p.product_id, productName:p.display_name, status:'ok'})}
  className="badge bg-green-100 ... cursor-pointer hover:bg-green-200 transition-colors">
  ✓ {p.asset_eol_ok} OK →
</button>
```

### Flujo completo verificado
1. Usuario pulsa badge "✓ N OK" en la fila del producto
2. `setAssetsModal({productId, productName, status:'ok'})` se dispara
3. Modal `<AssetsEolModal>` se abre con `status="ok"`
4. `eolApi.productAssets(productId, "ok")` → `GET /v1/eol/products/{id}/assets?status=ok`
5. Backend: `_asset_matches_product(asset, product_id)` + `_eol_status_for_asset_and_product(asset, cycles) == "ok"`
6. Devuelve assets cuya versión de OS/DB tiene ciclo con eol_status="ok"

### Validación con datos del seed
| Asset | Producto | Ciclo | Status |
|-------|---------|-------|--------|
| web-prod-01 (Ubuntu 22.04 LTS) | ubuntu | 22.04 (eol: 2027) | ok |
| db-prod-01 (RHEL 9) | rhel | 9 (eol: 2032) | ok |
| app-vm-staging-01 (Windows Server 2022) | windows-server | 2022 (eol: 2026) | ok |
| postgres-prod-01 (postgresql 16.2) | postgresql | 16 (eol: 2028) | ok |
| sqlserver-erp-01 (sqlserver 2022) | mssqlserver | 2022 (eol: 2033) | ok |

### Requisito para que funcione
La BD debe tener los ciclos EOL cargados. Si el inventario arranca limpio:
1. `docker compose down -v && docker compose build --no-cache && docker compose up -d`
2. En EolPage: "🔄 Sync todo" (descarga ciclos de endoflife.date)
3. "🏷 Recalcular etiquetas EOL" (asigna EOL KO/WARN/OK a assets)

## 11. Override de ciclo → recálculo automático

### PUT /v1/eol/products/{product_id}/cycles/{cycle_id}

Cuando se sobrescribe `custom_eol_date` de un ciclo, el endpoint:
1. Persiste el cambio con `db.flush()`
2. Llama `apply_eol_tags(db, asset)` en todos los assets que corresponden
   al producto (`_asset_matches_product(asset, product_id)`)
3. Hace `db.commit()`
4. Devuelve `{...ciclo, "retag_updated": N}` — número de assets recalculados

### Frontend — updateCycleMut.onSuccess
```js
qc.refetchQueries({ queryKey: ['eol-cycles', productId] })  // ciclos del modal
qc.refetchQueries({ queryKey: ['eol-products'] })            // contadores lista
qc.invalidateQueries({ queryKey: ['assets'], exact: false }) // etiquetas inventario
qc.invalidateQueries({ queryKey: ['dashboard'] })            // sectores dashboard
toast(`Versión actualizada · N activos recalculados`)
```

### Ejemplo
- Ciclo ubuntu/20.04 tiene `eol_date=2025-04-02` → eol_status="warning"
- Admin sobrescribe con `custom_eol_date=2026-04-02`
- `apply_eol_tags` recalcula → web-prod-01 pasa de "EOL WARN" a "EOL OK"
- Dashboard actualiza sectores EOL inmediatamente
- Inventario muestra nuevo badge EOL OK en web-prod-01

## EOL automático v1.5

### Diseño de la automatización

#### Cuándo se sincroniza
1. **Al dar de alta un asset**: `POST /v1/ingest` → `auto_sync_new_asset()` en background
   - Detecta OS/DB del asset y compara con productos EOL registrados
   - Si el producto no existe aún, lo añade desde endoflife.date y recalcula etiquetas
2. **Diariamente a las 05:00** (Europe/Madrid): `daily_eol_sync()`
   - Detecta productos en todos los assets no registrados → los añade
   - Resync de productos ya registrados (actualiza ciclos)
   - Recalcula etiquetas EOL en todos los assets

#### Scheduler (APScheduler 3.x)
```python
# main.py lifespan
scheduler.add_job(
    daily_eol_sync,
    CronTrigger(hour=5, minute=0, timezone="Europe/Madrid"),
    id="daily_eol_sync", misfire_grace_time=3600
)
scheduler.start()
# Al cerrar: scheduler.shutdown(wait=False)
```

### Nuevos endpoints

#### GET /v1/eol/detected-products
Devuelve productos detectados en assets separados en:
- `registered`: ya en BD, con asset_count
- `pending`: en assets pero no registrados, con asset_count

#### POST /v1/eol/auto-sync
Añade y sincroniza todos los productos de `pending`.
Recalcula etiquetas si se añadieron productos nuevos.

#### POST /v1/eol/products/{id}/custom-cycle
```json
{ "cycle": "2.3.1", "eol_date": "2026-12-31", "notes": "Versión en producción" }
```
- Crea el ciclo con fecha EOL custom
- Si el ciclo ya existe, actualiza custom_eol_date
- Recalcula etiquetas EOL en activos afectados automáticamente
- Registra en auditoría como EOL_OVERRIDE

### Frontend — EolPage cambios

#### Banner de detección automática
Si `detected.pending.length > 0`, aparece un banner ámbar con:
- Productos detectados y número de activos afectados
- Botón "Sincronizar ahora" → POST /auto-sync
- Botón "Añadir custom (sin API)"

#### Botones de acción
| Botón | Acción |
|-------|--------|
| 🔄 Sync todo | Actualiza ciclos de todos los productos desde API |
| 🔍 Auto-sync inventario (N) | Detecta y registra productos del inventario no cubiertos |
| 🏷 Recalcular | Recalcula etiquetas EOL en todos los assets |
| + Añadir de API | Modal original — buscar en catálogo endoflife.date |
| ✎ Añadir custom | Modal nuevo — fecha EOL manual sin API |

#### Modal "Añadir custom" — tres modos
1. **Detectados** — productos en assets sin cobertura EOL (con conteo de assets)
2. **Ya registrados** — añadir ciclo custom a un producto existente
3. **Nuevo producto** — crear producto completamente nuevo (software interno)

Preview del estado resultante: muestra si el ciclo quedará EOL KO / WARN / OK
según la fecha introducida.

#### Info del scheduler
Nota permanente en la UI: "⏰ Sincronización automática diaria a las 05:00"

### Flujo completo
```
Nuevo asset ingresado (OS: Ubuntu 20.04)
  → auto_sync_new_asset(asset_os="Ubuntu 20.04")
    → detecta slug "ubuntu"
    → "ubuntu" no registrado → _sync_product(db, "ubuntu")
    → ciclos: 20.04 eol=2025-04-02 (EOL KO), 22.04 ok, 24.04 ok...
    → apply_eol_tags(db, asset) → tag "EOL KO" asignada
  → dashboard KPI actualizado
```
