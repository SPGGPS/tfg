# Backend - Tests (E2E / Integration)

## ADDED Requirements

### Requirement: Entorno de pruebas reproducible
El backend SHALL incluir fixtures y datos de prueba para ejecutar tests de integración de forma determinista.

#### Scenario: Setup de pruebas
- **GIVEN** una base de datos de pruebas vacía
- **WHEN** se ejecutan los tests
- **THEN** el sistema levanta datos de ejemplo y los elimina al terminar

### Requirement: Cobertura de endpoints críticos
Los tests SHALL cubrir endpoints de auditoría, tags y assets.

#### Scenario: Validación de acceso
- **GIVEN** un usuario con rol 'viewer'
- **WHEN** intenta acceder a /v1/audit-logs
- **THEN** recibe 403 Forbidden
