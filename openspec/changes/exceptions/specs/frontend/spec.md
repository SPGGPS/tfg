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
2. **Formulario de nueva excepción** — en la misma página, desplegable o en modal
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
El formulario SHALL incluir los siguientes campos en este orden:

**1. Activo/s** (obligatorio): campo de búsqueda con dropdown y checkboxes para selección múltiple. La búsqueda se activa con ≥1 carácter o con `*` para ver todos. Una nota visible bajo el campo indica: *"Escribe * para ver y seleccionar todos los activos disponibles"*. Al cerrar el dropdown se muestran los nombres de los activos seleccionados.

**2. Indicador** (obligatorio): botones EDR / MON / SIEM / LOGS / BCK / BCKCL. Un solo indicador por operación.

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

**4. Descripción adicional** (obligatorio siempre, mínimo 20 caracteres): textarea con contador visible. Detalla la justificación específica del caso concreto. No puede estar vacía aunque la razón sea autoexplicativa. El botón "Crear excepción" está deshabilitado hasta que se cumplan todos los campos obligatorios.

**5. Expira el** (opcional): input datetime-local. Si se deja vacío, la excepción es permanente.

El campo `reason` almacenado en BD es la concatenación legible: `"[Etiqueta de razón]: [Descripción]"`. La columna Motivo en la tabla muestra este valor compuesto.

Cuando se seleccionan múltiples activos, se crea una excepción por cada par (asset_id, indicator). Los activos que ya tengan excepción activa para ese indicador se omiten. La respuesta muestra cuántas se crearon y cuántas se omitieron.

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

#### Scenario: Búsqueda con asterisco muestra todos los activos
- **GIVEN** un admin escribe "*" en el campo de activos
- **THEN** dropdown con todos los activos disponibles y checkboxes

#### Scenario: Selección múltiple visible al cerrar dropdown
- **GIVEN** un admin marca 3 activos
- **WHEN** cierra el dropdown
- **THEN** el campo muestra "core-switch-01, access-switch-02, router-edge-01"

#### Scenario: Creación en múltiples activos con omisión
- **GIVEN** 3 activos seleccionados, 1 ya tiene excepción activa
- **WHEN** se confirma la creación
- **THEN** toast: "2 excepciones creadas, 1 omitida (ya existía)"


### Requirement: Color unificado de los botones de indicador en el formulario de excepción
Los botones de selección de indicador (EDR / MON / SIEM / LOGS / BCK / BCKCL) en el formulario SHALL tener todos el mismo color base (por ejemplo, el color primario de la aplicación, `bg-primary/20 text-primary border-primary/40`). El color diferenciado por indicador añade complejidad visual innecesaria en el contexto del formulario. El indicador seleccionado se resalta con `ring-2 ring-primary scale-105`.

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

### Requirement: Color triestado en badges de compliance (verde / azul / rojo)
La lógica de color de los rectángulos de compliance en la tabla de inventario SHALL ser:

| Estado | Color | Condición |
|--------|-------|-----------|
| Verde  | `bg-green-900/60 text-green-300 border-green-700` | El origen reporta OK |
| Azul   | `bg-blue-900/60 text-blue-300 border-blue-700`   | El origen reporta KO **pero existe excepción activa** |
| Rojo   | `bg-red-900/60 text-red-300 border-red-700`      | El origen reporta KO y **no hay excepción activa** |

El color azul indica "incumplimiento conocido, justificado y registrado". No es un estado de error, es un estado informativo.

Los datos de excepciones activas por activo vienen incluidos en la respuesta de GET /v1/assets (campo `exceptions`). El frontend calcula el color localmente sin llamadas extra.

Para los badges azules, el tooltip SHALL mostrar el motivo de la excepción y quién la creó. Ejemplo: "Excepción activa: Switch Cisco — no soporta agente EDR. Creada por admin el 15/03/2026".

#### Scenario: Switch con excepción de EDR — badge azul
- **GIVEN** un switch con edr_installed=false y excepción activa para "edr"
- **WHEN** se visualiza en la tabla de inventario
- **THEN** el badge EDR aparece en azul con tooltip mostrando el motivo

#### Scenario: Servidor sin EDR sin excepción — badge rojo
- **GIVEN** un servidor con edr_installed=false y sin excepción para "edr"
- **WHEN** se visualiza en la tabla
- **THEN** el badge EDR aparece en rojo

#### Scenario: Servidor con EDR activo — badge verde
- **GIVEN** un servidor con edr_installed=true
- **WHEN** se visualiza en la tabla
- **THEN** el badge EDR aparece en verde independientemente de si hay excepción

#### Scenario: Excepción expirada — vuelve a rojo
- **GIVEN** una excepción con expires_at en el pasado
- **WHEN** se visualiza el activo en la tabla
- **THEN** el backend no la incluye en el campo exceptions del activo → badge vuelve a rojo

#### Scenario: Origen reporta OK pero existe excepción activa — badge mitad azul mitad verde
- **GIVEN** un activo con edr_installed=true (origen reporta OK) Y existe una excepción activa para "edr"
- **WHEN** se visualiza en la tabla
- **THEN** el badge EDR muestra un gradiente diagonal mitad azul / mitad verde indicando "el dato llegó OK pero la excepción sigue activa"
- El tooltip muestra: "OK desde el origen. Excepción activa: [motivo]. Considera revocarla."

---

### Requirement: Badge cuadriestad en compliance (verde / azul-verde / azul / rojo)
La lógica de color de los rectángulos de compliance en la tabla de inventario SHALL ser:

| Estado | Color | Condición |
|--------|-------|-----------| 
| Verde puro | `bg-green-900/60 text-green-300 border-green-700` | Origen reporta OK. Sin excepción activa. |
| Mitad azul / mitad verde | Gradiente diagonal `from-blue-900/60 to-green-900/60`, texto blanco | Origen reporta OK **Y** existe excepción activa (excepción ya no necesaria — considerar revocar) |
| Azul puro | `bg-blue-900/60 text-blue-300 border-blue-700` | Origen reporta KO. Excepción activa justifica el incumplimiento. |
| Rojo puro | `bg-red-900/60 text-red-300 border-red-700` | Origen reporta KO. Sin excepción activa. |

El estado "mitad azul / mitad verde" es un aviso visual: el problema técnico se ha resuelto pero la excepción administrativa sigue abierta. No es un error, pero invita al admin a revocar la excepción obsoleta.

---

### Requirement: Leyenda de colores en pie de tabla de inventario
La leyenda al pie de la tabla de inventario SHALL mostrar únicamente los rectángulos de compliance (no círculos) con su significado. Los cuatro estados:
- Rectángulo **verde** → OK — el origen reporta el servicio activo
- Rectángulo **azul-verde** (gradiente) → OK con excepción activa — el servicio está activo pero la excepción no ha sido revocada
- Rectángulo **azul** → Excepción — incumplimiento justificado y registrado
- Rectángulo **rojo** → KO — incumplimiento sin justificar

No se mostrarán círculos ni ningún otro elemento gráfico adicional. El rectángulo es el único indicador visual de la leyenda.
