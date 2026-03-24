# API Spec — Applications, Services & Topology

## CRUD Applications — /v1/applications
- GET /v1/applications?search=&status=&environment=
- GET /v1/applications/{id} — incluye infra_bindings y dependencies
- POST /v1/applications — requiere editor
- PUT /v1/applications/{id} — requiere editor
- DELETE /v1/applications/{id} — requiere admin

## Infra bindings
- POST /v1/applications/{id}/infra-bindings
  ```json
  {"asset_id": "uuid", "binding_tier": "compute",
   "is_critical": true, "is_single_point_of_failure": false,
   "communication_port": 5432,
   "tier_order_override": null, "redundancy_group": null}
  ```

`communication_port`: puerto por el que esta capa se comunica con la siguiente.
Ejemplos por tier: entry_point=443, gateway=443/80, data=5432(Postgres)/1521(Oracle)/3306(MySQL),
cache=6379(Redis), compute=22/443, auth=8080/443, network=22.
- DELETE /v1/applications/{id}/infra-bindings/{binding_id}

## Dependencies
- POST /v1/applications/{id}/dependencies
  ```json
  {"target_app_id": "uuid", "dep_type": "calls_api", "is_critical": true}
  ```
- DELETE /v1/applications/{id}/dependencies/{dep_id}

## CRUD Services — /v1/services
CRUD estándar + endpoints y components anidados.
- POST /v1/services/{id}/endpoints: {url, type, is_primary, certificate_id?}
- POST /v1/services/{id}/components: {application_id, role, order_index}

## GET /v1/services/{id}/dependency-graph
Parámetros: include_assets=true, include_certs=true

Respuesta:
```json
{
  "nodes": [
    {"id":"app-uuid","node_type":"application","label":"MiApp","environment":"production"},
    {"id":"ast-uuid","node_type":"asset","label":"srv-db-01",
     "asset_type":"database","binding_tier":"data","tier_order":5,
     "is_critical":true,"is_single_point_of_failure":false,"ips":["10.0.0.1"]}
  ],
  "edges": [
    {"id":"e-bind-uuid","source":"app-uuid","target":"ast-tier1-uuid",
     "edge_type":"HOSTED_ON","label":"entry_point","is_critical":true},
    {"id":"e-bind-uuid2","source":"ast-tier1-uuid","target":"ast-tier2-uuid",
     "edge_type":"HOSTED_ON","label":"compute","is_critical":true}
  ]
}
```

Lógica de aristas (cascada):
1. Ordenar bindings por tier_order_effective ASC
2. Primera arista: application_node → primer_asset
3. Para i=1..N: arista desde asset[i-1] → asset[i]
