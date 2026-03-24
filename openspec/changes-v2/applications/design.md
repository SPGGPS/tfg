# Design: Applications, Services & Infrastructure Topology

## Modelo de capas (BindingTier)

| Valor | tier_order | Descripción | Ejemplos |
|-------|-----------|-------------|---------|
| entry_point | 1 | URL pública, dominio | DNS, CDN |
| gateway | 2 | Proxy, load balancer | Traefik, Nginx, F5 |
| certificate | 3 | Terminación TLS | cert-manager |
| application | 4 | Servidor de aplicación | Tomcat, Node |
| auth | 4 | Autenticación | Keycloak |
| cache | 5 | Caché | Redis, Memcached |
| data | 5 | Base de datos | PostgreSQL, Oracle |
| compute | 6 | Cómputo / VM | vSphere |
| storage | 7 | Almacenamiento | NAS, SAN |
| network | 8 | Red | Switch core |

## Grafo en cascada
Las aristas conectan capas secuencialmente, no todas desde la aplicación:
```
App → Tier1(entry_point) → Tier2(gateway) → Tier3(compute) → Tier4(data)
```
Implementado en _build_graph(): ordenar bindings por tier_order_effective,
primera arista desde app, siguientes desde asset anterior.

## Decisiones

| Decisión | Rationale |
|----------|-----------|
| tier_order_override | Permite personalizar el orden de un binding específico |
| is_single_point_of_failure | Marca visual en el nodo del mapa |
| Cascada en aristas | Refleja dependencias reales: cada capa depende de la anterior |
| SVG con carriles horizontales | Legible, sin librería externa de grafos |
