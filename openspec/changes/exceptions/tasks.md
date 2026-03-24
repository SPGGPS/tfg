# Tasks: Compliance Exceptions

## 1. Modelo y DB
- [x] 1.1 Modelo ComplianceException: asset_id FK, indicator, reason_code, reason,
           created_by, created_by_name, created_at, expires_at,
           revoked_by, revoked_by_name, revoked_at
- [x] 1.2 Propiedades: is_active, status ("active"/"revoked"/"expired")
- [x] 1.3 Enum ComplianceIndicator: edr, mon, siem, logs, bck, bckcl
- [x] 1.4 Enum ExceptionReasonCode con 12 valores + REASON_LABELS dict
- [x] 1.5 Serialización: reason_code como str.split(".")[-1]

## 2. Backend
- [x] 2.1 GET /v1/exceptions con filtros: status, asset_id, indicator, page, page_size
- [x] 2.2 POST /v1/exceptions — acepta asset_ids (array), crea una excepción por asset
- [x] 2.3 DELETE /v1/exceptions/{id} — soft delete (rellena revoked_*)
- [x] 2.4 GET /v1/exceptions/reason-codes/list — DECLARADO ANTES DE /{id}
- [x] 2.5 Concatenar REASON_LABELS[reason_code] + ": " + description en campo reason

## 3. Frontend
- [x] 3.1 ExceptionsPage /exceptions — solo admin
- [x] 3.2 Tabla de excepciones activas con columnas: Activo, Indicador, Código, Motivo, Creada por, Expira, Acciones
- [x] 3.3 Ordenación client-side por columna con SortTh component
- [x] 3.4 Checkboxes + "Revocar seleccionadas (N)" con confirmación
- [x] 3.5 Formulario nueva excepción: indicator, reason_code, description (min 20 chars), expires_at
- [x] 3.6 MultiAssetSelector: lista flat con checkboxes, checkbox "Seleccionar todos",
           muestra nombre + tipo + IP, búsqueda por nombre, assets bloqueados (ya tienen excepción)
- [x] 3.7 Invalidación caché tras crear/revocar: queryClient.invalidateQueries({queryKey:["assets"],exact:false})
- [x] 3.8 Badges compliance: getComplianceState() + getBadgeClass() en ComplianceBadge.jsx

## 4. Seed de excepciones (init_db.py)

- [x] 4.1 core-switch-01   → EDR, reason: network_device, permanente
- [x] 4.2 access-switch-02 → EDR, reason: network_device, permanente
- [x] 4.3 router-edge-01   → EDR, reason: network_device, permanente
- [x] 4.4 ap-office-floor2 → EDR, reason: network_device, permanente
- [x] 4.5 app-vm-staging-01 → SIEM, reason: pending_deployment, expira 30/06/2026
