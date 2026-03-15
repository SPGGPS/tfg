# Frontend - Dashboard de inventario

## ADDED Requirements

### Requirement: Búsqueda por todos los campos mostrados

El dashboard SHALL incluir un botón de búsqueda que permita buscar por todos los campos visibles.

#### Scenario: Búsqueda por texto
- **GIVEN** un usuario en el dashboard de inventario
- **WHEN** introduce texto en el campo de búsqueda
- **THEN** la tabla se filtra mostrando solo activos que coinciden en algún campo visible

### Requirement: Ordenación por todos los campos

El dashboard SHALL permitir ordenar la tabla por todos los campos mostrados.

#### Scenario: Ordenar por columna
- **GIVEN** un usuario en la tabla de activos
- **WHEN** hace clic en el encabezado de una columna
- **THEN** la tabla se reordena según ese campo (asc/desc)

### Requirement: Columnas de estado de cumplimiento y sincronización
El dashboard SHALL mostrar las columnas obligatorias para cumplimiento y sincronización:
- Último backup (`last_backup`)
- Estado de monitorización (`monitored`)
- Estado de EDR (`edr_installed`)
- Última sincronización (`last_sync`)

#### Scenario: Muestra datos de compliance
- **GIVEN** un usuario en el dashboard de inventario
- **WHEN** carga la tabla de activos
- **THEN** cada registro muestra valores en las columnas de backup, monitorización, EDR y sincronización

### Requirement: Filtro por tipo de activo
El dashboard SHALL incluir un selector para filtrar por tipo de activo (server_physical, server_virtual, switch, router, ap) o "Todos".

#### Scenario: Filtrar por tipo específico
- **GIVEN** un usuario en el dashboard
- **WHEN** selecciona un tipo específico (ej. "switch")
- **THEN** la tabla muestra solo activos de ese tipo

#### Scenario: Mostrar todos los tipos
- **GIVEN** un usuario selecciona "Todos"
- **WHEN** carga la tabla
- **THEN** se muestran columnas adicionales: Nombre, Tipo, IP(s), Fabricante, Origen

### Requirement: Columnas adicionales para vista "Todos"
Cuando se selecciona "Todos", el dashboard SHALL mostrar estas columnas adicionales:
- Nombre del activo (`name`)
- Tipo de dispositivo (`type`)
- IP(s) (`ips`) - lista de direcciones IP si aplica
- Fabricante (`vendor`) - ej. Cisco, VMware, Dell
- Origen de datos (`source`) - ej. VMware, Veeam, Monica, ServiceNow, EDR, Monitorización

#### Scenario: Vista completa con datos detallados
- **GIVEN** un usuario selecciona "Todos"
- **WHEN** la tabla se carga
- **THEN** cada fila incluye nombre, tipo, IPs, fabricante y origen, además de los campos de compliance

### Requirement: Columnas específicas por tipo de activo
Cuando se selecciona un tipo específico, el dashboard SHALL mostrar columnas detalladas específicas de ese tipo, además de las de compliance.

#### Scenario: Vista de servidores (server_physical o server_virtual)
- **GIVEN** un usuario selecciona "server_physical" o "server_virtual"
- **WHEN** la tabla se carga
- **THEN** muestra columnas: Nombre, IP, RAM (GB), Suma de discos (GB), Número de CPUs, Sistema Operativo

#### Scenario: Vista de routers
- **GIVEN** un usuario selecciona "router"
- **WHEN** la tabla se carga
- **THEN** muestra columnas: Nombre, IP, Fabricante, Modelo, Número de puertos, Versión de firmware

#### Scenario: Vista de switches
- **GIVEN** un usuario selecciona "switch"
- **WHEN** la tabla se carga
- **THEN** muestra columnas: Nombre, IP, Fabricante, Modelo, Número de puertos, Velocidad máxima

#### Scenario: Vista de access points (ap)
- **GIVEN** un usuario selecciona "ap"
- **WHEN** la tabla se carga
- **THEN** muestra columnas: Nombre, IP, Fabricante, Modelo, Área de cobertura, Número de clientes conectados



### Requirement: Historificación con selector de momento
El dashboard SHALL permitir seleccionar "Live" o un momento pasado (día y hora) para consultar el inventario histórico.

#### Scenario: Vista Live vs histórico
- **GIVEN** un usuario en el dashboard
- **WHEN** selecciona "Live" o un día/hora del desplegable
- **THEN** la tabla muestra el inventario en ese momento temporal

### Requirement: Autenticación OpenID (Keycloak)
La aplicación frontend SHALL autenticarse mediante OpenID Connect (Authorization-Code + PKCE) y manejar roles para visualizar datos.

#### Scenario: Login con Keycloak
- **GIVEN** un usuario en la pantalla de inicio de sesión
- **WHEN** completa el flujo de autorización con Keycloak
- **THEN** obtiene un token válido y puede ver el dashboard de inventario

#### Scenario: Roles y visibilidad
- **GIVEN** un usuario logueado con rol `viewer` o `editor`
- **WHEN** accede al dashboard
- **THEN** solo puede visualizar los datos sin poder ejecutar acciones prohibidas (como asignar etiquetas masivas)
