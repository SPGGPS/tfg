# Design: Inventory Master

## Context
CMDB centralizado con activos (servidores, red, bases de datos), ingesta desde fuentes externas,
etiquetado dual (sistema + manual), y compliance (EDR, backup, monitorización, logs, SIEM).
Stack: FastAPI, React, PostgreSQL 16.

## Goals / Non-Goals

**Goals:**
- Esquema Asset polimórfico con tipos: server_physical, server_virtual, switch, router, ap, database
- Sistema de compliance con 6 indicadores: edr, mon, siem, logs, bck, bckcl
- Etiquetas dual: sistema (auto) y manuales (admin)
- Historificación por hora, búsqueda/ordenación/filtros
- Tipo "database" como activo de primera clase

**Non-Goals:**
- CRUD manual de activos (vienen de ingesta externa)
- Edición de etiquetas de sistema

## Decisiones de diseño

| Decisión | Rationale |
|----------|-----------|
| Discriminador `type` en Asset | server_physical/virtual/switch/router/ap/database — extensible sin herencia múltiple |
| Upsert por UUID/MAC | Evitar duplicados en ingestas horarias desde múltiples fuentes |
| Tabla asset_tag N:M | Un activo → muchas tags. CASCADE al borrar tag manual |
| database como AssetType propio | Campos específicos (engine, port, schemas) no encajan en servers ni en red |
| last_backup_local + last_backup_cloud | Dos columnas separadas en lugar de una genérica; permite compliance independiente |
| NULLS FIRST en sort ASC para backups | Sin backup aparece primero (peor estado visible arriba) |
| NULLS LAST en sort DESC para backups | Más recientes primero, sin backup al final |

## Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| Ingesta lenta con muchos activos | Upsert en batch; índice en mac_address |
| Historificación pesada | Retención 1 año; CronJob de purga en Helm |
