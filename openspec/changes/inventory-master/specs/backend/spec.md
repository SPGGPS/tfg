# Backend - Inventario (FastAPI + Sync)

## ADDED Requirements

### Requirement: Ingesta horaria y sincronización
El backend SHALL exponer endpoints protegidos para ingestión de datos cada hora (Veeam, VMware, EDR, monitorización) y actualizar `last_sync`.

#### Scenario: Sincronización horaria
- **GIVEN** un servicio de ingestión con credenciales válidas
- **WHEN** llama al endpoint de ingestión
- **THEN** el backend actualiza assets, registra `last_sync` y almacena historial por hora

### Requirement: Historial por hora (as_of)
El backend SHALL mantener un historial por hora que permita consultar el inventario en un momento puntual con un query param `as_of`.

#### Scenario: Consulta histórica
- **GIVEN** inventario histórico almacenado por hora
- **WHEN** un cliente solicita GET /v1/assets?as_of=2026-03-15T13:00:00Z
- **THEN** el backend retorna el inventario tal como estaba a esa hora

### Requirement: Compliance fields en el modelo de datos
El backend SHALL incluir en el modelo Asset los campos: `edr_installed`, `last_backup`, `monitored`, `logs_enabled`, `last_sync`, `name`, `ips`, `vendor`, `source`, y campos específicos por tipo (ram_gb, total_disk_gb, cpu_count, os para servidores; model, port_count, firmware_version para routers; etc.).

#### Scenario: Respuesta con compliance y datos básicos
- **GIVEN** un activo en la base de datos
- **WHEN** un cliente llama GET /v1/assets
- **THEN** la respuesta contiene todos los campos de compliance, básicos y específicos según el tipo


