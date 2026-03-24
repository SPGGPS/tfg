# Tasks: Dashboard

## 1. Backend
- [x] 1.1 GET /v1/dashboard — endpoint que agrega todos los datos necesarios
- [x] 1.2 EOL summary: assets por tipo × estado EOL
- [x] 1.3 Compliance summary: assets por indicador × estado
- [x] 1.4 Backup summary: local y cloud × estado
- [x] 1.5 Certificates summary: por estado (valid/expiring/critical/expired)

## 2. Frontend
- [x] 2.1 DashboardPage /dashboard — página principal
- [x] 2.2 Componente PieChart (SVG) reutilizable con hover/tooltip/click
- [x] 2.3 Bloque 1: EOL por tipo de asset
- [x] 2.4 Bloque 2: Compliance por indicador (6 gráficos)
- [x] 2.5 Bloque 3: Backup Local + Backup Cloud
- [x] 2.6 Bloque 4: Certificados por estado
- [x] 2.7 KPIs: total activos, certificados, excepciones activas
- [x] 2.8 Navegación: sidebar item "Dashboard" como primera entrada
- [x] 2.9 Ruta / redirige a /dashboard (inventario pasa a /inventario)

## 3. Infra
- [x] 3.1 Ruta /dashboard como default (index)

## Fixes v1.0

### EOL: solo mostrar segmentos con elementos
El backend ahora solo incluye segmentos y grupos EOL cuando `count > 0`.
Lo mismo aplica a compliance, backup y certificados.

### Dashboard se actualiza al crear/revocar excepciones
ExceptionsPage ahora invalida `['dashboard']` además de `['exceptions']` y `['assets']`
en todas las mutaciones (crear, revocar, etc.).

### Filtro compliance con excepciones
- ok_with_exception → navega a /inventario?search=EDR+Active (tiene activo + excepción)
- ko_with_exception → navega a /inventario?search=EDR+Missing (KO pero con excepción)
El backend busca por Tag.name.ilike(), por lo que ambos estados quedan filtrados
correctamente ya que ambos tienen el tag correspondiente.

## v1.1 — Fixes y consistencia

### KPIs — total_services real
Antes: hardcoded a 0. Ahora: `len(db.query(Service).all())` en cada request.

### Tests dashboard live
- test_kpi_total_assets_matches_inventory — kpi == inventario real
- test_kpi_total_services — ≥1 servicios
- test_compliance_segments_only_nonzero — sin segmentos vacíos
- test_eol_segments_only_nonzero — sin segmentos EOL vacíos

### Colores excepciones — azul (no morado)
- ok_with_exception: gradiente azul→rojo (OK pero vigilar)
- ko_with_exception: gradiente azul→verde (KO justificado, controlado)
