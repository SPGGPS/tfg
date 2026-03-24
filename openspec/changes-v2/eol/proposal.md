id: eol

context: |
  Feature: Gestión de End of Life (EOL) de productos software
  Fuente externa: https://endoflife.date/api — 445+ productos, actualización continua
  Motivación: El Ayuntamiento necesita saber qué versiones de software en producción
  están sin soporte o próximas a EOL para planificar renovaciones.

proposal: |
  1. Catálogo de productos EOL sincronizados desde endoflife.date
  2. Vista de ciclos de vida con fechas de lanzamiento, fin de soporte y EOL
  3. Valores custom por ciclo — sobrescriben los de la API (ej: EOL interno diferente)
  4. Botón "Sync" manual por producto y botón "Sync todo"
  5. Proceso automático diario (CronJob Helm) que marca unsynced los que desaparecen
  6. Etiquetas automáticas EOL en activos del inventario:
       EOL rojo     → ya sin soporte
       EOL amarillo → ≤ 1 año para EOL
       EOL verde    → > 2 años para EOL
  7. Badge sync/unsynced con fecha de última sincronización

status: Implementado al 100%.
