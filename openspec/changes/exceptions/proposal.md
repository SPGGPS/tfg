id: exceptions

# openspec/changes/exceptions/.openspec.yaml
schema: spec-driven
created: 2026-03-15

# Contexto: Gestión de Excepciones de Compliance
context: |
  Feature: Compliance Exceptions Management
  Domain: Cumplimiento y auditoría de activos.
  Motivation: Determinados activos no pueden cumplir ciertos indicadores de compliance
  por razones técnicas o de negocio justificadas. Por ejemplo, un switch no puede
  tener agente EDR instalado, o un servidor legacy no puede enviar logs al SIEM.
  Sin un mecanismo de excepciones, estos activos aparecerían siempre en rojo
  generando falsos positivos que degradan la utilidad del dashboard.
  
  Una excepción indica que el estado rojo de un indicador concreto en un activo
  concreto es conocido, justificado y aceptado. El indicador pasa a mostrarse en
  azul en lugar de rojo, diferenciando "incumplimiento sin justificar" (rojo) de
  "incumplimiento justificado y registrado" (azul).

# Definición del Cambio
proposal: |
  Implementar un módulo de gestión de excepciones de compliance:
  1. Modelo de datos: tabla compliance_exceptions con asset_id, indicator, reason,
     created_by, created_at, expires_at (opcional), revoked_by, revoked_at.
  2. API REST: CRUD de excepciones bajo /v1/exceptions, restringido a admin.
  3. Frontend: nueva entrada "Excepciones" en el menú lateral (solo admin), página
     con tabla de excepciones activas y formulario de creación.
  4. Efecto visual: cuando un activo tiene una excepción activa para un indicador,
     el rectángulo correspondiente (EDR/MON/SIEM/LOGS/BCK/BCKCL) se muestra en
     AZUL en lugar de rojo. Verde sigue siendo OK, rojo es incumplimiento sin
     justificar, azul es incumplimiento justificado con excepción activa.
  5. Registro inmutable: cada excepción registra quién la creó, cuándo y por qué.
     Las revocaciones también se registran. El historial es visible en la misma
     pantalla de excepciones.

# Reglas de implementación
rules:
  openapi_spec:
    - Endpoint 'POST /v1/exceptions': requiere rol 'admin'. Campos obligatorios:
      asset_id, indicator (enum), reason (string, min 20 chars para forzar justificación real).
    - Endpoint 'GET /v1/exceptions': lista excepciones con filtros por asset_id,
      indicator, status (active/revoked/expired). Rol viewer+.
    - Endpoint 'DELETE /v1/exceptions/{id}': revoca (soft delete) la excepción.
      Registra revoked_by y revoked_at. Rol admin.
    - El modelo GET /v1/assets debe incluir en cada activo un campo 'exceptions'
      con las excepciones activas para poder calcular el color del badge en frontend.
    - El campo 'indicator' es un enum estricto: edr, mon, siem, logs, bck, bckcl.

  backend_code:
    - Inmutabilidad parcial: no existe PUT/PATCH sobre excepciones. Solo crear (POST)
      y revocar (DELETE soft). La revocación no borra el registro, lo marca como revocado.
    - Una excepción es 'activa' si: revoked_at IS NULL y (expires_at IS NULL o expires_at > now()).
    - Validar que el asset_id existe antes de crear la excepción.
    - Validar que no existe ya una excepción activa para el mismo (asset_id, indicator).
      Si existe, devolver 409 Conflict con el id de la excepción existente.
    - Registrar en audit_logs la creación y revocación de excepciones.

  frontend_code:
    - Menú lateral: nueva entrada "Excepciones" con icono de escudo con exclamación,
      visible solo para rol 'admin'. Posición: entre "Fuentes de Datos" y "Auditoría".
    - Lógica de color de badges en la tabla de inventario:
        Verde  → el origen reporta OK (bool true o datetime con valor)
        Azul   → el origen reporta KO pero existe excepción activa para ese indicador
        Rojo   → el origen reporta KO y no hay excepción activa
    - Página de excepciones: tabla de excepciones con columnas Activo, Indicador,
      Motivo, Creada por, Fecha creación, Expira, Estado (Activa/Revocada/Expirada).
    - Formulario de creación: selector de activo (búsqueda por nombre), selector de
      indicador (EDR/MON/SIEM/LOGS/BCK/BCKCL), campo de motivo obligatorio (mínimo
      20 caracteres con contador), fecha de expiración opcional.
    - El motivo es obligatorio y tiene una longitud mínima para forzar una
      justificación real, no un texto vacío o trivial.
    - Historial visible: en la misma página, debajo de la tabla de activas, una
      sección "Historial" con las excepciones revocadas y expiradas.
    - Al revocar: modal de confirmación con el motivo de la excepción original.

# Dependencias
dependencies:
  - inventory-master  # necesita el modelo Asset y los indicadores de compliance
  - audit-logs        # las creaciones/revocaciones se registran en audit_logs
  - login             # requiere JWT con rol admin para crear/revocar

# Desglose de tareas
tasks:
  - name: "DB: Modelo compliance_exceptions con índices en (asset_id, indicator, revoked_at)"
    hours: 2
  - name: "Backend: CRUD API /v1/exceptions con validaciones y audit trail"
    hours: 3
  - name: "Backend: Enriquecer GET /v1/assets con campo exceptions por activo"
    hours: 2
  - name: "Frontend: Página de excepciones con tabla, formulario y historial"
    hours: 4
  - name: "Frontend: Lógica de color triestado (verde/azul/rojo) en badges de compliance"
    hours: 2
