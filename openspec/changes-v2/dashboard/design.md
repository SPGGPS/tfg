# Design: Dashboard

## Layout

```
┌─────────────────────────────────────────────────────────┐
│ Dashboard — Inventario Centralizado          [fecha/hora]│
├─────────────────────────────────────────────────────────┤
│ KPIs: N activos | N certificados | N excepciones activas  │
├─────────────────────────────────────────────────────────┤
│ BLOQUE 1 — End of Life por tipo                          │
│ [🖥 Servidores] [💻 Virtuales] [🔀 Switches] [🗄 BDs]   │
│   (pie chart por tipo con EOL KO/WARN/OK/Sin datos)      │
├─────────────────────────────────────────────────────────┤
│ BLOQUE 2 — Compliance                                    │
│ [EDR] [MON] [SIEM] [LOGS] [BCK Local] [BCK Cloud]       │
│   (pie chart por indicador)                              │
├─────────────────────────────────────────────────────────┤
│ BLOQUE 3 — Backup                                        │
│ [Backup Local]            [Backup Cloud]                 │
├─────────────────────────────────────────────────────────┤
│ BLOQUE 4 — Certificados                                  │
│ [Por estado TLS]                                         │
└─────────────────────────────────────────────────────────┘
```

## Gráfico de sectores — especificación SVG

Implementado en SVG puro (sin librería externa), dentro de la app.
Cada gráfico es un componente `<PieChart>` reutilizable.

### Interactividad
- Hover: el sector se escala (1.05) y aparece tooltip con lista de elementos
- Tooltip: posición calculada para no salirse del viewport
- Click: navega a la página correspondiente con filtros URL

### Colores por estado EOL
- EOL KO: #dc2626 (rojo)
- EOL WARN: #d97706 (ámbar)
- EOL OK: #16a34a (verde)
- Sin datos: #94a3b8 (gris)

### Colores compliance (mismos que los badges)
- OK: #16a34a
- KO con excepción: #1d4ed8 (azul semántico)
- KO: #dc2626
- Sin datos: #94a3b8

## Decisiones

| Decisión | Rationale |
|----------|-----------|
| SVG puro | Sin dependencia de Chart.js — más control sobre la interactividad |
| Backend endpoint único /v1/dashboard | Evitar N queries desde el frontend |
| Tooltip con lista de assets | Acción rápida sin salir del dashboard |
| Click → filtro URL | Reutiliza páginas existentes con parámetros |
