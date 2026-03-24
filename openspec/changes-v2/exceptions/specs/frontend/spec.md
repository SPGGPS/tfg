# Frontend Spec — Compliance Exceptions

## ComplianceBadge.jsx — funciones exportadas

```js
getComplianceState(indicator, asset, excMap) → "ok"|"ok_with_exception"|"ko_with_exception"|"ko"
getBadgeClass(state) → string de clases CSS
getTagComplianceClass(tagName, asset, excMap) → clases para TagBadge con compliance
```

## Lógica getComplianceState
```js
const ok  = asset[INDICATOR_FIELD[indicator]]  // campo booleano o fecha del asset
const exc = excMap[indicator]                  // excepción activa del indicador
if (ok && exc)  return "ok_with_exception"
if (ok)         return "ok"
if (exc)        return "ko_with_exception"
return "ko"
```

## Clases CSS por estado
```js
ok:                "bg-green-900/60 text-green-300 border-green-700"
ok_with_exception: "compliance-gradient text-white border-blue-600"      // azul→verde
ko_with_exception: "compliance-gradient-temp text-white border-red-700"  // azul→rojo
ko:                "bg-red-900/60 text-red-300 border-red-700"
```

## MultiAssetSelector (en ExceptionsPage)
- NO es un dropdown. Es una lista flat con checkboxes.
- Checkbox cabecera "Seleccionar todos (N)"
- Cada fila: <label> + checkbox + nombre + badge tipo + IP
- Assets con excepción activa para ese indicador: opacity-40 cursor-not-allowed
- Búsqueda: input texto arriba filtra por nombre
- Carga 100 assets al montarse (enabled: !!indicator)

## Bulk delete en tabla de excepciones
- Checkbox en cada fila + checkbox cabecera
- Botón "Revocar seleccionadas (N)" → confirm() → DELETE en serie
- Ordenación client-side: estado sortBy/sortDir + SortTh component
