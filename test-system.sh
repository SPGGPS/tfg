#!/bin/bash

# 🚀 Script de Testing Rápido - TFG CMDB
# Verifica que todos los componentes funcionen correctamente

echo "🧪 Iniciando tests del sistema TFG CMDB..."
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar endpoint
check_endpoint() {
    local url=$1
    local expected_code=$2
    local description=$3

    echo -n "Testing $description... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$response" -eq "$expected_code" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL (HTTP $response, expected $expected_code)${NC}"
        return 1
    fi
}

# Función para verificar JSON response
check_json_response() {
    local url=$1
    local description=$2

    echo -n "Testing $description... "
    response=$(curl -s "$url")

    if echo "$response" | jq . >/dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL (Invalid JSON)${NC}"
        return 1
    fi
}

# Verificar que los servicios estén corriendo
echo "📡 Verificando conectividad de servicios..."
echo "--------------------------------------------------"

# Backend health check
if check_endpoint "http://localhost:8000/v1/healthz" 200 "Backend Health Check"; then
    backend_ok=true
else
    backend_ok=false
    echo -e "${YELLOW}⚠️  Backend no responde. ¿Ejecutaste 'docker-compose up'?${NC}"
fi

# Verificar APIs si backend está OK
if [ "$backend_ok" = true ]; then
    echo ""
    echo "🔍 Verificando APIs del Backend..."
    echo "--------------------------------------------------"

    # Health check con JSON
    check_json_response "http://localhost:8000/v1/healthz" "Health Check JSON"

    # Assets API
    check_endpoint "http://localhost:8000/v1/assets" 200 "Assets API"
    check_json_response "http://localhost:8000/v1/assets" "Assets JSON Response"

    # Tags API
    check_endpoint "http://localhost:8000/v1/tags" 200 "Tags API"
    check_json_response "http://localhost:8000/v1/tags" "Tags JSON Response"

    # Audit Logs API (debería requerir admin, pero por ahora permite)
    check_endpoint "http://localhost:8000/v1/audit-logs?activity_type=CREATE&user_id=system&date_from=2024-01-01T00:00:00&date_to=2025-12-31T23:59:59" 200 "Audit Logs API"

    # Auth API
    check_endpoint "http://localhost:8000/v1/auth/oidc/config" 200 "OIDC Config API"

    echo ""
    echo "📊 Verificando datos de prueba..."
    echo "--------------------------------------------------"

    # Verificar que hay assets
    assets_count=$(curl -s "http://localhost:8000/v1/assets" | jq '.total // 0')
    if [ "$assets_count" -gt 0 ]; then
        echo -e "Assets en BD: ${GREEN}$assets_count${NC} ✅"
    else
        echo -e "Assets en BD: ${RED}$assets_count${NC} ❌"
    fi

    # Verificar que hay tags
    tags_count=$(curl -s "http://localhost:8000/v1/tags" | jq '.items | length // 0')
    if [ "$tags_count" -gt 0 ]; then
        echo -e "Tags en BD: ${GREEN}$tags_count${NC} ✅"
    else
        echo -e "Tags en BD: ${RED}$tags_count${NC} ❌"
    fi

    # Verificar auditoría
    audit_count=$(curl -s "http://localhost:8000/v1/audit-logs?activity_type=CREATE&user_id=system&date_from=2024-01-01T00:00:00&date_to=2025-12-31T23:59:59" | jq '.total // 0')
    if [ "$audit_count" -gt 0 ]; then
        echo -e "Registros de auditoría: ${GREEN}$audit_count${NC} ✅"
    else
        echo -e "Registros de auditoría: ${YELLOW}$audit_count${NC} ⚠️"
    fi
fi

# Verificar frontend (si está corriendo)
echo ""
echo "🌐 Verificando Frontend..."
echo "--------------------------------------------------"

if curl -s -f "http://localhost:5173" >/dev/null 2>&1; then
    echo -e "Frontend: ${GREEN}✅ OK${NC}"
    frontend_ok=true
else
    echo -e "Frontend: ${YELLOW}⚠️  No responde (¿ejecutaste 'npm run dev'?)${NC}"
    frontend_ok=false
fi

echo ""
echo "📋 Resumen de Testing"
echo "=================================================="

if [ "$backend_ok" = true ]; then
    echo -e "Backend: ${GREEN}✅ FUNCIONANDO${NC}"
    echo "  📍 http://localhost:8000"
    echo "  📚 http://localhost:8000/docs"
else
    echo -e "Backend: ${RED}❌ NO FUNCIONA${NC}"
fi

if [ "$frontend_ok" = true ]; then
    echo -e "Frontend: ${GREEN}✅ FUNCIONANDO${NC}"
    echo "  📍 http://localhost:5173"
else
    echo -e "Frontend: ${YELLOW}⚠️  NO FUNCIONA${NC}"
fi

echo ""
echo "🎯 Próximos pasos:"
echo "1. Si algo falla, ejecuta: docker-compose up --build"
echo "2. Accede al frontend y prueba las funcionalidades"
echo "3. Revisa los logs con: docker-compose logs -f"
echo ""
echo "¡Sistema TFG CMDB listo para testing! 🚀"