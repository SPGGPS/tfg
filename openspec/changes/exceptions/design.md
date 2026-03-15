# Design: Compliance Exceptions

## Context

Los indicadores de compliance (EDR/MON/SIEM/LOGS/BCK/BCKCL) se establecen automáticamente
desde los orígenes de datos externos. Algunos activos no pueden cumplir ciertos indicadores
por razones técnicas o de negocio legítimas. Sin excepciones, el dashboard muestra falsos
positivos permanentes que reducen la confianza en el sistema.

Stack: FastAPI, React, PostgreSQL, Keycloak (admin only).

## Goals / Non-Goals

**Goals:**
- Tabla `compliance_exceptions` inmutable en creación, con soft-delete para revocaciones
- API REST bajo `/v1/exceptions` restringida a admin para creación/revocación
- Badge triestado: verde (OK), azul (excepción activa), rojo (incumplimiento sin justificar)
- Motivo obligatorio con longitud mínima (≥20 chars)
- Registro de quién creó y quién revocó cada excepción
- Expiración opcional: la excepción deja de ser activa automáticamente tras la fecha

**Non-Goals:**
- Excepciones aprobadas por flujo de workflow (aprobador ≠ creador). Fuera de alcance v1.
- Excepciones globales por tipo de activo (ej. "todos los switches sin EDR"). En v1
  las excepciones son siempre por activo individual. Se puede añadir en v2.
- Modificar el motivo de una excepción existente (inmutabilidad total; revocar y recrear).

## Decisions

| Decisión | Rationale |
|----------|-----------|
| Soft delete en lugar de borrado físico | Preservar historial completo de quién justificó qué y cuándo. Alineado con filosofía de audit_logs. |
| Excepción por (asset_id, indicator) único activo | Evitar duplicados confusos. Si ya existe una activa, se devuelve 409 con el id existente. |
| Mínimo 20 chars en motivo | Forzar justificaciones reales, no "ok", "n/a" o "test". |
| Expiración opcional | Permite excepciones temporales (ej. "en proceso de instalación EDR, expira en 30 días") y permanentes (ej. "switch, nunca tendrá EDR"). |
| Color azul para excepción activa | Diferencia clara del semáforo verde/rojo. Azul es un estado neutro-informativo: "sabemos que está mal, está justificado". |
| Excepciones incluidas en GET /v1/assets | El frontend no necesita hacer una llamada extra por activo. El backend enriquece la respuesta con las excepciones activas. |
| Registro en audit_logs | Coherencia con el resto del sistema. Creación = ActivityType.CREATE, revocación = ActivityType.DELETE, entity_type = "exception". |

## Data Model

```
compliance_exceptions
─────────────────────
id              UUID PK
asset_id        FK → assets.id (ON DELETE CASCADE)
indicator       ENUM (edr, mon, siem, logs, bck, bckcl)
reason          TEXT NOT NULL (min 20 chars)
created_by      STRING NOT NULL  -- user_id del JWT
created_by_name STRING NOT NULL  -- preferred_username del JWT
created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
expires_at      TIMESTAMPTZ NULL  -- null = sin expiración
revoked_by      STRING NULL
revoked_by_name STRING NULL
revoked_at      TIMESTAMPTZ NULL

UNIQUE INDEX: (asset_id, indicator) WHERE revoked_at IS NULL
              -- solo puede haber una excepción activa por (asset, indicator)
INDEX: (asset_id)
INDEX: (indicator)
INDEX: (revoked_at)  -- para filtrar activas eficientemente
```

## Estado de una excepción

```
activa    → revoked_at IS NULL AND (expires_at IS NULL OR expires_at > now())
revocada  → revoked_at IS NOT NULL
expirada  → revoked_at IS NULL AND expires_at <= now()
```

## Color logic en frontend

```
para cada indicator de un asset:
  si el indicador es OK (bool=true o datetime != null):
    → VERDE
  si el indicador es KO (bool=false o datetime == null):
    si existe excepción activa para (asset.id, indicator):
      → AZUL
    sino:
      → ROJO
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Abuso: crear excepciones para ocultar problemas reales | Motivo obligatorio con mínimo 20 chars + registro inmutable de quién las crea + visible en historial |
| Excepciones expiradas no se limpian | La lógica de color las trata como inactivas automáticamente por fecha; no necesitan borrado físico |
| Performance: enriquecer cada asset con sus excepciones | Usar un JOIN o subquery eficiente; las excepciones son pocas relativas a los assets |
