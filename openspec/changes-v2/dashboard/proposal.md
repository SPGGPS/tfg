id: dashboard

context: |
  Feature: Dashboard / Página principal del CMDB
  Motivación: El usuario necesita una vista rápida del estado del inventario
  sin navegar por cada sección. El dashboard agrega datos de múltiples módulos
  en gráficos de sectores interactivos.

proposal: |
  Página de inicio ("/dashboard") con 4 bloques de gráficos de sectores:

  Bloque 1 — EOL por tipo de producto
    Gráfico por asset.type: cuántos están EOL KO, EOL WARN, EOL OK, Sin datos

  Bloque 2 — Compliance (6 indicadores)
    Un gráfico por indicador (EDR, MON, SIEM, LOGS, BCK, BCKCL):
    sectores: OK, KO con excepción, KO sin excepción

  Bloque 3 — Backup
    Dos gráficos: Backup Local y Backup Cloud
    sectores: Con backup reciente, Sin backup, Sin datos

  Bloque 4 — Certificados TLS/SSL
    sectores: Válidos, Próximos a caducar (≤30d), Críticos (≤7d), Expirados

  Interacción (todos los gráficos):
    - Hover sobre sector → se destaca (scale + sombra) + tooltip flotante con
      listado de elementos (nombre + tipo/estado)
    - Click en sector → navega a /inventario (o /certificates) con filtros
      aplicados que muestren exactamente esos elementos

status: implementing
