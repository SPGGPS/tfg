# Frontend - Compliance Exceptions

## ADDED Requirements

### Requirement: Entrada "Excepciones" en menú lateral
El sidebar SHALL incluir una entrada "Excepciones" visible únicamente para rol 'admin'. Se posiciona entre "Fuentes de Datos" y "Auditoría". Icono: escudo con exclamación.

#### Scenario: Visibilidad por rol
- **GIVEN** un usuario con rol 'admin'
- **WHEN** carga la aplicación
- **THEN** el sidebar muestra la entrada "Excepciones"

#### Scenario: Oculto para editor y viewer
- **GIVEN** un usuario con rol 'editor' o 'viewer'
- **WHEN** carga la aplicación
- **THEN** la entrada "Excepciones" no aparece en el sidebar

---

### Requirement: Página de Excepciones (/exceptions)
La página SHALL mostrar:
1. **Tabla de excepciones activas** — columnas: Activo, Indicador, Motivo, Creada por, Fecha creación, Expira, Acciones (Revocar)
2. **Formulario de nueva excepción** — en la misma página, en modal al pulsar "Nueva excepción"
3. **Historial** — sección inferior con excepciones revocadas y expiradas

#### Scenario: Vista de excepciones activas
- **GIVEN** un admin en /exceptions
- **WHEN** carga la página
- **THEN** ve la tabla con todas las excepciones activas con sus campos

#### Scenario: Historial visible
- **GIVEN** existen excepciones revocadas o expiradas
- **WHEN** el admin visualiza /exceptions
- **THEN** la sección de historial muestra esas excepciones con estado (Revocada/Expirada), fecha de revocación y quién la revocó

---

### Requirement: Formulario de creación de excepción — razones predefinidas, descripción obligatoria y multi-activo

El formulario SHALL abrirse en un **modal** al pulsar el botón "Nueva excepción". Los campos se presentan en este orden:

**1. Indicador** (obligatorio, primero): botones EDR / MON / SIEM / LOGS / BCK / BCKCL. Se selecciona primero el indicador porque determina qué activos están disponibles. Un solo indicador por operación.

**2. Activo/s** (obligatorio): campo de búsqueda con dropdown y checkboxes para selección múltiple. El campo está deshabilitado hasta que se seleccione un indicador, mostrando el placeholder *"Selecciona primero un indicador"*.

Comportamiento del campo de búsqueda una vez habilitado:
- Se activa con ≥1 carácter O con `*` para ver todos los activos disponibles.
- Una nota visible bajo el campo indica: *"Escribe * para ver todos los activos, o busca por nombre"*.
- El dropdown muestra un listado con checkbox por cada activo. Cada fila muestra nombre y tipo del activo.
- Los activos que **ya tengan excepción activa para el indicador seleccionado** se muestran deshabilitados (grises, no seleccionables) con el texto *"Ya tiene excepción activa"* a la derecha. No se pueden marcar.
- Al cerrar el dropdown, el campo muestra los nombres de los activos seleccionados separados por coma.
- El dropdown se cierra al hacer clic fuera de él o al pulsar Escape.

**Sincronización al cambiar indicador**: cuando el usuario cambia el indicador seleccionado, el campo de activos recalcula qué activos están deshabilitados según el nuevo indicador. Los activos ya seleccionados que queden deshabilitados se desmarcan automáticamente y se muestra un aviso inline: *"X activos deseleccionados porque ya tienen excepción activa para este indicador"*.

**3. Razón predefinida** (obligatorio): selector desplegable con catálogo estandarizado. El usuario DEBE elegir una razón del catálogo. Opciones:
- `agent_not_supported` — "Agente no compatible con el hardware o sistema operativo del dispositivo"
- `network_device` — "Dispositivo de red (switch/router/AP) — no admite instalación de agentes de software"
- `excluded_backup` — "Excluido de política de backup por decisión de negocio aprobada"
- `excluded_monitoring` — "Excluido de monitorización — entorno aislado, de pruebas o DMZ"
- `excluded_siem` — "Excluido de envío de logs a SIEM — dato clasificado o entorno restringido"
- `legacy_system` — "Sistema legacy sin soporte para herramientas de seguridad actuales"
- `pending_deployment` — "Pendiente de despliegue — instalación/configuración en curso"
- `decommissioning` — "Activo en proceso de baja o retirada programada"
- `cloud_backup_only` — "Política de solo backup en cloud, sin backup local"
- `local_backup_only` — "Política de solo backup local, sin backup cloud"
- `temporary_exclusion` — "Exclusión temporal por mantenimiento o ventana de cambio"
- `other` — "Otro motivo — especificar en descripción"

**4. Descripción adicional** (obligatorio siempre, mínimo 20 caracteres): textarea con contador visible. Detalla la justificación específica del caso concreto. No puede estar vacía aunque la razón sea autoexplicativa.

**5. Expira el** (opcional): input datetime-local. Si se deja vacío, la excepción es permanente.

El botón "Crear excepción" está deshabilitado hasta que se cumplan todos los campos obligatorios (indicador, ≥1 activo, razón predefinida, descripción ≥20 chars).

El campo `reason` almacenado en BD es la concatenación legible: `"[Etiqueta de razón]: [Descripción]"`. La columna Motivo en la tabla muestra este valor compuesto.

Cuando se seleccionan múltiples activos, se crea una excepción por cada par (asset_id, indicator). Los activos que ya tengan excepción activa para ese indicador se omiten sin error. La respuesta muestra cuántas se crearon y cuántas se omitieron mediante un toast.

**Manejo de errores al guardar**: si la llamada a la API falla (error 4xx o 5xx), el modal SHALL permanecer abierto y mostrar un mensaje de error inline claro bajo el botón, sin cerrar el formulario ni perder los datos introducidos. El botón "Crear excepción" se re-habilita para que el usuario pueda reintentar. No se usa alert() ni navegación. Ejemplos de mensajes:
- Error 409 (duplicado no esperado): "Ya existe una excepción activa para uno de los activos seleccionados"
- Error 404 (activo no encontrado): "Uno o más activos no se han encontrado. Recarga la página."
- Error 422 (validación): muestra el detalle de validación devuelto por la API
- Error 500 o red: "Error al guardar. Inténtalo de nuevo."

#### Scenario: Indicador seleccionado primero habilita el campo de activos
- **GIVEN** un admin abre el modal de nueva excepción
- **WHEN** aún no ha seleccionado indicador
- **THEN** el campo de activos está deshabilitado con placeholder "Selecciona primero un indicador"
- **WHEN** selecciona el indicador "EDR"
- **THEN** el campo de activos se habilita

#### Scenario: Asterisco muestra todos los activos con estado
- **GIVEN** un admin escribe "*" en el campo de activos con indicador "edr" seleccionado
- **THEN** dropdown con todos los activos; los que ya tienen excepción para "edr" aparecen deshabilitados en gris con texto "Ya tiene excepción activa"

#### Scenario: Activos con excepción no son seleccionables
- **GIVEN** core-switch-01 ya tiene excepción activa para "edr"
- **WHEN** el admin escribe "*" con indicador "edr"
- **THEN** core-switch-01 aparece en el dropdown pero el checkbox está deshabilitado y no puede marcarse

#### Scenario: Cambio de indicador desmarca activos bloqueados
- **GIVEN** un admin ha seleccionado indicador "edr" y marcado 3 activos, 1 de los cuales tiene excepción activa para "mon"
- **WHEN** cambia el indicador a "mon"
- **THEN** ese activo se desmarca automáticamente y aparece un aviso "1 activo deseleccionado porque ya tiene excepción activa para este indicador"

#### Scenario: Error al guardar no cierra el modal
- **GIVEN** un admin rellena el formulario correctamente y pulsa "Crear excepción"
- **WHEN** la API devuelve un error 500
- **THEN** el modal permanece abierto, los datos del formulario se conservan, y aparece el mensaje "Error al guardar. Inténtalo de nuevo." bajo el botón

#### Scenario: Razón predefinida obligatoria
- **GIVEN** un admin con activos y descripción rellenos pero sin razón seleccionada
- **WHEN** observa el formulario
- **THEN** el botón "Crear excepción" está deshabilitado

#### Scenario: Descripción obligatoria siempre
- **GIVEN** un admin que selecciona "Dispositivo de red" como razón
- **WHEN** deja la descripción con menos de 20 caracteres
- **THEN** el botón "Crear excepción" permanece deshabilitado

#### Scenario: Motivo compuesto visible en tabla
- **GIVEN** razón "Dispositivo de red" y descripción "Switch Cisco del CPD principal"
- **WHEN** la excepción se guarda y aparece en la tabla
- **THEN** la columna "Motivo" muestra "Dispositivo de red: Switch Cisco del CPD principal"

#### Scenario: Selección múltiple visible al cerrar dropdown
- **GIVEN** un admin marca 3 activos
- **WHEN** cierra el dropdown
- **THEN** el campo muestra "core-switch-01, access-switch-02, router-edge-01"

#### Scenario: Creación en múltiples activos con omisión
- **GIVEN** 3 activos seleccionados, 1 ya tiene excepción activa
- **WHEN** se confirma la creación
- **THEN** toast: "2 excepciones creadas, 1 omitida (ya existía)"

---

### Requirement: Color unificado de los botones de indicador en el formulario de excepción
Los botones de selección de indicador (EDR / MON / SIEM / LOGS / BCK / BCKCL) en el formulario SHALL tener todos el mismo color base (`bg-primary/20 text-primary border-primary/40`). El indicador seleccionado se resalta con `ring-2 ring-primary scale-105`.

#### Scenario: Todos los indicadores con el mismo color base
- **GIVEN** un admin en el formulario de nueva excepción
- **WHEN** visualiza los botones de indicador
- **THEN** todos tienen el mismo estilo base y solo el seleccionado se resalta con ring

---

### Requirement: Revocar excepción
Cada fila de la tabla de excepciones activas SHALL tener un botón "Revocar". Al pulsarlo se abre un modal de confirmación que muestra el motivo original y pide confirmación.

#### Scenario: Modal de confirmación al revocar
- **GIVEN** un admin pulsa "Revocar" en una excepción
- **WHEN** se abre el modal
- **THEN** muestra el nombre del activo, el indicador y el motivo original de la excepción, con botones "Cancelar" y "Confirmar revocación"

#### Scenario: Revocación registrada en historial
- **GIVEN** un admin confirma la revocación
- **WHEN** la operación es exitosa
- **THEN** la excepción desaparece de la tabla activa, aparece en el historial con estado "Revocada", la fecha y el nombre del admin que la revocó

---

### Requirement: Color cuadriestad en badges de compliance (4 estados)
Los rectángulos de compliance en la tabla de inventario son **rectángulos con texto**, nunca círculos.

La lógica de color SHALL ser:

| Estado | Color | Condición |
|--------|-------|-----------|
| Verde | `bg-green-900/60 text-green-300 border-green-700` | Origen OK. Sin excepción activa. |
| Azul-verde (gradiente) | `compliance-gradient` — diagonal azul→verde | Origen OK **Y** excepción activa — el dato llega pero la excepción sigue, considerar revocar. |
| Rojo-azul (gradiente) | `compliance-gradient-temp` — diagonal rojo→azul | Origen KO **Y** excepción activa — el dato NO llega, pero el incumplimiento está justificado (permanente o temporal). |
| Rojo | `bg-red-900/60 text-red-300 border-red-700` | Origen KO. Sin excepción activa. |

**Principio fundamental:** el gradiente siempre muestra los dos estados combinados. El rojo-azul indica que el dato del origen no llega (rojo) PERO hay una excepción registrada (azul). Nunca azul puro — eso ocultaría si el origen reporta o no.

**Distinción permanente/temporal:** ya no afecta al color del badge. Ambos tipos de excepción usan el mismo gradiente rojo-azul. La distinción permanente/temporal es informativa (se ve en la columna "Expira" de la tabla de excepciones) pero no cambia el color del compliance.

**No hay distinción de color entre excepción permanente y temporal.** Ambas usan el gradiente rojo-azul. La información de permanencia/temporalidad se muestra en la columna "Expira" de la tabla de excepciones.

Para todos los badges con excepción, el tooltip SHALL mostrar: motivo, quién la creó y fecha. Para azul-verde añadir sugerencia de revocar.

Los datos vienen en `exceptions` de GET /v1/assets. El frontend calcula el color localmente.

#### Scenario: Switch con excepción de EDR — badge rojo-azul
- **GIVEN** un switch con edr_installed=false y excepción activa para "edr" (permanente o temporal)
- **WHEN** se visualiza en la tabla
- **THEN** el badge EDR aparece con gradiente rojo-azul (origen KO + excepción registrada)

#### Scenario: Servidor con excepción temporal de EDR — mismo gradiente rojo-azul
- **GIVEN** un servidor con edr_installed=false y excepción con reason_code="pending_deployment"
- **WHEN** se visualiza en la tabla
- **THEN** el badge EDR aparece con el mismo gradiente rojo-azul que una excepción permanente

#### Scenario: Servidor sin EDR sin excepción — badge rojo
- **GIVEN** un servidor con edr_installed=false y sin excepción
- **WHEN** se visualiza en la tabla
- **THEN** el badge EDR aparece rojo puro

#### Scenario: Servidor con EDR activo — badge verde
- **GIVEN** un servidor con edr_installed=true y sin excepción activa
- **WHEN** se visualiza en la tabla
- **THEN** el badge EDR aparece verde puro

#### Scenario: Origen OK pero excepción activa — badge azul-verde
- **GIVEN** un activo con edr_installed=true Y excepción activa para "edr"
- **WHEN** se visualiza en la tabla
- **THEN** el badge EDR muestra gradiente azul-verde con tooltip sugiriendo revocar

#### Scenario: Excepción expirada — vuelve a rojo
- **GIVEN** una excepción con expires_at en el pasado
- **WHEN** se visualiza el activo
- **THEN** el badge vuelve a rojo puro

---

### Requirement: Leyenda de colores en pie de tabla de inventario
La leyenda al pie de la tabla SHALL mostrar los **cuatro estados** con rectángulos (no círculos):
- Rectángulo **verde** → OK — el origen reporta el servicio activo
- Rectángulo **azul-verde** (gradiente) → OK + excepción activa — el dato llega pero hay excepción, considerar revocar
- Rectángulo **rojo-azul** (gradiente) → KO con excepción — el dato NO llega, incumplimiento justificado
- Rectángulo **rojo** → KO — incumplimiento sin justificar

No se mostrarán círculos, azul puro ni ningún otro elemento gráfico adicional.

---

### Requirement: Actualización inmediata del inventario tras crear o revocar excepción

Cuando el usuario crea o revoca una excepción desde la página de Excepciones, la tabla de inventario SHALL reflejar el nuevo estado de compliance **sin necesidad de recargar la página manualmente**.

**Implementación correcta con TanStack Query:**
- Al crear una excepción: `queryClient.invalidateQueries({ queryKey: ['assets'], exact: false })`
- Al revocar una excepción: `queryClient.invalidateQueries({ queryKey: ['assets'], exact: false })`

La clave `exact: false` es **obligatoria** porque la query del inventario tiene una clave compuesta con parámetros: `['assets', { search, type, tag_ids, as_of, sort_by, sort_order, page, page_size }]`. Sin `exact: false`, la invalidación no matchea ninguna query activa y la tabla no se refresca.

**Anti-patrón a evitar:**
```javascript
// ❌ INCORRECTO — no matchea ['assets', params]
queryClient.invalidateQueries(['assets'])

// ✅ CORRECTO — invalida todas las queries que empiecen por ['assets']
queryClient.invalidateQueries({ queryKey: ['assets'], exact: false })
```

#### Scenario: Badge se actualiza al crear excepción sin recargar página
- **GIVEN** un servidor con edr_installed=false (badge EDR rojo) en la tabla de inventario
- **WHEN** el admin crea una excepción para "edr" en ese servidor desde la página Excepciones
- **THEN** el badge EDR del servidor en la tabla de inventario cambia a azul (o azul-rojo según el reason_code) **automáticamente**, sin que el usuario recargue la página

#### Scenario: Badge vuelve a rojo al revocar excepción
- **GIVEN** un switch con badge EDR azul (excepción activa)
- **WHEN** el admin revoca la excepción desde la página Excepciones
- **THEN** el badge EDR del switch en la tabla de inventario cambia a rojo automáticamente

#### Scenario: Invalidación con parámetros de filtro activos
- **GIVEN** el usuario tiene activo un filtro de búsqueda en el inventario (`search=switch`)
- **WHEN** se crea una excepción para un asset
- **THEN** la tabla filtrada se refresca igualmente y muestra el nuevo estado de compliance
---

### Requirement: Selección múltiple y eliminación masiva en tabla de excepciones

La tabla de excepciones activas SHALL soportar selección múltiple para revocar varias excepciones a la vez.

**Checkbox en cabecera:** selecciona/deselecciona todas las filas visibles.
**Checkbox en cada fila:** selecciona/deselecciona esa excepción.
**Botón "Revocar seleccionadas (N)":** aparece en la cabecera de la página cuando hay al menos una fila seleccionada. Requiere confirmación antes de ejecutar. Se deshabilita mientras la operación está en curso.

#### Scenario: Selección múltiple y revocación masiva
- **GIVEN** 4 excepciones activas en la tabla
- **WHEN** el admin selecciona 3 con los checkboxes y pulsa "Revocar seleccionadas (3)"
- **THEN** aparece un confirm, al aceptar se revocan las 3, la tabla se actualiza y el inventario refresca los badges

#### Scenario: Checkbox cabecera selecciona todas
- **GIVEN** 4 excepciones visibles, 0 seleccionadas
- **WHEN** el admin pulsa el checkbox de la cabecera
- **THEN** las 4 filas quedan seleccionadas y el botón muestra "Revocar seleccionadas (4)"

---

### Requirement: Ordenación por columna en tabla de excepciones

La tabla de excepciones activas SHALL tener ordenación por columna con iconos ↑↓, igual que la tabla de inventario.

**Columnas ordenables:** Activo, Indicador, Creada por, Fecha creación, Expira.
**Columna Motivo:** no ordenable (texto libre largo).
**Ordenación por defecto:** Fecha creación descendente (más recientes primero).
**Comportamiento:** primer click = asc, segundo click = desc, tercer click = asc (toggle).

La ordenación es **client-side** sobre los datos ya cargados (no requiere nueva llamada a la API), dado que el listado de excepciones activas es típicamente pequeño (<200 registros).

#### Scenario: Ordenar por Activo
- **GIVEN** varias excepciones de distintos activos
- **WHEN** el admin pulsa la cabecera "Activo"
- **THEN** las filas se ordenan alfabéticamente por nombre de activo (asc)

#### Scenario: Ordenar por Expira — permanentes al final
- **GIVEN** mezcla de excepciones con y sin fecha de expiración
- **WHEN** el admin ordena por "Expira" asc
- **THEN** las excepciones con fecha más próxima aparecen primero; las permanentes (sin fecha) al final
