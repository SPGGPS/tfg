# OpenSpec – TFG

Especificaciones y cambios del proyecto TFG (CMDB, inventario, auditoría, auth).

## Orden recomendado de apply

Para aplicar los changes con las dependencias correctas, usar este orden:

1. **login** — Auth primero (Keycloak OIDC + PKCE, RBAC).
2. **app-core** — Scaffold full-stack (FastAPI + React + OpenAPI + DB).
3. **inventory-master**, **tags-management**, **user-profile** — Dominios de negocio (orden intercambiable).
4. **audit-logs** — Auditoría (depende de auth y de los endpoints que registra).
5. **unit-test** — Especificaciones de prueba (validar tras implementar).

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
