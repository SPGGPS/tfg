# Frontend - Plataforma Core (Inventario + Compliance + Tags)

## ADDED Requirements

### Requirement: Login OpenID (Keycloak) con PKCE
La aplicación SHALL implementar el flujo OpenID Connect Authorization Code + PKCE y almacenar tokens en cookies HttpOnly/Secure.

#### Scenario: Usuario logueado
- **GIVEN** un usuario con credenciales válidas
- **WHEN** completa el login con Keycloak
- **THEN** la aplicación recibe tokens y muestra el dashboard de inventario

### Requirement: Dashboard de inventario con compliance
El dashboard SHALL mostrar una tabla de activos que incluya:
- Tipo (servidor, switch, router, ap)
- Último backup (`last_backup`)
- Estado EDR (`edr_installed`)
- Estado monitorización (`monitored`)
- Estado logs (`logs_enabled`)
- Última sincronización (`last_sync`)
- Tags (manuales + automáticas)

#### Scenario: Visualización de compliance
- **GIVEN** un usuario en el dashboard
- **WHEN** carga la lista de activos
- **THEN** cada fila muestra badges/íconos para compliance y tags

### Requirement: Filtros, ordenación y búsqueda
El dashboard SHALL soportar filtros por tipo, tags, estado de compliance y texto libre.

#### Scenario: Filtrado y ordenación
- **GIVEN** un usuario en el dashboard
- **WHEN** aplica filtros o ordena columnas
- **THEN** la tabla se actualiza mostrando los resultados correspondientes

### Requirement: Selector de historificación (Live / hora)
El dashboard SHALL permitir elegir entre ver datos en vivo o ver el inventario a una hora específica (ciclos horarios).

#### Scenario: Selección de histórico
- **GIVEN** un usuario en el dashboard
- **WHEN** selecciona un timestamp pasado
- **THEN** la tabla muestra los datos del inventario en esa fecha/hora

### Requirement: Roles y permisos
La aplicación SHALL mostrar/ocultar funciones según rol (admin/editor/viewer). Ejemplo: solo admin puede asignar tags masivos.

#### Scenario: Rol viewer
- **GIVEN** un usuario con rol `viewer`
- **WHEN** accede al dashboard
- **THEN** puede ver datos pero no ejecutar acciones de edición
