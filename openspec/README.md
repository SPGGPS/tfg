# OpenSpec – Inventario Centralizado (Ayuntamiento SSReyes)

Especificaciones y cambios del proyecto Inventario Centralizado (CMDB, inventario, auditoría, auth, excepciones, branding).

## Orden recomendado de apply

Para aplicar los changes con las dependencias correctas, usar este orden:

1. **login** — Auth primero (Keycloak OIDC + PKCE, RBAC).
2. **app-core** — Scaffold full-stack (FastAPI + React + OpenAPI + DB).
3. **branding** — Identidad visual corporativa (nombre, logo, paleta SSReyes).
4. **inventory-master**, **tags-management**, **user-profile** — Dominios de negocio (orden intercambiable).
5. **applications** — Aplicaciones, servicios y mapa de dependencias (depende de inventory-master para los asset bindings).
5. **exceptions** — Excepciones de compliance (depende de inventory-master y audit-logs).
6. **audit-logs** — Auditoría (depende de auth y de los endpoints que registra).
7. **unit-test** — Especificaciones de prueba (validar tras implementar).

Comando por change:

```bash
openspec instructions apply --change <nombre>
```

## Estructura

- **config.yaml** — Contexto global, rutas, reglas por artefacto.
- **changes/** — Cambios activos (proposal, design, specs, tasks).
- **changes/archive/** — Cambios archivados.
- **specs/** — Especificaciones consolidadas (tras archivar).

## Validación

```bash
openspec validate --changes
# o
openspec validate --all
```

## Revisión de consistencia y mejoras

Ver `REVISION-consistencia-y-mejoras.md` para el informe de revisión (consistencia, seguridad, RFCs, navegadores).
