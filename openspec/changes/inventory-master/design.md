# Design: Inventory Master

## Context

CMDB centralizado con activos (servidores, red), ingesta desde VMware/Veeam/Monica/EDR, etiquetado dual (sistema + manual), y compliance (EDR, backup, monitorización, logs). Sync horaria. Stack: FastAPI, React, PostgreSQL.

## Goals / Non-Goals

**Goals:** Esquema Asset polimórfico, POST /v1/assets/bulk-tags, auto-tagging, dashboard con badges, historificación por hora, búsqueda/ordenación.

**Non-Goals:** CRUD manual de activos (vienen de ingesta), edición de tags de sistema.

## Decisions

| Decisión | Rationale |
|----------|-----------|
| Discriminador `type` | server_physical, server_virtual, switch, router, ap permiten extensión sin herencia múltiple |
| Upsert por UUID/MAC | Evitar duplicados en ingestas; identificadores únicos de fuentes externas |
| Tabla Asset-Tag N:M | Un activo muchas tags, una tag muchos activos; CASCADE al borrar tag manual |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Ingesta lenta | Procesamiento asíncrono; CronJob 0 * * * * |
| Historificación pesada | Particionado por mes; retención 1 año |
