# Backend - Core (FastAPI + Datos)

## ADDED Requirements

### Requirement: Arquitectura del backend
El backend SHALL estar implementado en FastAPI con una capa de servicios clara (ingesta, sincronización, API) y un modelo de datos relacional en PostgreSQL.

#### Scenario: Estructura de servicios
- **GIVEN** un desarrollador revisando el repositorio
- **WHEN** explora el código del backend
- **THEN** encuentra separadas las capas: modelos, repositorios, servicios y routers

### Requirement: Persistencia y versionado histórico
El backend SHALL guardar el inventario y su historial por hora para permitir consultas "as_of".

#### Scenario: Histórico de inventario
- **GIVEN** datos de inventario procesados cada hora
- **WHEN** el backend recibe una petición con `as_of`
- **THEN** responde con el inventario tal como estaba en ese timestamp

### Requirement: Ingestión de datos externa
El backend SHALL exponer endpoints (protegidos) para ingestión desde Veeam, VMware, EDR y monitorización, ejecutados cada hora.

#### Scenario: Ingestión horaria
- **GIVEN** un sistema externo con credenciales válidas
- **WHEN** llama al endpoint de ingestión
- **THEN** el backend procesa y actualiza `last_sync` en los assets

### Requirement: Integración con audit-logs
El backend SHALL utilizar el motor de audit-logs para registrar cambios críticos (tags, inventario, login).

#### Scenario: Auditoría de cambio de etiqueta
- **GIVEN** un admin cambia el color de una etiqueta manual
- **WHEN** el cambio se procesa
- **THEN** se crea un registro de auditoría con el diff JSON
