# Tasks: Certificates

## 1. Modelo y DB
- [x] 1.1 Modelo Certificate: common_name, san_domains(JSON), expires_at(INDEX),
           issued_at, ca_type, key_type, wildcard, auto_renew, fingerprint_sha256(INDEX)
- [x] 1.2 cert_status calculado: valid/expiring(≤30d)/critical(≤7d)/expired
- [x] 1.3 days_remaining calculado: (expires_at - today).days
- [x] 1.4 ServiceEndpoint.certificate_id FK → certificates.id SET NULL
- [x] 1.5 ServiceEndpoint.tls_status: propiedad calculada que consulta el cert

## 2. Backend
- [x] 2.1 CRUD /v1/certificates con search y status filter
- [x] 2.2 GET /v1/certificates/expiry-summary — ANTES de /{id} en el router
       Devuelve: {total, valid, expiring, critical, expired}

## 3. Frontend
- [x] 3.1 CertificatesPage /certificates: tab desde InventoryPage
- [x] 3.2 Panel de resumen con 5 contadores (total, válidos, próximos, críticos, expirados)
- [x] 3.3 Tabla con columnas: CN, emisor, estado, días restantes, SAN, wildcard, auto-renew
- [x] 3.4 Tab "Certificados 🔒" en InventoryPage — sidebar permanece activo en "Inventario"

## 4. Seed de certificados (init_db.py)

- [x] 4.1 cert-001: *.ssreyes.org — wildcard, válido 245 días, DigiCert, producción
- [x] 4.2 cert-002: sede.ssreyes.es — FNMT, CRÍTICO caduca en 5 días, sin auto-renew
- [x] 4.3 cert-003: api-interna.ssreyes.lan — CA interna, caduca en 22 días (expiring)
- [x] 4.4 cert-004: staging.ssreyes.lan — CA interna, válido 180 días, staging
- [x] 4.5 cert-005: keycloak.ssreyes.lan — CA interna, EXPIRADO hace 15 días

Estos 5 certificados cubren todos los estados posibles: valid, expiring, critical, expired.
Vinculados a ServiceEndpoints del seed de aplicaciones.
