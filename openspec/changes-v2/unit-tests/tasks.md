# Tasks: Tests de integración

## Estado: implementado (tests escritos, pendiente de ejecutar en entorno con BD)

## Archivo
`backend/tests/test_api.py` — 383 líneas, 36 tests

## Ejecutar
```bash
pip install pytest httpx --break-system-packages
docker compose down -v && docker compose build --no-cache && docker compose up -d
sleep 15
pytest backend/tests/test_api.py -v --tb=short
```

## Clases de test implementadas
- [x] TestHealth (1): Backend levantado
- [x] TestAssets (8): Listado, paginación, filtros, enum serializado, bulk-tags, bulk-untag
- [x] TestTags (4): Listado, color_code con #, enum origin, protección tags sistema
- [x] TestExceptions (3): Listado, reason-codes, enum indicator
- [x] TestLocations (4): Árbol, zonas, IntegrityError→409, bulk-assign endpoint
- [x] TestCertificates (3): Listado, expiry-summary orden de rutas, enum status
- [x] TestEol (6): Listado, ciclos seed, eol_status, proxy endoflife.date, custom update
- [x] TestApplications (4): Apps/services, enum, dependency-graph
- [x] TestAudit (1): Listado logs
- [x] TestDataSources (2): Listado, enum type

## Tests de regresión críticos (bugs encontrados en desarrollo)

| Test | Bug que detecta |
|------|----------------|
| test_asset_enum_serialized_as_string | Enum serializado como "AssetType.server_physical" |
| test_zone_integrity_error_returns_409 | IntegrityError → 500 (no capturado) |
| test_expiry_summary | Ruta /expiry-summary shadowed por /{cert_id} |
| test_reason_codes_list | Ruta /reason-codes/list shadowed por /{id} |
| test_bulk_untag_endpoint_exists | POST /bulk-untag no registrado |
| test_eol_cycle_update_custom_date | custom_eol_date no persiste |

## Bugs de compilación corregidos en frontend

| Bug | Causa | Archivo |
|-----|-------|---------|
| `complianceCls` declarado dos veces | Duplicado en TagBadge tras refactorización | index.jsx |
| `cmp` declarado dos veces | Dos const cmp en el mismo scope en función sort | ExceptionsPage.jsx |
| `e` declarado dos veces | Dos const e en la misma función getTooltip | ComplianceBadge.jsx |
| Columna "Override EOL" faltante | 8 <td> pero 7 <th> en tabla de ciclos | EolPage.jsx |

## Pendiente
- [ ] E2E con Playwright: flujo completo asignar/eliminar etiqueta [v2.0 — requiere entorno CI]
- [ ] E2E: flujo excepciones (crear → verificar badge → revocar) [v2.0]
- [ ] E2E: flujo EOL (añadir producto → sync → ver ciclos → override) [v2.0]

## EOL matching tests (añadir a test_api.py)
- [x] Test: asset con os="Ubuntu 22.04" → tag EOL OK si ciclo existe (TestEolMatching.test_ubuntu_22_maps_to_ok)
- [x] Test: asset con os="Ubuntu 18.04" → tag EOL KO si ciclo marcado eol (TestEolMatching.test_eol_products_different_counts)
- [x] Test: POST /v1/eol/recalculate-tags → 200 + {updated: N} (TestEolMatching.test_recalculate_eol_tags)
- [x] Test: getBadgeClass retorna clases light-mode (no bg-*-900) — verificado en compilación Vite

## Tests añadidos en test_api.py (498 líneas, ~50 tests)

### TestEolMatching (7 tests)
- test_eol_products_list — lista productos con ≥1 en seed
- test_eol_product_has_asset_counts — verifica campos asset_eol_ko/warn/ok presentes
- test_ubuntu_22_maps_to_ok — web-prod-01 (Ubuntu 22.04) → EOL OK en producto ubuntu
- test_recalculate_eol_tags — POST /recalculate-tags devuelve {updated: N}
- test_eol_products_different_counts — conteos distintos por producto (no global)
- test_reseed_endpoint — POST /v1/admin/reseed → {ok: true}
- test_assets_visible_after_reseed — ≥10 assets tras reseed

### TestComplianceBadges (5 tests)
- test_asset_compliance_fields_present — edr_installed, monitored, last_backup_local
- test_asset_type_is_plain_string — tipo sin "." (enum bien serializado)
- test_dashboard_kpis — total_assets≥1, active_exceptions, total_certificates presentes
- test_dashboard_eol_segments_not_empty — segmentos con count>0 si existen
- test_cell_full_path_in_assets — todos los assets del seed tienen cell_full_path

## Tests finales v1.1 — 58 test methods en test_api.py

### Nuevas clases:
- TestEolProductAssets (5 tests) — matching real por producto+versión
- TestDashboardLive (4 tests) — KPIs coherentes con inventario real

### Total cobertura:
Assets CRUD, Tags, Compliance, EOL matching, EOL product assets,
Excepciones, Certificados, Aplicaciones/Servicios, Grafo, Auditoría,
Fuentes de datos, Dashboard KPIs, Dashboard vs inventario
