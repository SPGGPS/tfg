# Recomendaciones de Seguridad y UX

**Fecha:** 2026-03-15  
**Contexto:** Revisión experta de la CMDB TFG para mejorar auditorías de seguridad y experiencia de usuario.

---

## SEGURIDAD

### 🔴 Alta prioridad

#### SEC-01: Content Security Policy (CSP) estricta
La CSP actual es permisiva (`unsafe-inline` en styles). Recomendación: usar nonces o hashes para estilos inline y eliminar `unsafe-inline`. Añadir `frame-ancestors 'none'` para prevenir clickjacking.

#### SEC-02: Tokens de avatar no predecibles en URL
Actualmente el avatar se sirve en `/v1/auth/me/avatar/:filename`. Si el filename fuera predecible o enumerable, otro usuario podría acceder. Recomendación: servir el avatar autenticado en `/v1/auth/me/avatar` (sin filename en la URL), resolviendo el filename desde user_profiles por el JWT del solicitante. Implementado en el spec de user-profile.

#### SEC-03: Registro de intentos de login fallidos
Sin registro de logins fallidos no es posible detectar ataques de fuerza bruta ni alertar al usuario. Implementado en el spec de user-profile (last_failed_login_at/ip).

#### SEC-04: Rotación de refresh tokens (Refresh Token Rotation)
Keycloak soporta Single-Use Refresh Tokens. Activarlo previene que un token robado pueda usarse indefinidamente. Configurar en Keycloak: `Revoke Refresh Token = ON`, `Refresh Token Max Reuse = 0`.

#### SEC-05: Audit log de acceso a datos sensibles
Actualmente se registran cambios en assets y tags, pero no las consultas de lectura en bulk. Recomendación: registrar en audit_logs los accesos de exportación masiva o consultas históricas (as_of) por usuarios con rol viewer, para detectar exfiltración.

#### SEC-06: Validación de `redirect_uri` en OIDC
El frontend debe usar exactamente la redirect_uri registrada en Keycloak. Nunca construirla dinámicamente desde parámetros de URL. Previene Open Redirect attacks en el flujo PKCE.

### 🟡 Media prioridad

#### SEC-07: Cabecera `Permissions-Policy`
Añadir `Permissions-Policy: geolocation=(), microphone=(), camera=()` para deshabilitar APIs de navegador no usadas.

#### SEC-08: Subresource Integrity (SRI) en assets externos
Si se cargan fuentes o scripts de CDN externos, añadir atributos `integrity` y `crossorigin` para prevenir ataques de supply chain.

#### SEC-09: Timeout de sesión por inactividad
Keycloak permite configurar `SSO Session Idle` y `Access Token Lifespan`. Recomendación: Access Token = 5 min, Refresh Token = 30 min, SSO Session Idle = 4h. Reducir la ventana de exposición ante tokens robados.

#### SEC-10: Sanitización de campos de búsqueda en backend
El parámetro `search` debe sanitizarse antes de usarlo en LIKE queries (escapar `%` y `_`). SQLAlchemy lo hace automáticamente con `ilike()` pero debe verificarse en el test TS-03.

#### SEC-11: Política de retención de user_profiles
Los campos last_failed_login_at/ip deben limpiarse tras N días (90 recomendado) para cumplir con GDPR/LOPD. Añadir al CronJob de limpieza diaria.

#### SEC-12: Headers de caché en respuestas con datos sensibles
Añadir `Cache-Control: no-store` en endpoints que devuelven datos de inventario o perfil, para evitar que proxies intermedios cacheen información sensible.

### 🟢 Baja prioridad

#### SEC-13: Enumeración de usuarios
El endpoint GET /v1/auth/me/avatar no debe revelar si un user_id existe o no mediante el código de respuesta (404 vs 403). Devolver siempre el avatar del usuario autenticado (no aceptar user_id externo en la URL).

#### SEC-14: Logging estructurado con correlation ID
Añadir un `X-Request-ID` header en todas las peticiones (generado por el frontend o por Traefik mediante middleware). El backend debe propagarlo en todos los logs para facilitar la trazabilidad en auditorías.

---

## UX

### 🎨 Visualización

#### UX-01: Columna Compliance — rectángulos con texto ✅ (ya en spec)
Los rectángulos EDR/MON/SIEM/LOGS/BCK/BCKCL con color verde/rojo son más legibles que los puntos. Añadir tooltip con descripción del estado al hacer hover.

#### UX-02: Ordenación por cabecera de columna con iconos ✅ (ya en spec)
Eliminar el combo de ordenación. Los iconos ↑↓ en cabecera son el patrón estándar de tablas de datos. Columna activa muestra el icono en color primario, las demás en gris.

#### UX-03: Página de detalle de activo ✅ (ya en spec)
Muy recomendable. Permite mostrar información que no cabe en la tabla sin sobrecargarla. Sugerencia de estructura en el detalle:
- Header con nombre, tipo badge y estado de compliance resumido
- Tabs o secciones: "General", "Compliance", "Técnico", "Etiquetas", "Historial"

#### UX-04: Estado vacío diferenciado
Cuando no hay resultados por filtros activos, mostrar un estado vacío con el mensaje "Sin resultados para los filtros actuales" y un botón "Limpiar filtros". Diferente al estado vacío de "No hay activos" cuando la BD está vacía.

#### UX-05: Skeleton loaders en lugar de spinner global
Los skeleton loaders (filas grises animadas) dan sensación de carga más rápida. Ya implementados en TableSkeleton. Asegurarse de que se usan en todas las transiciones de página, no solo en la carga inicial.

#### UX-06: Indicador de "última actualización" en header de tabla
Mostrar junto al estado Live/Histórico cuándo se realizó la última sincronización del dato más reciente. Ejemplo: "● Live · sincronizado hace 3 min". Reduce la ansiedad del usuario sobre la frescura de los datos.

#### UX-07: Paginación con salto de página
La paginación actual solo tiene Anterior/Siguiente. Para tablas con muchos activos, añadir un input numérico o botones de páginas con "..." para saltar directamente.

#### UX-08: Persistencia de filtros en URL (query params)
Los filtros activos (búsqueda, tipo, etiqueta, as_of) deben reflejarse en los query params de la URL (`?search=cisco&type=switch`). Así el usuario puede compartir un enlace a una vista filtrada y el navegador recuerda la posición al volver atrás.

#### UX-09: Confirmación visual en acciones masivas
Tras asignar etiquetas masivamente, mostrar un toast/notificación de éxito con el resumen: "Etiqueta 'Producción' asignada a 5 activos". Desaparece automáticamente en 4 segundos.

#### UX-10: Accesibilidad (A11y)
- Los rectángulos de compliance deben tener `role="status"` y `aria-label` descriptivo para lectores de pantalla.
- Los botones de etiqueta clickable deben tener `aria-pressed` indicando si el filtro está activo.
- El campo de búsqueda debe tener `aria-label="Buscar activos"`.

---

## Resumen de acciones por prioridad

| ID | Tipo | Prioridad | Acción |
|----|------|-----------|--------|
| SEC-01 | Seguridad | Alta | CSP estricta sin unsafe-inline |
| SEC-02 | Seguridad | Alta | Avatar por JWT, no por filename en URL |
| SEC-03 | Seguridad | Alta | Registro de logins fallidos (implementado en spec) |
| SEC-04 | Seguridad | Alta | Refresh Token Rotation en Keycloak |
| SEC-05 | Seguridad | Alta | Audit log de lecturas masivas |
| SEC-06 | Seguridad | Alta | Validar redirect_uri estáticamente |
| SEC-07 | Seguridad | Media | Permissions-Policy header |
| SEC-08 | Seguridad | Media | SRI en assets externos |
| SEC-09 | Seguridad | Media | Timeout de sesión por inactividad |
| SEC-10 | Seguridad | Media | Sanitización del parámetro search |
| SEC-11 | Seguridad | Media | Retención GDPR de user_profiles |
| SEC-12 | Seguridad | Media | Cache-Control: no-store en APIs sensibles |
| UX-03 | UX | Alta | Página de detalle de activo (implementada en spec) |
| UX-04 | UX | Alta | Estado vacío diferenciado con "Limpiar filtros" |
| UX-06 | UX | Media | Indicador de última sincronización en header |
| UX-08 | UX | Media | Filtros persistentes en query params de URL |
| UX-09 | UX | Media | Toast de confirmación en acciones masivas |
| UX-10 | UX | Media | Accesibilidad A11y en tabla |
