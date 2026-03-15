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

### Requirement: Formulario de creación de excepción
El formulario SHALL incluir:
- **Activo**: selector con búsqueda por nombre (typeahead) — obligatorio
- **Indicador**: selector con las opciones EDR / MON / SIEM / LOGS / BCK / BCKCL — obligatorio
- **Motivo**: textarea con contador de caracteres, mínimo 20 chars — obligatorio. El botón "Crear" está deshabilitado hasta que se cumple el mínimo.
- **Expira el**: input de fecha (date picker) — opcional. Si se deja vacío la excepción es permanente.

#### Scenario: Botón deshabilitado con motivo corto
- **GIVEN** un admin en el formulario con motivo de 10 caracteres
- **WHEN** observa el formulario
- **THEN** el botón "Crear excepción" está deshabilitado y el contador muestra "10/20 mínimo"

#### Scenario: Crear excepción exitosamente
- **GIVEN** un admin con activo seleccionado, indicador "EDR" y motivo ≥20 chars
- **WHEN** pulsa "Crear excepción"
- **THEN** la excepción se crea, la tabla se actualiza y aparece un toast de confirmación con "Excepción creada para [nombre activo] — EDR"

#### Scenario: Excepción duplicada
- **GIVEN** ya existe una excepción activa para ese activo e indicador
- **WHEN** se intenta crear
- **THEN** el formulario muestra un error inline "Ya existe una excepción activa para este indicador en este activo"

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

---

### Requirement: Leyenda de colores en pie de tabla de inventario
La leyenda al pie de la tabla de inventario SHALL incluir los tres estados:
- 🟢 OK — el origen de datos reporta el servicio activo
- 🔵 Excepción — incumplimiento justificado y registrado
- 🔴 KO — incumplimiento sin justificar
