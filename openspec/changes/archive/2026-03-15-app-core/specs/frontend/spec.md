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

### Requirement: Selector de fecha y hora para historificación
El dashboard SHALL incluir un input `datetime-local` que permita seleccionar cualquier fecha y hora exacta para consultar el inventario en ese instante. Al activarlo, el header mostrará "● Histórico — dd/MM/yyyy HH:mm" en ámbar. Un botón "🟢 Volver a Live" permite cancelar el modo histórico.

#### Scenario: Selección de histórico con fecha y hora
- **GIVEN** un usuario en el dashboard
- **WHEN** selecciona una fecha y hora en el input datetime-local
- **THEN** la tabla muestra el inventario tal como estaba en ese momento exacto y el indicador cambia a ámbar

#### Scenario: Volver a modo Live
- **GIVEN** un usuario en modo histórico
- **WHEN** hace click en "Volver a Live"
- **THEN** el input se limpia y la tabla muestra datos en tiempo real

### Requirement: Filtro por click en etiqueta
Al hacer click en cualquier etiqueta mostrada en la tabla del inventario, SHALL activarse un filtro que muestre únicamente los activos que contienen esa etiqueta. La etiqueta activa se resalta con `ring-2`. Un segundo click en la misma etiqueta o el botón ✕ en el indicador de filtro activo lo elimina.

#### Scenario: Activar filtro por etiqueta
- **GIVEN** un usuario en el dashboard con activos que tienen etiquetas
- **WHEN** hace click en una etiqueta de cualquier fila
- **THEN** la tabla se actualiza mostrando solo activos con esa etiqueta, aparece un indicador del filtro activo y la etiqueta se resalta visualmente

#### Scenario: Desactivar filtro por etiqueta
- **GIVEN** un filtro de etiqueta activo
- **WHEN** el usuario hace click de nuevo en la misma etiqueta o pulsa el botón ✕
- **THEN** el filtro se elimina y la tabla vuelve a mostrar todos los activos

### Requirement: Perfil de usuario en header superior derecho
El layout de la aplicación SHALL mostrar en el header superior un área con el avatar, el nombre de usuario en `text-base font-semibold` y el rol en `text-xs` debajo, alineados a la derecha. Este header es visible en todas las páginas autenticadas. El área de perfil es un enlace a la página de perfil.

#### Scenario: Visualización del perfil en header
- **GIVEN** un usuario autenticado en cualquier página
- **WHEN** visualiza la aplicación
- **THEN** ve su avatar, nombre en texto grande y rol en texto pequeño en la esquina superior derecha

### Requirement: Roles y permisos
La aplicación SHALL mostrar/ocultar funciones según rol (admin/editor/viewer). Ejemplo: solo admin puede asignar tags masivos.

#### Scenario: Rol viewer
- **GIVEN** un usuario con rol `viewer`
- **WHEN** accede al dashboard
- **THEN** puede ver datos pero no ejecutar acciones de edición
