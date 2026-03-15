# Design: Tags Management

## Context

Etiquetas automáticas (sistema) vs manuales (admin). CRUD de manuales. Propagación de cambios a activos. Protección de tags de sistema.

## Goals / Non-Goals

**Goals:** PUT/DELETE /v1/tags/{id} (admin), protección origin=system, propagación color/nombre, modal confirmación borrado.

**Non-Goals:** Crear tags de sistema desde UI, renombrar masivamente.

## Decisions

| Decisión | Rationale |
|----------|-----------|
| ON DELETE CASCADE en asset_tag | Desvinculación atómica al borrar tag |
| Invalidar caché frontend | TanStack Query invalidation tras update tag |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Borrado accidental | Modal con nº activos afectados |
| Inconsistencia UI | Invalidar queries tras PUT/DELETE |
