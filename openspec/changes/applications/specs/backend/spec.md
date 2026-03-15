# Backend - Applications, Services & Infrastructure Topology

## ADDED Requirements

---

### Requirement: Enum BindingTier con tier_order canónico

El backend SHALL definir el enum `BindingTier` y un diccionario `TIER_ORDER` que mapea cada valor a su orden por defecto:

```python
class BindingTier(str, enum.Enum):
    entry_point  = "entry_point"   # order=1
    gateway      = "gateway"       # order=2
    certificate  = "certificate"   # order=3
    application  = "application"   # order=4
    auth         = "auth"          # order=4
    cache        = "cache"         # order=5
    data         = "data"          # order=5
    compute      = "compute"       # order=6
    storage      = "storage"       # order=7
    network      = "network"       # order=8

TIER_ORDER = {
    "entry_point": 1, "gateway": 2, "certificate": 3,
    "application": 4, "auth": 4,
    "cache": 5, "data": 5,
    "compute": 6, "storage": 7, "network": 8,
}

TIER_LABELS = {
    "entry_point": "Punto de entrada",
    "gateway":     "Gateway / Proxy",
    "certificate": "Certificados TLS",
    "application": "Aplicación / Auth",
    "auth":        "Aplicación / Auth",
    "cache":       "Datos / Caché",
    "data":        "Datos / Caché",
    "compute":     "Cómputo",
    "storage":     "Almacenamiento",
    "network":     "Red",
}
```

La función `effective_tier_order(binding)` devuelve `binding.tier_order_override` si no es null, o `TIER_ORDER[binding.binding_tier]` si es null.

---

### Requirement: Modelo Certificate

El backend SHALL implementar el modelo `Certificate` en `app/models/certificate.py` con todos los campos definidos en el spec de API:

```python
class KeyType(str, enum.Enum):
    rsa_2048  = "rsa_2048"
    rsa_4096  = "rsa_4096"
    ecdsa_256 = "ecdsa_256"
    ecdsa_384 = "ecdsa_384"
    ed25519   = "ed25519"
    other     = "other"

class CAType(str, enum.Enum):
    public_trusted = "public_trusted"   # Let's Encrypt, DigiCert, Sectigo...
    fnmt           = "fnmt"             # FNMT española
    internal_ca    = "internal_ca"      # CA interna del Ayuntamiento
    self_signed    = "self_signed"      # autofirmado
    unknown        = "unknown"

class Certificate(Base):
    __tablename__ = "certificates"

    # Identificación
    id                  = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    common_name         = Column(String(255), nullable=False)
    san_domains         = Column(JSON, default=list)
    serial_number       = Column(String(100), nullable=True)
    fingerprint_sha256  = Column(String(100), nullable=True, index=True)  # identifica unívocamente
    fingerprint_sha1    = Column(String(60), nullable=True)

    # Vigencia
    issued_at           = Column(Date, nullable=True)
    expires_at          = Column(Date, nullable=False, index=True)  # campo crítico
    not_before          = Column(Date, nullable=True)

    # Entidad Certificadora
    issuer              = Column(String(255), nullable=True)        # DN completo del emisor
    issuer_common_name  = Column(String(255), nullable=True)        # CN del emisor
    issuer_organization = Column(String(255), nullable=True)        # O del emisor
    issuer_country      = Column(String(2), nullable=True)          # C del emisor
    ca_type             = Column(Enum(CAType), default=CAType.unknown)

    # Sujeto
    subject_organization      = Column(String(255), nullable=True)
    subject_organizational_unit = Column(String(255), nullable=True)
    subject_country           = Column(String(2), nullable=True)
    subject_state             = Column(String(100), nullable=True)
    subject_locality          = Column(String(100), nullable=True)

    # Criptografía y extensiones
    key_type            = Column(Enum(KeyType), default=KeyType.rsa_2048)
    signature_algorithm = Column(String(100), nullable=True)
    wildcard            = Column(Boolean, default=False)
    key_usages          = Column(JSON, nullable=True)           # ["digitalSignature", ...]
    extended_key_usages = Column(JSON, nullable=True)           # ["serverAuth", ...]
    ocsp_url            = Column(String(500), nullable=True)
    crl_url             = Column(String(500), nullable=True)
    ca_issuers_url      = Column(String(500), nullable=True)
    is_ca               = Column(Boolean, default=False)
    chain_valid         = Column(Boolean, nullable=True)        # null = no verificado aún

    # Gestión
    auto_renew          = Column(Boolean, default=False)
    managed_by          = Column(String(100), nullable=True)
    acme_account        = Column(String(255), nullable=True)
    environment         = Column(Enum(AppEnvironment), default=AppEnvironment.production)
    notes               = Column(Text, nullable=True)

    # Metadatos de ingesta (para Apache Flow)
    source              = Column(String(100), nullable=True)    # "apache-flow", "manual", etc.
    last_verified_at    = Column(DateTime(timezone=True), nullable=True)

    created_at          = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at          = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                                 onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    service_endpoints   = relationship("ServiceEndpoint", back_populates="certificate",
                                       foreign_keys="ServiceEndpoint.certificate_id")
    infra_bindings      = relationship("AppInfraBinding", back_populates="certificate",
                                       foreign_keys="AppInfraBinding.certificate_id")
```

**Propiedades calculadas:**
```python
@property
def cert_status(self) -> str:
    if not self.expires_at: return "unknown"
    delta = (self.expires_at - date.today()).days
    if delta < 0:    return "expired"
    if delta <= 7:   return "critical"
    if delta <= 30:  return "expiring"
    return "valid"

@property
def days_remaining(self) -> int | None:
    if not self.expires_at: return None
    return (self.expires_at - date.today()).days
```

**`to_dict()` incluye todos los campos + `cert_status` + `days_remaining`.**

**Modelo ServiceEndpoint actualizado** — añadir campo `certificate_id`:
```python
class ServiceEndpoint(Base):
    # ... campos existentes ...
    certificate_id = Column(String, ForeignKey("certificates.id", ondelete="SET NULL"), nullable=True)
    certificate    = relationship("Certificate", back_populates="service_endpoints",
                                  foreign_keys=[certificate_id])
```

**`tls_status` calculado en `to_dict()` de ServiceEndpoint:**
```python
def to_dict(self):
    cert = self.certificate
    if cert is None:
        tls_status = "none"
    else:
        tls_status = cert.cert_status
    return {
        ...,
        "certificate_id": self.certificate_id,
        "certificate": cert.to_dict() if cert else None,
        "tls_status": tls_status,
    }
```

**Índices adicionales:**
- INDEX en `fingerprint_sha256` — para deduplicación al ingestar desde Apache Flow
- INDEX en `ca_type` — para filtrar por tipo de CA
- INDEX en `expires_at` — ya existía, mantener

**Validación al eliminar Certificate:**
Antes de hacer DELETE, el router SHALL verificar que no existen `ServiceEndpoint` con `certificate_id = id` activos → si existen, devolver 409 con lista de servicios afectados.

#### Scenario: Deduplicación por fingerprint en ingesta Apache Flow
- **GIVEN** Apache Flow envía un certificado con fingerprint_sha256 ya existente en la BD
- **WHEN** el proceso de ingesta procesa el payload
- **THEN** el backend actualiza el registro existente en lugar de crear uno duplicado (upsert por fingerprint)

#### Scenario: ServiceEndpoint devuelve tls_status en respuesta
- **GIVEN** un endpoint con certificate_id apuntando a un cert expirado
- **WHEN** GET /v1/services/{id}
- **THEN** el endpoint en la respuesta incluye tls_status="expired" y el objeto certificate completo

**Propiedad calculada `cert_status`:**
```python
@property
def cert_status(self) -> str:
    if not self.expires_at: return "unknown"
    today = date.today()
    delta = (self.expires_at - today).days
    if delta < 0:    return "expired"
    if delta <= 7:   return "critical"
    if delta <= 30:  return "expiring"
    return "valid"

@property
def days_remaining(self) -> int:
    if not self.expires_at: return None
    return (self.expires_at - date.today()).days
```

**`to_dict()` incluye:** todos los campos + `status` (cert_status) + `days_remaining`.

**Índices:**
- INDEX en `expires_at` — para filtros de caducidad eficientes
- INDEX en `environment`

---

### Requirement: Modelo AppInfraBinding extendido con tier

El modelo `AppInfraBinding` SHALL actualizarse con los nuevos campos de tier:

```python
class AppInfraBinding(Base):
    __tablename__ = "app_infra_bindings"
    id                  = Column(String, PK)
    application_id      = Column(String, FK("applications.id", CASCADE))
    asset_id            = Column(String, FK("assets.id", SET NULL), nullable=True)
    certificate_id      = Column(String, FK("certificates.id", SET NULL), nullable=True)
    binding_tier        = Column(Enum(BindingTier), nullable=False)
    tier_order_override = Column(Integer, nullable=True)
    is_critical         = Column(Boolean, default=True)
    is_single_point_of_failure = Column(Boolean, default=False)
    redundancy_group    = Column(String(100), nullable=True, index=True)
    notes               = Column(String(300), nullable=True)
    # CHECK: debe tener asset_id XOR certificate_id (no ambos null, no ambos rellenos)
    __table_args__ = (
        CheckConstraint(
            "(asset_id IS NOT NULL AND certificate_id IS NULL) OR "
            "(asset_id IS NULL AND certificate_id IS NOT NULL)",
            name="ck_binding_asset_xor_certificate"
        ),
    )
```

**Propiedad calculada `tier_order_effective`:**
```python
@property
def tier_order_effective(self) -> int:
    if self.tier_order_override is not None:
        return self.tier_order_override
    return TIER_ORDER.get(str(self.binding_tier), 99)
```

**`to_dict()` incluye:** todos los campos + `tier_order_effective` + campos del asset/certificado asociado.

#### Scenario: Constraint asset XOR certificate
- **GIVEN** un intento de crear binding con asset_id y certificate_id ambos rellenos
- **WHEN** se intenta insertar en la DB
- **THEN** CheckConstraint lanza error → el router devuelve 422

---

### Requirement: Router /v1/certificates — CRUD completo

El backend SHALL implementar el router en `app/routers/certificates.py` con:

- `GET /v1/certificates` — paginado, filtros: `status`, `environment`, `search`, `expiring_days`
  - `expiring_days`: filtra `expires_at <= date.today() + timedelta(days=expiring_days)`
  - Ordenado por `expires_at ASC` por defecto
- `GET /v1/certificates/{id}` — detalle con bindings
- `POST /v1/certificates` — crear
- `PUT /v1/certificates/{id}` — actualizar
- `DELETE /v1/certificates/{id}` — eliminar (solo si no tiene bindings activos → 409)
- `GET /v1/certificates/expiry-summary` — resumen de estados

**Implementación de expiry-summary:**
```python
@router.get("/v1/certificates/expiry-summary")
def expiry_summary(db: Session = Depends(get_db), user = Depends(require_viewer)):
    today = date.today()
    certs = db.query(Certificate).all()
    result = {"total": len(certs), "valid": 0, "expiring_soon": 0, "critical": 0, "expired": 0, "next_expiry": None}
    soonest = None
    for c in certs:
        s = c.cert_status
        if s == "valid":     result["valid"] += 1
        elif s == "expiring": result["expiring_soon"] += 1
        elif s == "critical": result["critical"] += 1
        elif s == "expired":  result["expired"] += 1
        if c.expires_at and c.expires_at > today:
            if soonest is None or c.expires_at < soonest.expires_at:
                soonest = c
    if soonest:
        result["next_expiry"] = {"id": soonest.id, "common_name": soonest.common_name,
                                  "expires_at": soonest.expires_at.isoformat(), "days_remaining": soonest.days_remaining}
    return result
```

---

### Requirement: Router /v1/applications/{id}/infra-bindings — actualizado

El router SHALL actualizarse para aceptar el body extendido con `binding_tier`, `tier_order_override`, `is_critical`, `is_single_point_of_failure`, `redundancy_group`, y opcionalmente `certificate_id`.

**Validaciones adicionales en POST:**
1. Si `binding_tier == "certificate"`: `certificate_id` es obligatorio, `asset_id` debe ser null.
2. Si `binding_tier != "certificate"`: `asset_id` es obligatorio, `certificate_id` debe ser null.
3. Verificar que el `certificate_id` o `asset_id` existen en la BD → 404 si no.
4. No se permite duplicar `(application_id, asset_id, binding_tier)` ni `(application_id, certificate_id)` → 409.

---

### Requirement: Construcción del grafo con tiers — _build_graph actualizado

La función `_build_graph` SHALL actualizarse para incluir:

1. **Nodos de certificado:** cuando `include_certificates=True`, añadir nodos de tipo `certificate` con sus campos de estado.

2. **Campo tier en nodos de asset:**
```python
# Para cada binding de infra:
node = {
    "id": f"ast-{asset.id}",
    "node_type": "asset",
    "label": asset.name,
    "asset_type": str(asset.type),
    "ips": asset.ips or [],
    "binding_tier": str(binding.binding_tier),
    "tier_order": binding.tier_order_effective,
    "is_critical": binding.is_critical,
    "is_single_point_of_failure": binding.is_single_point_of_failure,
    "redundancy_group": binding.redundancy_group,
    "compliance_ok": asset.edr_installed and asset.monitored,  # simplificado
}
```

3. **Campo `tiers`** en la respuesta raíz: lista de capas presentes en este grafo (no todas las capas, solo las que tienen nodos), ordenadas por `tier_order`.

4. **Campo `spf_nodes`:** lista de IDs de nodos con `is_single_point_of_failure=True`.

5. **Campo `expiring_certificates`:** lista de IDs de nodos de certificado con status `expiring` o `critical` o `expired`.

6. **Arista `SECURED_BY`:** para cada binding de tipo certificate.

**Algoritmo para construir `tiers` dinámicamente:**
```python
tiers_present = {}
for node in nodes.values():
    order = node.get("tier_order")
    tier  = node.get("binding_tier")
    if order and tier and order not in tiers_present:
        tiers_present[order] = {
            "tier_order": order,
            "binding_tier": tier,
            "label": TIER_LABELS.get(tier, tier),
        }
# Añadir siempre tier de servicios (order=0) y aplicaciones (order=4)
response["tiers"] = sorted(tiers_present.values(), key=lambda x: x["tier_order"])
```

---

### Requirement: Análisis de impacto — endpoint /v1/assets/{id}/impact

`GET /v1/assets/{id}/impact` — dado un asset, devuelve qué aplicaciones y servicios se verían afectados si ese asset fallara.

```python
@router.get("/v1/assets/{asset_id}/impact")
def asset_impact(asset_id: str, db: Session = Depends(get_db), user = Depends(require_viewer)):
    # 1. Encontrar todos los bindings que referencian este asset
    bindings = db.query(AppInfraBinding).filter_by(asset_id=asset_id).all()
    affected_apps = {}
    for b in bindings:
        app = b.application
        if not app: continue
        affected_apps[app.id] = {
            "id": app.id, "name": app.name, "status": str(app.status),
            "binding_tier": str(b.binding_tier),
            "is_critical": b.is_critical,
            "is_spf": b.is_single_point_of_failure,
        }
    # 2. Para cada app afectada, encontrar los servicios que la usan
    affected_services = {}
    for app_id in affected_apps:
        components = db.query(ServiceComponent).filter_by(application_id=app_id).all()
        for sc in components:
            svc = sc.service
            if not svc: continue
            affected_services[svc.id] = {
                "id": svc.id, "name": svc.name,
                "criticality": str(svc.criticality), "status": str(svc.status),
            }
    return {
        "asset_id": asset_id,
        "affected_applications": list(affected_apps.values()),
        "affected_services": list(affected_services.values()),
        "total_affected_apps": len(affected_apps),
        "total_affected_services": len(affected_services),
        "has_critical_impact": any(s["criticality"] == "critical" for s in affected_services.values()),
    }
```

#### Scenario: Impacto de caída de router-edge-01
- **GIVEN** router-edge-01 vinculado como `network/spf=true` a "sede-api" que es parte de "Sede Electrónica"
- **WHEN** GET /v1/assets/router-edge-01/impact
- **THEN** affected_applications=[sede-api], affected_services=[Sede Electrónica], has_critical_impact=true

---

### Requirement: Modelo __init__.py — registrar Certificate

`app/models/__init__.py` SHALL importar y exportar `Certificate`, `BindingTier`, `TIER_ORDER`, `TIER_LABELS`.

`app/main.py` SHALL incluir el router de certificados:
```python
from app.routers.certificates import router as certificates_router
app.include_router(certificates_router)
```
---

### Requirement: Modelo Pydantic BindingCreate — campos obligatorios actualizados

El modelo Pydantic `BindingCreate` usado en `POST /v1/applications/{id}/infra-bindings` SHALL definir los campos del spec de API. **Nunca usar `binding_type` (enum antiguo) — usar `binding_tier` (BindingTier).**

```python
class BindingCreate(BaseModel):
    asset_id: str
    binding_tier: BindingTier = BindingTier.compute
    tier_order_override: Optional[int] = None
    is_critical: bool = True
    is_single_point_of_failure: bool = False
    redundancy_group: Optional[str] = None
    notes: Optional[str] = None
```

Si el modelo Pydantic no coincide con lo que envía el frontend, FastAPI devuelve un error 422 con `detail` como array de objetos — que el frontend mostrará como `[object Object]` si no lo maneja correctamente.

#### Scenario: Campo incorrecto en BindingCreate causa 422
- **GIVEN** el modelo tiene `binding_type` en lugar de `binding_tier`
- **WHEN** el frontend envía `{binding_tier: "compute", asset_id: "uuid"}`
- **THEN** FastAPI devuelve 422 `{"detail": [{"loc": ["body","binding_tier"], "msg": "field required"}]}`
- **THEN** el frontend muestra el error legible "binding_tier: field required" (NO "[object Object]")

---

### Requirement: Formato de errores FastAPI — detail puede ser array

Cuando FastAPI devuelve errores de validación Pydantic (422 Unprocessable Entity), el campo `detail` es un **array de objetos**, no un string:

```json
{
  "detail": [
    {"loc": ["body", "binding_tier"], "msg": "field required", "type": "value_error.missing"}
  ]
}
```

El frontend SHALL manejar ambos formatos en la función `req()` de `api.js`:

```javascript
const raw = err.detail
let msg
if (!raw)                  msg = `HTTP ${res.status}`
else if (typeof raw === 'string') msg = raw
else if (Array.isArray(raw))      msg = raw.map(e => `${e.loc?.slice(-1)[0]}: ${e.msg}`).join(', ')
else                       msg = JSON.stringify(raw)
throw Object.assign(new Error(msg), { status: res.status, data: err })
```

Esta lógica SHALL aplicarse en el fichero `services/api.js` de forma centralizada, cubriendo todos los endpoints.

#### Scenario: Error de validación muestra mensaje legible
- **GIVEN** el backend devuelve 422 con detail=[{loc:["body","binding_tier"], msg:"field required"}]
- **WHEN** el frontend captura el error
- **THEN** el toast muestra "binding_tier: field required" y NO "[object Object]"
---

### Requirement: _build_graph — usar binding_tier y resolver nombre del asset

La función `_build_graph` SHALL usar `binding_tier` (no `binding_type`) y SHALL resolver el nombre real del asset desde la BD para cada nodo de infraestructura.

```python
def _build_graph(services, include_assets=True, db=None):
    # ...
    if include_assets:
        for b in app.infra_bindings:
            if not b.asset_id: continue
            astid = f"ast-{b.asset_id}"
            if astid not in nodes:
                tier_key = str(b.binding_tier).split(".")[-1] if b.binding_tier else "compute"
                # Resolver nombre real del asset — NUNCA usar b.asset_id como label
                ast_name, ast_type, ast_ips = b.asset_id, "unknown", []
                if db:
                    ast = db.query(Asset).filter_by(id=b.asset_id).first()
                    if ast:
                        ast_name = ast.name
                        ast_type = str(ast.type).split(".")[-1]
                        ast_ips  = ast.ips or []
                nodes[astid] = {"id":astid, "node_type":"asset", "label":ast_name,
                                "asset_type":ast_type, "ips":ast_ips,
                                "binding_tier":tier_key, "tier_order":b.tier_order_effective,
                                "is_critical":b.is_critical,
                                "is_single_point_of_failure":b.is_single_point_of_failure}
            edges.append({"source":aid, "target":astid, "edge_type":"HOSTED_ON",
                          "label":tier_key, "is_critical":b.is_critical})
```

La función recibe `db` como parámetro opcional y los endpoints que la llaman le pasan el objeto `Session`.

#### Scenario: Grafo muestra nombre del asset, no su UUID
- **GIVEN** la aplicación "flexia" tiene un binding a "web-prod-01" (tier: compute)
- **WHEN** GET /v1/services/{id}/dependency-graph
- **THEN** el nodo del asset tiene label="web-prod-01" y asset_type="server_physical", NO label="uuid-xxx"

#### Scenario: Grafo vacío cuando no hay componentes de servicio
- **GIVEN** un servicio existe pero no tiene componentes (Service components = [])
- **WHEN** GET /v1/services/{id}/dependency-graph
- **THEN** el grafo devuelve solo el nodo del servicio y edges=[] — no crashea
