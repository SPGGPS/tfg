# Design: Applications, Services & Infrastructure Topology

## Context

El CMDB modela activos físicos pero no la capa lógica. Este módulo añade esa capa y la conecta
a la infraestructura mediante un **mapa topológico por capas** que responde:

- *"Si cae srv-db-01, ¿qué servicios ciudadanos se ven afectados?"*
- *"¿Cuál es la ruta completa desde la URL pública hasta el hardware?"*
- *"¿Qué certificados caducan este mes?"*
- *"¿Hay puntos de fallo único en servicios críticos?"*

Stack: FastAPI + React + PostgreSQL. Visualización: SVG con carriles horizontales (layered view).

---

## Modelo de capas (Opción C — Híbrido canónico + override)

Cada asset vinculado a una aplicación tiene un `binding_tier` que determina su capa:

```
tier_order  binding_tier    Descripción              Assets típicos
──────────  ────────────    ───────────────          ──────────────
    1       entry_point     Punto de entrada público  URLs, CDN, DNS
    2       gateway         Proxy, LB, ingress        Traefik, Nginx, F5
    3       certificate     Certificados TLS/SSL      Cert-manager, FNMT, LE
    4       application     Apps, frontends, backends VMs con software
    4       auth            IdP, SSO                  Keycloak, LDAP
    5       cache           Caché en memoria          Redis, Memcached
    5       data            BBDDs, brokers, storage   PostgreSQL, Kafka, MinIO
    6       compute         Servidores físicos/virt.  server_physical/virtual
    7       storage         SANs, NAS, backups        NAS, SAN, Veeam target
    8       network         Red — switching/routing   switch, router, AP, FW
```

Los tiers 4+4, 5+5 son deliberadamente iguales — auth y application son el mismo nivel lógico,
igual que cache y data.

---

## Modelo conceptual — capas completas

```
TIER 0 — Servicio
  Service (ej: "Sede Electrónica")  criticality: critical
  ServiceEndpoint: https://sede.ssreyes.es
        │  COMPOSED_OF
        ▼
TIER 2 — Gateway
  [Traefik ingress]   ← binding_tier=gateway, is_spf=true
        │
        ▼
TIER 3 — Certificados TLS
  [sede.ssreyes.es ⚠ 12 días]  ← binding_tier=certificate, Certificate entity
        │
        ▼
TIER 4 — Aplicaciones / Auth
  [sede-frontend]  [sede-api]  [Keycloak]  ← Applications
        │                │
        ▼                ▼
TIER 5 — Datos / Caché
  [postgres-ha ⚠SPF]  [Redis]  ← binding_tier=data/cache
        │
        ▼
TIER 6 — Cómputo
  [srv-web-01]  [srv-app-01]  [srv-db-01 🔄pg-cluster]  ← binding_tier=compute
        │
        ▼
TIER 8 — Red
  [core-switch-01]  [router-edge-01 ⚠SPF]  ← binding_tier=network
```

---

## Entidad Certificate — por qué es de primera clase y campos completos

Los certificados TLS son activos críticos de infraestructura con ciclo de vida propio:
- Tienen fecha de caducidad — generan alertas automáticas
- Pueden ser punto de fallo único (si caduca, el servicio deja de funcionar)
- Están directamente vinculados a los endpoints públicos de los servicios
- Contienen información de la entidad certificadora (FNMT, Let's Encrypt, CA interna…)
- Sus datos técnicos completos se rellenan automáticamente mediante Apache Flow

**Campos del modelo Certificate organizados por grupo:**

| Grupo | Campos | Origen |
|-------|--------|--------|
| Identificación | common_name, san_domains, serial_number, fingerprint_sha256/sha1 | Manual o Apache Flow |
| Vigencia | issued_at, expires_at, not_before | Manual o Apache Flow |
| Entidad Certificadora | issuer, issuer_common_name, issuer_organization, issuer_country, ca_type | Apache Flow preferido |
| Sujeto | subject_organization, subject_ou, subject_country, subject_state, subject_locality | Apache Flow preferido |
| Criptografía | key_type, signature_algorithm, wildcard, key_usages, extended_key_usages | Apache Flow preferido |
| Extensiones X.509 | ocsp_url, crl_url, ca_issuers_url, is_ca, chain_valid | Apache Flow |
| Gestión | auto_renew, managed_by, acme_account, environment, notes | Manual |
| Metadatos ingesta | source, last_verified_at | Apache Flow |

**Flujo de datos previsto:**
1. El admin crea el certificado manualmente con los campos mínimos: `common_name` + `expires_at` + `environment`
2. Apache Flow (proceso futuro) lee el certificado real del servidor/HSM y rellena todos los campos técnicos
3. El campo `last_verified_at` indica cuándo Apache Flow actualizó los datos por última vez
4. Los campos rellenados por Apache Flow se muestran en modo solo lectura en la UI con el badge "Apache Flow"

**Vinculación con ServiceEndpoint:**
El campo `certificate_id` en `ServiceEndpoint` es la relación principal entre certificados y servicios. Si es null → el endpoint funciona sin TLS. El `tls_status` calculado se propaga al grafo de dependencias y al mapa de topología.



---

## Análisis de impacto (Impact Analysis)

El endpoint `/v1/assets/{id}/impact` recorre el grafo hacia arriba:

```
asset → [AppInfraBinding] → Application → [ServiceComponent] → Service
```

Responde: dado que falla este asset, ¿qué aplicaciones y servicios se ven afectados?

El análisis tiene en cuenta:
- `is_critical=true` → el fallo del asset afecta a la aplicación
- `is_single_point_of_failure=true` → sin redundancia
- `redundancy_group` → si el grupo tiene otros assets activos, el impacto puede ser absorbido

---

## Single Point of Failure (SPF)

Un asset es SPF cuando:
1. `is_single_point_of_failure=true` en su binding
2. No tiene otros assets activos en el mismo `redundancy_group`

El mapa de topología resalta los SPFs con borde naranja pulsante.
El análisis de impacto prioriza los SPFs como los puntos de mayor riesgo.

---

## Mapa de caídas — flujo visual

```
┌──────────────────────────────────────────────────────────────┐
│ TIER 1 — Punto de entrada                                    │
│   [https://sede.ssreyes.es]                                  │
├──────────────────────────────────────────────────────────────┤
│ TIER 2 — Gateway                                             │
│   [Traefik ⚠SPF]                                            │
├──────────────────────────────────────────────────────────────┤
│ TIER 3 — Certificados TLS         ← CARRIL ÁMBAR             │
│   [sede.ssreyes.es 🔒 válido]                               │
├──────────────────────────────────────────────────────────────┤
│ TIER 4 — Aplicación / Auth                                   │
│   [sede-frontend]  [sede-api]  [Keycloak]                   │
├──────────────────────────────────────────────────────────────┤
│ TIER 5 — Datos / Caché                                       │
│   [postgres-ha ⚠SPF]  [Redis 🔄cache-cluster]              │
├──────────────────────────────────────────────────────────────┤
│ TIER 6 — Cómputo                                             │
│   [srv-web-01 🔄web-lb]  [srv-app-01 🔄web-lb]  [srv-db-01]│
├──────────────────────────────────────────────────────────────┤
│ TIER 8 — Red                                                 │
│   [core-switch-01]  [router-edge-01 ⚠SPF]                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Decisions

| Decisión | Rationale |
|----------|-----------|
| BindingTier enum + tier_order_override | Consistencia automática + flexibilidad para casos especiales |
| Certificate como entidad independiente | Ciclo de vida diferente a los assets. Dashboard de caducidad propio. |
| asset XOR certificate en AppInfraBinding | Un binding es o de asset o de certificado, nunca ambos. CheckConstraint en DB. |
| redundancy_group como string libre | Permite agrupar assets de cualquier tipo sin FK explícita. Más flexible. |
| is_single_point_of_failure como campo explícito | No calculado — lo decide el admin que conoce la arquitectura real. |
| Vista de capas como default del mapa | Más legible que un grafo libre. Refleja mejor el modelo mental de un sysadmin. |
| Impact analysis en el backend | El grafo transitivo es complejo de calcular en frontend. Mejor como endpoint. |

---

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| SPF marcado incorrectamente | Campo informativo, no bloquea nada. Admin es responsable. |
| Certs importados manualmente desactualizados | Campo `updated_at` + advertencia si no se actualiza en >90 días |
| Mapa muy complejo para servicios grandes | Toggle "Solo SPFs" para vista simplificada de ruta crítica |
| Carril de certificados confuso si hay muchos | Paginación dentro del carril, tooltip con detalles al hover |
