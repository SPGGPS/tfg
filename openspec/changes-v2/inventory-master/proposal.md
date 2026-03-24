id: inventory-master

# Contexto
context: |
  Feature: Inventario centralizado de activos (CMDB)
  Domain: Gestión de activos IT — servidores, red, bases de datos.
  Integraciones: VMware vCenter, Veeam, EDR (CrowdStrike/SentinelOne), Monica, Zabbix/Nagios.
  Compliance: EDR, backup local, backup cloud, monitorización, SIEM, logs.
  Etiquetado dual: automático (sistema) y manual (admin).

# Qué implementa este change
proposal: |
  1. Modelo Asset polimórfico con discriminador "type":
       server_physical, server_virtual, switch, router, ap, database
  2. Campos de compliance: edr_installed, monitored, siem_enabled, logs_enabled,
       last_backup_local, last_backup_cloud, last_sync
     (solo escritura por ingesta — no editables por usuarios)
  3. Tipo "database" con campos específicos: db_engine, db_version, db_port,
       db_replication, db_schemas, db_users, etc.
  4. Etiquetas de sistema generadas automáticamente por tagging_service.py
  5. Bulk tags: POST /v1/assets/bulk-tags para asignar etiquetas a múltiples activos
  6. Tabla de inventario con badges de compliance, ordenación, filtros, paginación
  7. Histórico horario (AssetHistory) con parámetro as_of
  8. Página de detalle /assets/:id

# Estado
status: Implementado al 95%. Pendiente: ubicación en columna de inventario.
