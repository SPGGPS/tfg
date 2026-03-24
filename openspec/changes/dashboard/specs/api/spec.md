# API Spec — Dashboard

## GET /v1/dashboard

Devuelve todos los datos necesarios para el dashboard en una sola query.
Requiere viewer.

### Respuesta
```json
{
  "kpis": {
    "total_assets": 10,
    "active_exceptions": 5,
    "total_certificates": 5,
    "critical_certs": 2
  },
  "eol_by_type": [
    {
      "type": "server_physical",
      "label": "Servidores físicos",
      "total": 2,
      "segments": [
        {"status": "eol_ko",   "label": "EOL KO",    "count": 0, "color": "#dc2626", "asset_ids": []},
        {"status": "eol_warn", "label": "EOL WARN",  "count": 1, "color": "#d97706", "asset_ids": ["uuid1"]},
        {"status": "eol_ok",   "label": "EOL OK",    "count": 1, "color": "#16a34a", "asset_ids": ["uuid2"]},
        {"status": "no_data",  "label": "Sin datos", "count": 0, "color": "#94a3b8", "asset_ids": []}
      ]
    }
    // ... resto de tipos
  ],
  "compliance": [
    {
      "indicator": "edr",
      "label": "EDR",
      "segments": [
        {"status": "ok",               "label": "Activo",         "count": 6, "color": "#16a34a", "asset_ids": [...]},
        {"status": "ko_with_exception","label": "Con excepción",  "count": 4, "color": "#1d4ed8", "asset_ids": [...]},
        {"status": "ko",               "label": "Sin instalar",   "count": 0, "color": "#dc2626", "asset_ids": [...]}
      ]
    }
    // ... 5 más: mon, siem, logs, bck, bckcl
  ],
  "backup": {
    "local": {
      "label": "Backup Local",
      "segments": [
        {"status": "ok",      "label": "Con backup",  "count": 5, "color": "#16a34a", "asset_ids": [...]},
        {"status": "missing", "label": "Sin backup",  "count": 5, "color": "#dc2626", "asset_ids": [...]}
      ]
    },
    "cloud": { ... }
  },
  "certificates": {
    "segments": [
      {"status": "valid",    "label": "Válidos",       "count": 2, "color": "#16a34a", "cert_ids": [...]},
      {"status": "expiring", "label": "Próximos",      "count": 1, "color": "#d97706", "cert_ids": [...]},
      {"status": "critical", "label": "Críticos",      "count": 1, "color": "#f97316", "cert_ids": [...]},
      {"status": "expired",  "label": "Expirados",     "count": 1, "color": "#dc2626", "cert_ids": [...]}
    ]
  }
}
```

### Notas de implementación
- Los asset_ids permiten al frontend construir el enlace de filtro al inventario
- Para compliance: cruzar con active_exceptions para determinar ok/ko_with_exception/ko
- Para EOL: buscar en asset.tags los nombres "EOL KO", "EOL WARN", "EOL OK"
