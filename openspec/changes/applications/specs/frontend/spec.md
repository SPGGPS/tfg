> **Nota:** el título de esta página es "Gestión de Servicios" y el orden de tabs es: Servicios | Aplicaciones | Mapa de Dependencias. Ver change `locations` para el spec completo del renombrado y tooltip.

# Frontend - Applications, Services & Infrastructure Topology

## ADDED Requirements

---

### Requirement: Entrada "Aplicaciones" en el sidebar
Sin cambios respecto al spec anterior. Visible para viewer+, posicionada entre Inventario y Etiquetas.

---

### Requirement: Página /applications con cuatro tabs
La ruta `/applications` SHALL mostrar cuatro pestañas:

| Tab | Ruta | Descripción |
|-----|------|-------------|
| Aplicaciones | `/applications` | Tabla CRUD de aplicaciones |
| Servicios | `/applications/services` | Tabla CRUD de servicios con componentes |
| Certificados | `/applications/certificates` | Gestión y estado de certificados TLS |
| Mapa de Topología | `/applications/map` | Grafo interactivo por capas |

---

### Requirement: Tab "Aplicaciones" — tabla con botón explícito de infraestructura

La tabla de aplicaciones SHALL mostrar en cada fila un botón **"🏗 Infraestructura"** en la columna de acciones. Este botón es el punto de entrada para gestionar los assets vinculados a la aplicación.

**Comportamiento del botón:**
- Si el panel de infra está cerrado → abre el panel debajo de la tabla
- Si el panel ya está abierto para esa app → lo cierra (toggle)
- Cuando el panel está abierto, el botón muestra un borde azul sutil y el texto en azul para indicar el estado activo
- La fila tiene `border-left: 2px solid blue` cuando su panel está abierto

**Columnas de la tabla:**
| Columna | Descripción |
|---------|-------------|
| Nombre | Nombre + versión |
| Entorno | Badge (Producción/Staging/Desarrollo/DR) |
| Estado | Badge (Activa/Mantenimiento/Deprecada/Inactiva) |
| Stack | Chips de tech_stack (máx 3 visibles) |
| Equipo | owner_team |
| Acciones | 🏗 Infraestructura + Editar + Eliminar (editor+) |

**No usar click en fila como trigger de infra** — el click en fila puede interferir con los botones. El trigger SHALL ser el botón explícito "🏗 Infraestructura".

#### Scenario: Abrir panel de infraestructura
- **GIVEN** una aplicación "sede-api" en la tabla
- **WHEN** el usuario pulsa "🏗 Infraestructura"
- **THEN** aparece el panel InfraBindingsSection debajo de la tabla con los assets vinculados y el botón "Asociar infraestructura"

#### Scenario: Botón Editar no abre el panel de infra
- **GIVEN** el panel de infra está cerrado
- **WHEN** el usuario pulsa "Editar" en una fila
- **THEN** se abre el modal de edición de la aplicación, el panel de infra permanece cerrado

#### Scenario: Toggle del panel
- **GIVEN** el panel de infra está abierto para "sede-api"
- **WHEN** el usuario vuelve a pulsar "🏗 Infraestructura" en la misma fila
- **THEN** el panel se cierra, con el ajuste de que el formulario de creación/edición incluye un selector de certificados asociados (multi-select de `certificate_ids`).

---

### Requirement: Tab "Certificados" — gestión completa de certificados TLS

**Cabecera con resumen de estado:**
Encima de la tabla, un banner con los contadores del endpoint `/v1/certificates/expiry-summary`:
```
[18 válidos]  [4 próximos a caducar ⚠]  [1 crítico 🔴]  [1 expirado ❌]
```
Cada contador es clickable y filtra la tabla por ese estado.

**Tabla de certificados:**
Columnas: Common Name, SANs, Emisor, Estado, Días restantes, Caducidad, Entorno, Renovación auto, Acciones.

**Badges de estado:**
| Estado | Color | Icono |
|--------|-------|-------|
| `valid` | Verde `bg-green-900/60 text-green-300` | ✓ Válido |
| `expiring` | Naranja `bg-orange-900/60 text-orange-300` | ⚠ Caduca pronto |
| `critical` | Rojo pulsante `bg-red-900 text-red-200` + `animate-pulse` | 🔴 Crítico |
| `expired` | Rojo oscuro `bg-red-950 text-red-400 line-through` | ❌ Expirado |

**Columna "Días restantes":**
- > 30 días → número en verde
- 8–30 días → número en naranja con `⚠`
- 1–7 días → número en rojo pulsante con `🔴`
- ≤ 0 días → número negativo en rojo con `❌ Expirado hace N días`

**Formulario de creación/edición** (modal):
- `common_name` — obligatorio, placeholder: `sede.ssreyes.es`
- `san_domains` — input de chips (igual que tech_stack en apps), placeholder: `api.ssreyes.es`
- `issuer` — input libre, placeholder: `Let's Encrypt`, `FNMT`, `DigiCert` (se rellenará automáticamente vía Apache Flow)
- `issued_at` — date picker (opcional al crear manualmente)
- `expires_at` — date picker, **obligatorio**, resaltado si la fecha es <30 días desde hoy
- `serial_number` — input texto (opcional)
- `key_type` — select: RSA 2048 / RSA 4096 / ECDSA P-256 / ECDSA P-384 / Ed25519 / Otro
- `wildcard` — checkbox
- `auto_renew` — checkbox
- `managed_by` — input libre, placeholder: `cert-manager`, `manual`, `Keycloak`, `fnmt-portal`
- `environment` — select: Producción / Staging / Desarrollo / DR
- `ca_type` — select: CA pública / FNMT / CA interna / Autofirmado / Desconocida
- `notes` — textarea

Los siguientes campos se rellenan automáticamente por Apache Flow y se muestran en modo solo lectura en el formulario de edición manual (con etiqueta "Completado por Apache Flow"):
- `fingerprint_sha256`, `fingerprint_sha1`
- `issuer_common_name`, `issuer_organization`, `issuer_country`
- `subject_organization`, `subject_organizational_unit`, `subject_country`, `subject_state`, `subject_locality`
- `signature_algorithm`
- `key_usages`, `extended_key_usages`
- `ocsp_url`, `crl_url`, `ca_issuers_url`
- `chain_valid`
- `last_verified_at` (fecha de última sincronización con Apache Flow)

**Página de detalle del certificado** (al hacer click en el Common Name, ruta `/certificates/:id`):

La página se divide en secciones:

**Sección "Identificación":**
- Common Name con badge de estado (valid/expiring/critical/expired)
- Barra visual de tiempo restante: `[████████░░░░] 45 días restantes` (verde/naranja/rojo según estado)
- SANs como chips: `[sede.ssreyes.es] [api.ssreyes.es] [www.ssreyes.es]`
- Número de serie, Fingerprint SHA-256, Fingerprint SHA-1

**Sección "Entidad Certificadora":**
- Nombre del emisor (issuer_common_name)
- Organización del emisor
- País del emisor
- Tipo de CA con badge: `[CA Pública ✓]`, `[FNMT 🏛]`, `[CA Interna]`, `[Autofirmado ⚠]`
- Estado de la cadena: `[✓ Cadena válida]` o `[⚠ Cadena inválida]` (rojo si chain_valid=false)
- URL OCSP (link), URL CRL (link)

**Sección "Sujeto del certificado":**
- Organización, Unidad organizativa, País, Comunidad, Municipio
- (Solo visible si alguno de estos campos está relleno)

**Sección "Vigencia y criptografía":**
- Emitido el, Válido desde, Caduca el
- Tipo de clave, Algoritmo de firma
- Usos de clave (key_usages como chips), Usos extendidos (extended_key_usages como chips)
- ¿Wildcard?, ¿Es CA?

**Sección "Gestión":**
- Gestionado por, Renovación automática, Cuenta ACME, Entorno
- Última verificación (last_verified_at con badge "Apache Flow" si source="apache-flow")
- Notas

**Sección "Servicios que usan este certificado":**
Lista de servicios cuyos endpoints tienen `certificate_id` = este certificado:
```
Sede Electrónica (crítico) → https://sede.ssreyes.es [público, principal]
Portal de Empleo (alto)    → https://empleo.ssreyes.es [público]
```
Si no hay ninguno: *"Este certificado no está asignado a ningún endpoint de servicio."*

**Sección "Aplicaciones vinculadas":**
Lista de aplicaciones con AppInfraBinding de tipo certificate:
```
sede-frontend (producción) → binding_tier: certificate
```

**Botón "Ver en mapa de topología":** navega al mapa filtrando por el primer servicio que usa el certificado.

**Barra de búsqueda y filtros:**
- Búsqueda libre (common_name, issuer, SANs, subject_organization)
- Filtro por estado (todos / válido / caduca pronto / crítico / expirado)
- Filtro por tipo de CA (todos / CA pública / FNMT / CA interna / Autofirmado)
- Filtro por entorno
- Filtro por renovación auto (todos / Sí / No)

**Alerta sticky en la página** cuando hay certificados críticos o expirados:
```
🔴 Hay 1 certificado crítico que caduca en menos de 7 días. Renuévalo urgentemente.
```

#### Scenario: Certificado crítico con badge pulsante
- **GIVEN** un certificado con days_remaining=3
- **WHEN** se muestra en la tabla
- **THEN** el badge "🔴 Crítico" tiene animación `animate-pulse` y la fila tiene fondo rojo sutil

#### Scenario: Detalle con barra visual de tiempo restante
- **GIVEN** un certificado con 45 días restantes (30%)
- **WHEN** el usuario accede a su detalle
- **THEN** ve una barra de progreso en naranja mostrando "45 días restantes"

#### Scenario: Cadena de confianza inválida en detalle
- **GIVEN** un certificado con chain_valid=false
- **WHEN** se muestra la sección Entidad Certificadora en el detalle
- **THEN** aparece "⚠ Cadena inválida" en rojo con tooltip explicativo

#### Scenario: Certificado FNMT con datos completos
- **GIVEN** un certificado con ca_type="fnmt" y todos los campos de sujeto rellenos por Apache Flow
- **WHEN** el usuario ve el detalle
- **THEN** la sección Entidad Certificadora muestra el badge "FNMT 🏛" y todos los campos, con indicador "Completado por Apache Flow" en la sección Gestión

#### Scenario: Alerta sticky en cabecera
- **GIVEN** 1 certificado con status="critical"
- **WHEN** el admin abre el tab Certificados
- **THEN** aparece un banner rojo sticky encima de la tabla con el nombre del certificado y los días restantes

---

### Requirement: Tab "Servicios" — selector de certificado en endpoints (TLS del servicio)

**Sección "URLs / Endpoints del servicio"** en el detalle de un servicio SHALL mostrar para cada endpoint:
- URL (link clickable)
- Tipo (Público / Interno / VPN / API / Webhook) con badge
- ⭐ si is_primary
- **Badge TLS** junto a la URL:
  - Si `tls_status="none"` → badge gris `[Sin TLS]` — indica HTTP sin cifrar
  - Si `tls_status="valid"` → badge verde `[🔒 TLS válido]`
  - Si `tls_status="expiring"` → badge naranja `[⚠ TLS caduca pronto]`
  - Si `tls_status="critical"` → badge rojo pulsante `[🔴 TLS crítico]`
  - Si `tls_status="expired"` → badge rojo `[❌ TLS expirado]`
- Al hacer hover sobre el badge TLS (cuando no es "none") → tooltip con: CN, días restantes, emisor, fecha de caducidad
- Botón "✕" para eliminar el endpoint (editor+)

**Formulario "Añadir URL / endpoint"** (modal, editor+) SHALL incluir el campo de certificado:

1. `url` — obligatorio
2. `type` — select
3. `is_primary` — checkbox
4. `description` — input opcional
5. **`certificate_id` — selector de certificado TLS** (dropdown buscable):
   - Placeholder: *"Sin TLS (HTTP) — selecciona un certificado para usar HTTPS"*
   - El dropdown muestra cada certificado con: CN, badge de estado de caducidad, días restantes, emisor
   - Los certificados `expired` se muestran en gris con icono ❌ (seleccionables pero con advertencia)
   - Los certificados `critical` se muestran con fondo rojo sutil y advertencia al seleccionar
   - Si se deja en blanco → el endpoint se configura sin TLS
   - Filtro de búsqueda dentro del dropdown por CN o SAN

Al seleccionar un certificado `critical` o `expired`, aparece un aviso inline:
```
⚠ Este certificado caduca en N días. El endpoint quedará sin TLS válido pronto.
```

#### Scenario: Endpoint sin certificado — badge "Sin TLS"
- **GIVEN** un endpoint interno con certificate_id=null
- **WHEN** se muestra en la sección de URLs del servicio
- **THEN** aparece el badge gris "Sin TLS" junto a la URL

#### Scenario: Endpoint con certificado válido — badge verde
- **GIVEN** un endpoint con tls_status="valid"
- **WHEN** se muestra en la lista de URLs
- **THEN** aparece badge verde "🔒 TLS válido" con tooltip "sede.ssreyes.es · 87 días · Let's Encrypt"

#### Scenario: Dropdown de certificados con estado inline
- **GIVEN** un editor abre el formulario de añadir endpoint
- **WHEN** despliega el selector de certificado
- **THEN** ve cada certificado con su badge de estado: ✓ verde / ⚠ naranja / 🔴 rojo / ❌ gris

#### Scenario: Advertencia al seleccionar certificado crítico
- **GIVEN** el editor selecciona un certificado con days_remaining=4
- **WHEN** lo selecciona en el dropdown
- **THEN** aparece aviso inline "⚠ Este certificado caduca en 4 días"

#### Scenario: Servicio sin ningún endpoint TLS — indicador en tabla de servicios
- **GIVEN** un servicio con todos sus endpoints en tls_status="none"
- **WHEN** se muestra en la tabla de servicios
- **THEN** aparece un badge "Sin TLS" en la columna URLs



En el detalle de un servicio, la sección de componentes SHALL incluir una subsección **"Infraestructura del servicio"** que muestra los assets vinculados a cada aplicación del servicio, organizados por capa (binding_tier).

**Vista de infraestructura por capas (mini-mapa tabular):**
Para cada capa presente en el servicio, una fila con:
- Icono y nombre de la capa (Cómputo, Red, Datos, etc.)
- Badges de los assets en esa capa con su nombre y estado de compliance
- Indicador ⚠ si algún asset de esa capa tiene `is_single_point_of_failure=true`
- Indicador de redundancia si hay `redundancy_group`

**Formulario "Asociar infraestructura" (al añadir infra binding desde el detalle de aplicación):**

1. **Selector de asset o certificado** (toggle radio: "Asset del inventario" / "Certificado TLS")
   - Si Asset: búsqueda por nombre con dropdown igual que en excepciones
   - Si Certificado: dropdown de certificados con su estado de caducidad inline

2. **Selector de capa (binding_tier)** — botones con icono y descripción:
   ```
   [1 Entrada] [2 Gateway] [3 Certificado TLS] [4 Aplicación] [4 Auth]
   [5 Caché]  [5 Datos]   [6 Cómputo]         [7 Storage]    [8 Red]
   ```
   Al seleccionar un tier, se muestra el `tier_order` canónico. Si se activa "Sobrescribir orden", aparece un input numérico.

3. **Toggle "¿Crítico?"** — si este asset falla, ¿cae la aplicación?

4. **Toggle "¿Punto de fallo único?"** — no hay redundancia
   - Si se activa, aparece un aviso: *"Este asset no tiene redundancia. Considerar añadir otro asset al mismo grupo."*
   - Si se desactiva y se rellena `redundancy_group`, el aviso desaparece.

5. **Campo "Grupo de redundancia"** (opcional) — input texto libre, placeholder: `pg-cluster-prod`, `app-servers-lb`

6. **Notas** — textarea opcional

#### Scenario: Añadir servidor con tier compute y SPF
- **GIVEN** un editor añade "srv-app-01" a "sede-api" con tier="compute", is_critical=true, is_spf=true
- **WHEN** guarda el binding
- **THEN** el asset aparece en la capa Cómputo con icono ⚠ de punto de fallo único

#### Scenario: Añadir certificado a aplicación
- **GIVEN** un editor selecciona "Certificado TLS" en el toggle
- **WHEN** busca y selecciona "sede.ssreyes.es" (expiring, 12 días)
- **THEN** el certificado aparece en la capa Certificados con badge naranja "⚠ 12 días"

#### Scenario: Dos servidores en el mismo redundancy_group
- **GIVEN** "srv-app-01" y "srv-app-02" con redundancy_group="app-cluster"
- **WHEN** se muestra la capa Cómputo
- **THEN** ambos aparecen juntos con el badge "🔄 app-cluster" indicando redundancia

---

### Requirement: Tab "Mapa de Topología" — vista en carriles por capas (Layered View)

El mapa SHALL tener **dos modos de visualización** seleccionables con un toggle:

#### Modo A: "Vista de capas" (default)
Renderiza el grafo como **carriles horizontales**, uno por tier. Cada carril tiene:
- Etiqueta en el lado izquierdo: "TIER 1 — Punto de entrada", "TIER 2 — Gateway", etc.
- Nodos del tier alineados horizontalmente dentro del carril
- Altura del carril se ajusta al número de nodos
- Carriles vacíos se ocultan automáticamente

Layout de los nodos dentro de un carril:
- Los nodos se distribuyen uniformemente de izquierda a derecha
- Los nodos con `is_single_point_of_failure=true` tienen borde naranja pulsante
- Los nodos de certificado con `status=critical` tienen borde rojo pulsante

**Colores de carril (fondo sutil):**
| Tier | Color de fondo del carril |
|------|--------------------------|
| entry_point | `rgba(59,130,246,0.05)` azul muy sutil |
| gateway | `rgba(99,102,241,0.05)` índigo |
| certificate | `rgba(245,158,11,0.05)` ámbar — resalta la capa de certs |
| application/auth | `rgba(34,197,94,0.05)` verde |
| cache/data | `rgba(6,182,212,0.05)` cyan |
| compute | `rgba(107,114,128,0.05)` gris |
| storage | `rgba(75,85,99,0.05)` gris oscuro |
| network | `rgba(55,65,81,0.05)` gris muy oscuro |

#### Modo B: "Vista de grafo" (alternativa)
Mismo grafo que antes pero con layout dagre automático. Los nodos de certificado se muestran como rombos amarillos.

#### Controles del mapa (actualizados):
- Toggle **Vista Capas / Vista Grafo**
- Selector de servicio
- Toggle "Mostrar infraestructura"
- Toggle "Mostrar certificados"
- Toggle "Solo puntos de fallo único" — filtra mostrando solo la ruta crítica
- Toggle "Solo críticos" — aristas críticas únicamente
- **Panel de alertas** (si hay SPFs o certs expirados): banner amarillo/rojo con resumen
- Botón "Ver análisis de impacto" — abre drawer con el resultado de `/v1/assets/{id}/impact` para el asset seleccionado
- Botón "Exportar PNG"

#### Nodos — aspecto visual por tipo en Vista de Capas:

| Tipo | Forma | Color | Distintivo |
|------|-------|-------|-----------|
| Service | Rectángulo grande redondeado | Azul corporativo `#003F7F` | Badge criticality |
| Application | Rectángulo redondeado | Verde `#14532d` | Badge status + versión |
| Certificate válido | Rectángulo con icono 🔒 | Gris azulado | Días restantes en verde |
| Certificate expirando | Rectángulo con icono ⚠ | Naranja | Días restantes en naranja |
| Certificate crítico | Rectángulo con icono 🔴 | Rojo pulsante | Días restantes en rojo |
| Asset servidor | Rectángulo | Gris `#1f2937` | IPs debajo del nombre |
| Asset database | Cilindro visual (border-radius asimétrico) | Gris azulado | Motor (PG, MySQL…) |
| Asset switch/router | Hexágono visual | Gris oscuro | IPs |
| Asset SPF | Borde naranja pulsante | — | `⚠ SPF` label |

#### Panel lateral de detalle de asset (al hacer click):
Muestra la información del asset más:
- **Análisis de impacto**: llamada a `/v1/assets/{id}/impact` y muestra "Afecta a: [app1, app2]" → "Servicios: [Sede Electrónica (crítico)]"
- **Estado de compliance**: badges EDR/MON/SIEM en verde/rojo
- Si es certificado: estado, días restantes, emisor, SANs, enlace "Ir a certificados"

#### Scenario: Vista de capas con carril de certificados
- **GIVEN** el servicio "Sede Electrónica" con un cert en tier=3
- **WHEN** se carga el mapa en modo "Vista Capas"
- **THEN** aparece el carril "TIER 3 — Certificados TLS" con fondo ámbar y el certificado como nodo

#### Scenario: Análisis de impacto desde el mapa
- **GIVEN** el usuario hace click en "router-edge-01" (SPF) en el mapa
- **WHEN** el panel lateral se abre
- **THEN** muestra "Si falla: afecta a [sede-api] → [Sede Electrónica (crítico)]"

#### Scenario: Toggle "Solo puntos de fallo único"
- **GIVEN** el mapa tiene 20 nodos, 3 con is_spf=true
- **WHEN** el usuario activa "Solo puntos de fallo único"
- **THEN** el mapa muestra solo los 3 nodos SPF y sus rutas hacia los servicios afectados

#### Scenario: Carril de certificados con alerta
- **GIVEN** un certificado en el tier=3 con status="critical"
- **WHEN** se renderiza el carril de Certificados
- **THEN** el carril tiene fondo rojo sutil en lugar de ámbar, y el nodo del certificado pulsa

---

### Requirement: Leyenda actualizada del mapa

La leyenda fija en la esquina inferior izquierda SHALL incluir:
- Colores de nodo por tipo (Service, Application, Asset, Certificado)
- Colores de arista (COMPOSED_OF, DEPENDS_ON crítica, DEPENDS_ON no crítica, HOSTED_ON, SECURED_BY)
- Indicadores: `⚠ SPF` = punto de fallo único, `🔄` = redundante, `🔒` = certificado válido, `⚠🔴` = certificado crítico

---

### Requirement: Widget de alertas en cabecera de Aplicaciones

Cuando hay certificados en estado `critical` o `expired`, o assets marcados como SPF sin redundancia en servicios críticos, SHALL aparecer un banner de alerta en la cabecera del módulo de Aplicaciones (no solo en el tab de Certificados):

```
⚠ 1 certificado caduca en 3 días (sede.ssreyes.es) · 2 puntos de fallo único en servicios críticos
```

Cada parte del mensaje es un enlace al tab correspondiente.
---

### Requirement: Manejo de errores de API — nunca mostrar [object Object]

La función `req()` en `services/api.js` SHALL extraer siempre un mensaje legible del error, independientemente del formato que devuelva el backend.

**Regla:** `detail` en la respuesta de error FastAPI puede ser:
- `string` → error de negocio simple, ej: `"Asset not found"`
- `array` → errores de validación Pydantic (422), ej: `[{loc, msg, type}]`
- `object` → error genérico estructurado

El toast de error SHALL mostrar siempre texto legible para el usuario, nunca `[object Object]`.

#### Scenario: Mensaje de error legible en toast de infra binding
- **GIVEN** el usuario pulsa "Asociar" sin haber seleccionado un asset
- **WHEN** el backend responde 422 con errores de validación
- **THEN** el toast muestra un mensaje como "asset_id: field required" en lugar de "[object Object]"

#### Scenario: Error de negocio simple
- **GIVEN** el backend devuelve 404 con detail="Asset not found"
- **WHEN** el frontend captura el error
- **THEN** el toast muestra "Asset not found"

