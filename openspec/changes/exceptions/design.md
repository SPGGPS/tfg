# Design: Compliance Exceptions

## Context
Los indicadores de compliance (EDR/MON/SIEM/LOGS/BCK/BCKCL) se establecen automáticamente
desde los orígenes de datos. Algunos activos no pueden cumplirlos por razones legítimas.

## Sistema de 4 estados

| Estado | CSS | Condición |
|--------|-----|-----------|
| ok | bg-green-900/60 text-green-300 | Origen activo, sin excepción |
| ok_with_exception | compliance-gradient (azul→verde) | Origen OK + excepción activa |
| ko_with_exception | compliance-gradient-temp (azul→rojo) | Origen KO + excepción |
| ko | bg-red-900/60 text-red-300 | Origen KO, sin excepción |

El azul (#1d4ed8) en los gradientes es SEMÁNTICO — representa "hay excepción registrada".
NO es el rojo corporativo y NO debe cambiarse con el branding.

```css
.compliance-gradient      { background: linear-gradient(135deg, #1d4ed8 50%, #15803d 50%); }
.compliance-gradient-temp { background: linear-gradient(135deg, #1d4ed8 50%, #991b1b 50%); }
```

## Ciclo de vida
1. Admin crea excepción para (asset(s), indicador) con reason_code + description + expires_at
2. Activa: revoked_at IS NULL AND (expires_at IS NULL OR expires_at > now())
3. Admin revoca: soft delete — rellena revoked_by, revoked_by_name, revoked_at

## Decisiones

| Decisión | Rationale |
|----------|-----------|
| Soft delete | Trazabilidad: quién revocó y cuándo |
| reason_code enum | Catálogo finito de razones; evita texto libre inconsistente |
| expires_at nullable | Permanente (null) o temporal (fecha) |
| Bulk por asset_ids | Un indicador puede afectar a muchos activos del mismo tipo |
