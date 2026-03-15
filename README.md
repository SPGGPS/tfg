# 🚀 TFG - CMDB - Guía Completa

Sistema completo de CMDB (Configuration Management Database) con FastAPI backend, React frontend y PostgreSQL. **¡AHORA FUNCIONAL!**

## 📋 Prerrequisitos

- **Docker & Docker Compose** (recomendado para desarrollo rápido)
- **Node.js 18+** y **Python 3.11+** (si no usas Docker)

## 🏃‍♂️ Inicio Rápido con Docker (Recomendado)

### 1. Levantar todo el stack
```bash
cd /ruta/a/tu/proyecto/tfg
docker-compose up --build
```

### 2. Acceder a la aplicación
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Base de datos**: localhost:5432 (tfg/tfg)

### 3. ¡Datos de prueba incluidos automáticamente!
- ✅ 5 activos realistas (servidores, switches, routers, APs)
- ✅ Etiquetas del sistema y manuales
- ✅ Registros de auditoría automáticos

## 🔧 Inicio Manual (Sin Docker)

### Backend
```bash
cd backend
pip install -e .
python init_db.py  # Inicializar BD con datos de prueba
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Base de datos
```bash
# PostgreSQL local
createdb tfg
psql -d tfg -c "CREATE USER tfg WITH PASSWORD 'tfg';"
psql -d tfg -c "GRANT ALL PRIVILEGES ON DATABASE tfg TO tfg;"
```

## 🎯 Funcionalidades Implementadas

### ✅ Backend (FastAPI)
- **Assets API**: CRUD completo con filtros, paginación y asignación masiva de tags
- **Tags API**: Gestión completa de etiquetas (manuales/sistema)
- **Audit Logs**: Logs automáticos de todas las operaciones
- **Health Checks**: Endpoints de monitoring
- **Auditoría Automática**: Interceptor que registra cambios en BD

### ✅ Frontend (React + Vite)
- **Dashboard de Inventario**: Tabla completa con filtros, selección múltiple
- **Gestión de Tags**: Crear, editar, eliminar etiquetas con colores
- **Auditoría**: Vista de logs (solo admin)
- **UI Moderna**: Tailwind CSS + TanStack Table + React Query

### ✅ Base de Datos
- **PostgreSQL**: Modelo relacional completo
- **Auditoría**: Triggers automáticos en SQLAlchemy
- **Datos de Prueba**: Assets y tags realistas

## 🔐 Roles y Permisos

- **Viewer**: Solo lectura de inventario
- **Editor**: Gestión de tags manuales
- **Admin**: Acceso completo + auditoría

*(Por ahora todos los usuarios tienen rol "viewer" por defecto)*

## 🧪 Testing Rápido

### Verificar que todo funciona:
1. **Health Check**: http://localhost:8000/v1/healthz
2. **API Assets**: http://localhost:8000/v1/assets
3. **API Tags**: http://localhost:8000/v1/tags
4. **Frontend**: http://localhost:5173

### Endpoints principales:
```bash
# Assets
GET  /v1/assets              # Listar con filtros
POST /v1/assets/bulk-tags    # Asignar tags masivamente

# Tags
GET  /v1/tags               # Listar tags
POST /v1/tags               # Crear tag
PUT  /v1/tags/{id}          # Actualizar tag
DELETE /v1/tags/{id}        # Eliminar tag

# Audit
GET /v1/audit-logs          # Logs de auditoría (admin)

# Auth
GET /v1/auth/oidc/config    # Config OIDC
```

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │    │   PostgreSQL    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│                 │    │                 │    │                 │
│ - Dashboard     │    │ - REST API      │    │ - Assets        │
│ - Tag Mgmt      │    │ - Auth/ACL      │    │ - Tags          │
│ - Audit Logs    │    │ - Audit Trail   │    │ - Audit Logs    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Estructura del Proyecto

```
tfg/
├── openspec/          # Especificaciones OpenSpec
├── backend/           # API FastAPI (Python)
│   ├── app/
│   │   ├── models/    # SQLAlchemy models
│   │   ├── routers/   # API endpoints
│   │   ├── database.py # Config BD
│   │   └── main.py    # FastAPI app
│   ├── init_db.py     # Script inicialización
│   └── Dockerfile
├── frontend/          # UI React
│   ├── src/
│   │   ├── pages/     # Dashboard, Tags, Audit
│   │   ├── components/# Layout, ProtectedRoute
│   │   └── services/  # API client
│   └── Dockerfile
├── docker-compose.yml # Desarrollo completo
└── README.md
```

## 🚀 Próximos Pasos

1. **Autenticación**: Implementar Keycloak OIDC completo
2. **Historificación**: Sistema de point-in-time queries
3. **Auto-tagging**: Reglas automáticas por vendor/tipo
4. **Kubernetes**: Despliegue en cluster
5. **Monitoreo**: Métricas y alertas

## 📝 Notas Técnicas

- **Backend**: SQLAlchemy async con interceptor de auditoría
- **Frontend**: TanStack Query + React Table + Tailwind CSS
- **BD**: PostgreSQL con relaciones complejas y JSONB
- **Testing**: Docker Compose para desarrollo integrado

¡El sistema está **100% funcional** y listo para desarrollo avanzado! 🎉
