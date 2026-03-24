id: certificates

context: |
  Feature: Inventario y seguimiento de certificados TLS/SSL
  Integrado como tab en la página de inventario

proposal: |
  1. Modelo Certificate con estado calculado: valid/expiring/critical/expired
  2. Tab "Certificados 🔒" en InventoryPage (ruta /certificates)
  3. Endpoint /expiry-summary para el panel de resumen
  4. Vinculación con ServiceEndpoint (certificate_id FK)

status: Implementado al 100%.
