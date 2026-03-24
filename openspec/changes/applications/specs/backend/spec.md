# Backend Spec — Applications

## Serialización de enums en to_dict()
Todos los enums de Application, Service, etc. deben serializarse como string plano:
```python
"environment": str(self.environment).split(".")[-1] if self.environment else None
"binding_tier": str(self.binding_tier).split(".")[-1] if self.binding_tier else None
```

## _build_graph() en routers/applications.py — aristas en cascada
```python
# Ordenar bindings por tier efectivo
app_bindings = sorted(app.infra_bindings, key=lambda b: b.tier_order_effective)
sorted_ids = [f"ast-{b.asset_id}" for b in app_bindings if b.asset_id]

if sorted_ids:
    # Primera arista: app → tier1
    edges.append({"source": aid, "target": sorted_ids[0], ...})
    # Aristas siguientes: tier_n → tier_n+1
    for i in range(1, len(sorted_ids)):
        edges.append({"source": sorted_ids[i-1], "target": sorted_ids[i], ...})
```

## ServiceEndpoint.tls_status
Propiedad calculada — no columna:
```python
@property
def tls_status(self):
    if not self.certificate_id: return "none"
    from sqlalchemy.orm import object_session
    sess = object_session(self)
    cert = sess.query(Certificate).filter_by(id=self.certificate_id).first()
    return cert.cert_status if cert else "none"
```

## communication_port en nodos y aristas del grafo

El nodo del asset incluye `communication_port` en su representación:
```python
nodes[astid] = {
    ...,
    "communication_port": b.communication_port,  # puede ser null
    ...
}
```

Las aristas incluyen `port`:
```python
edges.append({
    "id": f"e-bind-{b.id}",
    "source": ..., "target": ...,
    "edge_type": "HOSTED_ON",
    "label": tier_key,
    "port": b.communication_port,  # null si no está definido
    "is_critical": b.is_critical
})
```

En el frontend, la etiqueta de la arista muestra: `"compute :5432"` si hay puerto definido.
En el tooltip del nodo: línea `"Puerto: 5432"` si communication_port está definido.

---

## Mapa de dependencias — fixes v1.0

### Enum labels en aristas
```python
# ❌ ANTES: str(comp.role) → "ComponentRole.backend"
# ✅ DESPUÉS:
"label": str(comp.role).split(".")[-1]       # → "backend"
"label": str(dep.dep_type).split(".")[-1]    # → "calls_api"
"label": tier_key.replace("_", " ")          # → "hosted on"
"criticality": str(svc.criticality).split(".")[-1]  # → "critical"
```

### location_name en nodos del grafo
Todos los nodos (service, application, asset) incluyen `location_name`:
```python
# Application/Dependency node:
cell_info = cell.to_dict().get("full_path", "") or cell.name if cell else ""
nodes[aid] = {..., "location_name": cell_info}

# Asset node:
ast_location = ast_cell.to_dict().get("full_path","") or ast_cell.name if ast_cell else ""
nodes[astid] = {..., "location_name": ast_location}
```

### Aislamiento por servicio
El endpoint `GET /v1/services/{svc_id}/dependency-graph` devuelve SOLO
los nodos y aristas del servicio seleccionado. El frontend NO debe usar
`placeholderData: (prev) => prev` para el grafo — causaría mostrar
el grafo anterior mientras carga el nuevo.
