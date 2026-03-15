id: inventory-master

# openspec/changes/inventory-master/.openspec.yaml
schema: spec-driven
created: 2026-03-14

# Contexto: CMDB Centralizado, Auditoría de Cumplimiento y Etiquetado Dinámico
context: |
  Feature: Centralized Inventory, Compliance Audit & Asset Tagging
  Domain: Gestión de activos (Servidores físicos/virtuales, Networking).
  Integrations: Ingesta de datos desde VMware (vCenter), Veeam (Backups), Monica (Assets), EDR y Monitorización.
  Compliance Logic: Cada activo debe validar el estado de: EDR, Backup, Monitorización y Logs.
  Sync Frequency: Ejecución horaria (Cada 60 minutos).
  Tagging System: 
    - Automáticas: Asignadas por backend según tipo/estado (ej: 'Virtual', 'Cisco', 'On').
    - Manuales: Creadas por Admin y asignables a activos de forma individual o masiva.

# Definición del Cambio
proposal: |
  Definir el contrato de API para la gestión del inventario, ingesta masiva y etiquetado:
  1. Esquema de activos unificado para Servidores y Red con soporte para etiquetas.
  2. Endpoints de ingesta protegidos para sincronización horaria con herramientas externas.
  3. Campos de auditoría de seguridad (EDR_status, backup_status, etc.).
  4. Sistema de etiquetas dual: Automáticas (Backend) y Manuales (Admin).
  5. Funcionalidad de asignación masiva de etiquetas manuales a activos seleccionados.

# Reglas de implementación para el inventario
rules:
  openapi_spec:
    - Definir modelos polimórficos para activos (discriminador: type [server_physical, server_virtual, switch, router, ap]).
    - El modelo Asset debe incluir un array 'tags' que contenga objetos Tag (id, name, color, origin).
    - Endpoint 'POST /v1/assets/bulk-tags': Para asignar etiquetas manuales a múltiples asset_ids simultáneamente.
    - Campos obligatorios de cumplimiento: 'edr_installed' (bool), 'last_backup' (datetime), 'monitored' (bool), 'logs_enabled' (bool).
    - Validación de seguridad: Patterns y maxLength en todos los inputs para mitigar inyecciones.
  backend_code:
    - Lógica de Auto-Tagging: Al procesar datos de VMware o Red, asignar etiquetas de sistema (ej: 'Cisco' si el vendor es cisco, 'Virtual' si viene de vCenter).
    - Implementar lógica de 'Upsert' basada en identificadores únicos (UUID/MAC).
    - El backend debe impedir que un usuario borre o modifique etiquetas cuyo 'origin' sea 'system'.
    - Rendimiento: Procesamiento asíncrono para ingestas masivas horarias.
  frontend_code:
    - Dashboard: Componentes visuales (Badges) para cumplimiento y etiquetas.
    - Estilo de Etiquetas: Las manuales deben tener colores vibrantes (definidos por admin) y las automáticas colores neutros (sistema).
    - Acciones Masivas: Tabla con checkboxes para selección múltiple y botón "Asignar Etiquetas".
    - Indicador de frescura: Mostrar tiempo transcurrido desde la última sincronización horaria.
    - Historificacion: Se tiene que poder señalar en que momento se quiere ver el inventario. Habra una opcion Live o un desplegable con la hora y el dia. Como la syn es cada 60 miutos solo saldran las horas 
    - Busqueda: En el dashboard se mostrara un boton de busqueda, que sera, por todos los campos que se muestren.
    - Ordenar: Se podra ordenar por todos los campos que se muestren.
    - Estado: La información que indique si hay agente instaladoo esta dado de alta en EDR, MONICA, ... mostrara un punto rojo en caso de no estarlo y uno verde si lo esta. En el caso del backup mostrará la fecha del ultimo backup.
  k8s_manifests:
    - Helm: Configurar CronJobs (0 * * * *) para las tareas de sincronización periódica.
    - Gestión de Secretos: Inyectar credenciales de vCenter/Veeam/Monica de forma segura.

# Desglose de tareas
tasks:
  - name: "Design OpenAPI: Asset schemas with security compliance and tag support"
    hours: 2
  - name: "Backend: Logic for Automated System Tags (VMware/Networking detection)"
    hours: 3
  - name: "API: Implement Bulk Assignment endpoint for manual tags"
    hours: 2
  - name: "Frontend: Inventory list with bulk actions and color-coded tag badges"
    hours: 4
  - name: "DB Design: Relations for Asset-Tag mapping (N:M) and compliance tracking"
    hours: 3
  - name: "Helm: Configure Hourly CronJobs for external API data ingestion"
    hours: 2
