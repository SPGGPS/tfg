id: applications

context: |
  Feature: Gestión de aplicaciones, servicios y mapa de dependencias topológico
  Domain: Capa lógica sobre la infraestructura física del CMDB.
  Motivación: El CMDB conoce los activos físicos pero no qué servicios corren sobre ellos.
  Este módulo responde: "Si cae srv-db-01, ¿qué servicios ciudadanos se ven afectados?"

proposal: |
  Jerarquía de modelos:
    Service (servicio ciudadano con URL pública)
      └── ServiceEndpoint (URLs + certificado TLS)
      └── ServiceComponent → Application (N aplicaciones componen el servicio)
            └── AppInfraBinding (binding al asset de infra con binding_tier y tier_order)
            └── AppDependency (dependencias entre aplicaciones)

  Mapa topológico SVG con layout por filas (tier_order) y aristas en cascada.
  10 capas: entry_point→gateway→certificate→application/auth→cache/data→compute→storage→network

status: Implementado al 100%.
