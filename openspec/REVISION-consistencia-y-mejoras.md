# Revisión OpenSpec: Consistencia, Organización, Seguridad y Mejoras

**Fecha:** 2026-03-15  
**Alcance:** `openspec/` (config, changes: audit-logs, app-core, inventory-master, login, tags-management, user-profile, unit-test).

---

## 1. Consistencia

### 1.1 Nombre del campo de diff en Audit Logs

- **Problema:** En `audit-logs/specs/frontend/spec.md` (línea 40) se referencia el campo **`details`** para el JSON diff del modal.
- **Resto del sistema:** En `audit-logs/tasks.md`, `design.md`, `specs/api` y `unit-test` se usa **`changes`** (JSONB).
- **Recomendación:** Unificar en **`changes`** en todo el change audit-logs. Cambiar en `audit-logs/specs/frontend/spec.md` la frase "almacenado en el campo `details`" por "almacenado en el campo `changes`".

### 1.2 Comentario incorrecto en `.openspec.yaml`

- **Problema:** `audit-logs/.openspec.yaml` tiene como comentario `# openspec/changes/inventory-master/.openspec.yaml`.
- **Recomendación:** Sustituir por `# openspec/changes/audit-logs/.openspec.yaml`.

### 1.3 Estructura de specs por change

- **audit-logs:** api, backend, frontend, infrastructure ✅
- **inventory-master:** api, backend, frontend ✅
- **app-core:** api, backend, frontend ✅ (sin design.md; si el schema exige design para apply, añadir uno)
- **login:** solo auth (specs/auth/spec.md); existen también login/specs/backend y login/specs/frontend en el árbol
- **tags-management, user-profile:** api, frontend; tags/user-profile tienen además specs/backend
- **unit-test:** solo specs/testing

La organización es aceptable; solo conviene definir si cada change debe tener siempre las mismas capacidades (api/backend/frontend/infra) o si por tipo (auth, testing) se permite una estructura distinta, y documentarlo en el config o en un README de OpenSpec.

---

## 2. Organización desde el punto de vista OpenSpec

### 2.1 Orden de aplicación y dependencias

- **app-core** describe el scaffold full-stack y referencia assets, tags, audit y auth. Los changes **inventory-master**, **tags-management**, **audit-logs** y **login** definen el detalle de cada dominio.
- **Recomendación:** Documentar orden sugerido de apply, por ejemplo en `openspec/README.md` o en el propio `config.yaml` (sección opcional `apply_order`), e.g.:
  1. login (auth primero)
  2. app-core (scaffold)
  3. inventory-master, tags-management, user-profile
  4. audit-logs
  5. unit-test

Así se evita aplicar app-core antes de tener definidos los contratos de auth y de los demás módulos.

### 2.2 Duplicación de requisitos entre app-core e inventory-master / audit-logs

- app-core/specs/api y inventory-master/specs/api (y audit-logs) comparten requisitos (Asset polimórfico, compliance, as_of, audit).
- **Recomendación:** Considerar que app-core sea el “contrato global” y que inventory-master y audit-logs usen **MODIFIED** o **ADDED** sobre esos requisitos cuando aporten detalle extra, para que los deltas no repitan el mismo texto y sea más fácil mantener consistencia.

### 2.3 config.yaml y parseo YAML

- En línea 48 de `config.yaml`:  
  `Validación: 'pattern', 'format' y 'maxLength' obligatorios en todos los inputs.`
- Algunos parsers YAML pueden tener problemas con comillas simples dentro de la misma cadena.
- **Recomendación:** Usar comillas dobles para la cadena completa o escapar; por ejemplo:  
  `- "Validación: 'pattern', 'format' y 'maxLength' obligatorios en todos los inputs."`  
  Así se evitan fallos de `openspec validate` o de otras herramientas que lean el config.

---

## 3. Seguridad

### 3.1 Lo que ya está bien cubierto

- **config.yaml:** OWASP (SQLi, XSS, CSRF, Secure Headers), ORM, Keycloak OIDC + PKCE, RBAC, K8s NetworkPolicies, contenedores non-root.
- **audit-logs:** Inmutabilidad de logs, sanitización de datos sensibles en diff (design), CORS configurable, health checks, Secrets en K8s.
- **login:** RS256, JWKS, verificación iss/aud/azp, roles en JWT, ProtectedRoute.
- **user-profile:** Validación tipo/tamaño avatar, UUID para nombre de archivo (Path Traversal), EXIF, Magic Bytes.
- **infrastructure (audit-logs):** Secrets para JWT y Postgres, CORS y mención a CSRF.

### 3.2 Mejoras de definición en seguridad

- **Rate limiting:** No aparece en specs. Recomendación: añadir en config (rules.backend_code o openapi_spec) una regla tipo “Endpoints públicos o de login deben tener rate limiting (por IP y/o por usuario)” y reflejarlo en el design/backend de login y, si aplica, en app-core.
- **Secure Headers:** Están en config pero no en specs por capability. Recomendación: en backend (o infrastructure) de app-core o audit-logs, añadir un requirement que exija headers (e.g. X-Content-Type-Options, X-Frame-Options, Content-Security-Policy, Strict-Transport-Security) y un escenario de verificación.
- **CSRF:** CORS está cubierto; para flujos con cookies (tokens en cookie HttpOnly), conviene dejar explícito que el flujo OIDC + PKCE y el uso de SameSite en cookies son la mitigación principal, y que no hay formularios tradicionales que requieran token CSRF adicional. Se puede añadir una línea en login/proposal o en design.
- **Paginación y filtros audit-logs:** Ya se exigen filtros obligatorios y se menciona paginación en design. Recomendación: que en api/backend de audit-logs quede explícito un límite máximo de resultados por página (p.ej. 100) para evitar fugas de datos y carga.

---

## 4. RFCs y estándares

- **OpenAPI:** config y app-core exigen OpenAPI 3.1 ✅
- **OIDC:** Keycloak, Authorization Code + PKCE ✅
- **Recomendación (opcional):** En config o en un doc de “Estándares”, citar explícitamente:
  - RFC 6749 (OAuth 2.0)
  - RFC 7636 (PKCE)
  - OpenID Connect Core 1.0
  - OpenAPI 3.1.0
  Así queda trazabilidad para auditoría y cumplimiento.

---

## 5. Funcionamiento en cualquier navegador

- En specs no hay requisitos explícitos de compatibilidad de navegador.
- **Recomendación:** Añadir en `config.yaml` (context o rules.frontend_code) algo como:
  - “La aplicación web debe ser utilizable en navegadores modernos (evergreen): Chrome, Firefox, Safari, Edge en sus dos últimas versiones principales; y debe degradar de forma controlada en navegadores más antiguos (mensaje claro, sin fallos críticos).”
- Opcional: en app-core o en un change de “frontend-base”, un requirement de que la UI no dependa de APIs o características no soportadas en esos navegadores (p.ej. evitar dependencias que rompan en Safari sin polyfills).

---

## 6. Resumen de acciones sugeridas

| Prioridad | Acción |
|----------|--------|
| Alta | Unificar `details` → `changes` en audit-logs/specs/frontend/spec.md |
| Alta | Corregir comentario en audit-logs/.openspec.yaml a `audit-logs` |
| Media | Ajustar comillas en config.yaml línea 48 para evitar errores de parseo |
| Media | Documentar orden de apply (login → app-core → dominio → audit-logs → unit-test) |
| Media | Añadir requirement de Secure Headers en backend/infra y de rate limiting en auth/backend |
| Baja | Citar RFCs (6749, 7636, OIDC, OpenAPI 3.1) en config o estándares |
| Baja | Añadir requisito de compatibilidad con navegadores modernos en config (frontend_code) |

---

## 7. Conclusión

El contenido de OpenSpec es **consistente en su mayoría** y está **bien organizado** por changes y por capabilities (api, backend, frontend, infra). Las correcciones más importantes son la unificación del nombre del campo de diff (`changes`), el comentario del `.openspec.yaml` de audit-logs y la robustez del `config.yaml` frente al parseo YAML. Con las mejoras de seguridad (rate limiting, Secure Headers, aclaración CSRF) y la definición de orden de apply y de compatibilidad de navegador, la especificación queda más clara, segura y alineada con RFCs y buenas prácticas.
