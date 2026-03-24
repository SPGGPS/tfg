# API Spec — Compliance Exceptions

## GET /v1/exceptions
Parámetros: status (active/revoked/expired/all), asset_id, indicator, page, page_size.
Devuelve lista de ComplianceException.to_dict().

## POST /v1/exceptions
Requiere admin. Crea excepciones en bulk.
```json
{
  "asset_ids": ["uuid1", "uuid2"],
  "indicator": "edr",
  "reason_code": "network_device",
  "description": "Switch de red, no admite agentes EDR (mínimo 20 chars)",
  "expires_at": "2026-12-31T23:59:59Z"
}
```
- expires_at es opcional; null = permanente
- Genera una ComplianceException por cada asset_id
- Campo reason = REASON_LABELS[reason_code] + ": " + description

## DELETE /v1/exceptions/{id}
Requiere admin. Soft delete: rellena revoked_by, revoked_by_name, revoked_at.
No borra el registro.

## GET /v1/exceptions/reason-codes/list
⚠️ DECLARAR ANTES DE /{id} EN EL ROUTER (FastAPI evalúa en orden)
Devuelve:
```json
[{"code": "network_device", "label": "Dispositivo de red..."}]
```

## Reason codes disponibles
agent_not_supported, network_device, excluded_backup, excluded_monitoring,
excluded_siem, legacy_system, pending_deployment, decommissioning,
cloud_backup_only, local_backup_only, temporary_exclusion, other
