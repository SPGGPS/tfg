# Design: Branding Corporativo

## Paleta de colores

```js
// tailwind.config.js
primary: {
  DEFAULT: "#C8001D",   // rojo principal — sidebar, botones, focus, scrollbar
  hover:   "#A8001A",
  dark:    "#8B0016",
  light:   "#FDECEA",   // fondo tenue para selecciones
}
```

## Tema claro — superficies
| Elemento | Color |
|---------|-------|
| Body | #FDF7F7 (blanco con tinte rojo muy leve) |
| Cards | #FFFFFF con borde #EED8D8 |
| Inputs | #FFFBFB con borde #E8CCCC |
| Filas pares | #FFF8F8 |
| Filas hover | #FFEEEE |
| Filas selected | #FFE0E0 + border-left 3px #C8001D |

## Compliance — colores semánticos (NO tocar)
Los gradientes de compliance usan azul #1d4ed8 que representa "hay excepción".
NO es el rojo corporativo y NO debe cambiarse.
```css
.compliance-gradient      { background: linear-gradient(135deg, #1d4ed8 50%, #15803d 50%); }
.compliance-gradient-temp { background: linear-gradient(135deg, #1d4ed8 50%, #991b1b 50%); }
```

## TagBadge
```js
style = {
  backgroundColor: tag.color_code + "18",  // 9% opacidad
  color: tag.color_code,                    // texto sólido del color
  borderColor: tag.color_code,              // borde sólido
  border: "1px solid",
  fontWeight: "600"
}
```

## AssetTypeBadge — pasteles claros
```js
server_physical: "bg-slate-100 text-slate-700 border border-slate-300"
server_virtual:  "bg-violet-100 text-violet-700 border border-violet-300"
switch:          "bg-sky-100 text-sky-700 border border-sky-300"
router:          "bg-amber-100 text-amber-700 border border-amber-300"
ap:              "bg-emerald-100 text-emerald-700 border border-emerald-300"
database:        "bg-cyan-100 text-cyan-700 border border-cyan-300"
```

## Nota sobre el hex exacto
#C8001D es aproximación visual de ssreyes.org. Si el hex oficial difiere,
cambiar solo primary.DEFAULT en tailwind.config.js y #C8001D en index.css.
