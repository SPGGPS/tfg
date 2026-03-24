# Tasks: Branding

## 1. Tailwind config
- [x] 1.1 Definir primary: {DEFAULT: "#C8001D", hover, dark, light}
- [x] 1.2 Definir corporate y surface tokens

## 2. index.css — clases globales
- [x] 2.1 body: background #FDF7F7, color #2D1515
- [x] 2.2 .btn-primary: #C8001D, hover #A8001A
- [x] 2.3 .btn-secondary: background #FFF0F0, borde #F0CCCC, texto #8B0016
- [x] 2.4 .card: blanco, borde #EED8D8, shadow rojo tenue
- [x] 2.5 .input: #FFFBFB, borde #E8CCCC, focus borde #C8001D
- [x] 2.6 .sidebar-item y .sidebar-active
- [x] 2.7 .table-row-alt: even #FFF8F8, hover #FFEEEE, selected #FFE0E0
- [x] 2.8 Scrollbar: track #F5EDED, thumb rgba(200,0,29,0.35)
- [x] 2.9 Compliance gradients: semanticos, NO rojo corporativo

## 3. Layout
- [x] 3.1 Sidebar: degradado linear-gradient(180deg, #A8001A 0%, #C8001D 100%)
- [x] 3.2 Logo: <img src="/logo-ssreyes.png" style={{filter:"brightness(0) invert(1)"}}/>
- [x] 3.3 Topbar: #A8001A, borde inferior #8B0016
- [x] 3.4 Subtítulo "Inventario Centralizado": color #FFB3B3 (rosa claro sobre rojo)

## 4. Componentes
- [x] 4.1 TagBadge: color sólido, fondo 9% opacidad, fontWeight 600
- [x] 4.2 AssetTypeBadge: pasteles claros (slate/violet/sky/amber/emerald/cyan)
- [x] 4.3 IndicatorBadge: pasteles claros
- [x] 4.4 Tabs activos: border-red-600 text-red-700 font-semibold
- [x] 4.5 Tabs inactivos: text-gray-500 hover:text-gray-700

## 5. Correcciones de contraste finales
- [x] 5.1 colorBadgeStyle v4: rgba() fondo 12% + texto darkened 62% + borde 45%
- [x] 5.2 getBadgeClass: dark-mode → light-mode (green-100/red-100 con text-800)
- [x] 5.3 Localizaciones: zone=#FEF2F2, site=#F3F4F6, cell=blanco, border=#E5E7EB
- [x] 5.4 ExceptionsPage banner: bg-blue-950/20 → #EFF6FF con text-blue-800
- [x] 5.5 CertificatesPage: todos los colores dark-mode → light-mode
- [x] 5.6 colorBadgeStyle usa siempre rgba() para compatibilidad garantizada
