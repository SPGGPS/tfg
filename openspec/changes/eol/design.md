# Design: End of Life (EOL)

## Flujo de datos

```
endoflife.date/api/{product}.json
        ↓  (sync manual o CronJob diario)
EolProduct + EolCycle (BD)
        ↓  (apply_eol_tags en tagging_service)
Etiqueta EOL en Asset (tag de sistema)
```

## Modelos

### EolProduct
Representa un producto del catálogo (ej: "ubuntu", "postgresql").
- `product_id` — slug de la API (único, no borrar)
- `display_name` — nombre legible, editable por admin
- `category` — OS, Database, Language, Framework...
- `sync_status` — synced / unsynced (no borrar nunca)
- `last_synced_at` — timestamp de la última sync exitosa

### EolCycle
Ciclo de vida de una versión concreta (ej: Ubuntu 22.04).
- `cycle` — string de versión (ej: "22.04", "3.11", "8")
- `eol_date` — fecha EOL de la API (puede ser null)
- `eol_boolean` — true cuando la API indica "ya sin soporte" sin fecha
- `custom_eol_date` — override admin (prioridad sobre eol_date)
- `effective_eol_date` = custom_eol_date ?? eol_date
- `eol_status` — calculado: eol / warning / ok / unknown

## Estados EOL

| Estado | Color | Condición |
|--------|-------|-----------|
| eol | rojo | eol_boolean=true OR effective_eol_date ≤ hoy |
| warning | amarillo | 0 < días_restantes ≤ 365 |
| ok | verde | días_restantes > 730 (>2 años) |
| unknown | gris | sin fecha |

Nota: días_restantes entre 365 y 730 también es "warning" (≤2 años).

## Política de no borrado
Cuando un ciclo desaparece de endoflife.date en una sync:
- NO se borra del BD
- Se marca `sync_status = unsynced`
- Se muestra con fondo rojo claro + badge "🔴 unsynced"
- Los valores custom se conservan

## Etiquetas automáticas en activos
`apply_eol_tags(db, asset)` en `tagging_service.py`:
1. Busca el OS del asset en los productos EOL (ubuntu, rhel, debian, windows-server...)
2. Busca el db_engine en los productos EOL (postgresql, mssqlserver, mysql...)
3. Extrae la versión con regex (X.Y o X)
4. Consulta el EolCycle correspondiente
5. Asigna la etiqueta de sistema con el peor estado encontrado:
   - "EOL" (#dc2626 rojo)
   - "EOL Próximo" (#d97706 amarillo)
   - "EOL OK" (#16a34a verde)

## CronJob Helm (diario)
Schedule: "0 3 * * *" (3:00 AM cada día)
Llama a POST /v1/eol/sync-all vía HTTP interno al backend.
