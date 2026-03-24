id: exceptions

context: |
  Feature: Gestión de excepciones de compliance
  Domain: Cumplimiento y auditoría de activos.
  Motivación: Un switch no puede tener EDR. Un servidor legacy no puede enviar logs al SIEM.
  Sin excepciones, estos activos siempre aparecen en rojo (falsos positivos).
  Una excepción indica que el incumplimiento es conocido, justificado y aceptado.

proposal: |
  1. Tabla compliance_exceptions con soft-delete (revoked_at)
  2. Ciclo: admin crea excepción → activo → admin revoca
  3. Bulk: crear excepciones para múltiples assets a la vez (array asset_ids)
  4. Sistema de 4 estados visuales en badges de compliance:
       ok / ok_with_exception / ko_with_exception / ko
  5. Selector de assets en formulario: lista con checkboxes (no dropdown)
  6. Bulk delete en página de excepciones

status: Implementado al 100%.
