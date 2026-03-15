# TFG Backend (FastAPI)

Primera versión: scaffold con `/v1/healthz`, CORS, Secure Headers y stubs de `/v1/assets`, `/v1/tags`, `/v1/audit-logs`, `/v1/auth`.

## Requisitos

- Python 3.11+

## Instalación

```bash
cd backend
pip install -e .
# o: uv pip install -e .
```

## Ejecución

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/v1/healthz

## Variables de entorno

| Variable        | Descripción              | Por defecto                          |
|----------------|--------------------------|--------------------------------------|
| CORS_ORIGINS   | Orígenes permitidos CORS | http://localhost:5173,localhost:3000 |
| DEBUG          | Modo debug               | false                                |
| DATABASE_URL   | URL de PostgreSQL        | postgresql+asyncpg://...             |
| KEYCLOAK_ISSUER| Issuer Keycloak          | http://localhost:8080/realms/tfg     |
