# Frontend Spec — End of Life

## Ruta y acceso
- Ruta: `/eol`
- Sidebar: "End of Life" con ShieldIcon — visible a todos los roles
- Operaciones de escritura (añadir, sync, editar, borrar): solo admin

## Componentes

### EolStatusBadge({ status })
```jsx
eol:     <span className="badge bg-red-100 text-red-800 border border-red-400 font-bold">EOL</span>
warning: <span className="badge bg-amber-100 text-amber-800 border border-amber-400 font-semibold">⚠ EOL próximo</span>
ok:      <span className="badge bg-green-100 text-green-800 border border-green-400 font-semibold">✓ Soportado</span>
unknown: <span className="badge bg-gray-100 text-gray-600 border border-gray-300">Sin fecha</span>
```

### SyncBadge({ status, lastSync })
```jsx
unsynced: "badge bg-red-50 text-red-700 border border-red-300"  → "🔴 unsynced"
synced:   "badge bg-green-50 text-green-700 border border-green-400" → "✓ sync dd/MM/yy HH:mm"
```

### EolDaysCell({ eolDate, eolBoolean })
- eolBoolean=true → "Sin soporte" rojo
- days < 0 → "Expirado hace Nd" rojo
- days ≤ 365 → "⚠ Nd" ámbar
- days > 365 → "Nd (Na)" verde

## Tabla de productos (EolPage)

Columnas: Producto | Categoría | Ciclos | Estado sync | EOL / Advertencias | Acciones

Fila unsynced: `bg-red-50/60` para visibilidad.
Click en fila → abre modal ProductDetail con ciclos.
Botón 🔄 por fila (solo admin): sync del producto.
Botón ✕ por fila (solo admin): eliminar con confirm().

## ProductDetail — tabla de ciclos

Columnas: Versión | Lanzamiento | Fin soporte | EOL | Días restantes | Estado | Sync | Acción

- Versión: `font-mono font-semibold` + badge LTS (azul) + badge "custom" (violeta si hay custom_eol_date)
- EOL con custom: texto violeta + " *" para indicar que es override
- Fila unsynced: `bg-red-50/60`
- Botón "Editar": abre modal con custom_eol_date y custom_notes

## AddProductModal

1. Input búsqueda → filtra la lista de all-products de endoflife.date
2. Lista radio con scroll (max 200px): slugs en font-mono
3. Al seleccionar → muestra campos display_name, category, notes
4. Botón "+ Añadir y sincronizar" → POST /v1/eol/products/{id} + primera sync

## eolApi (services/api.js)
```js
export const eolApi = {
  allProducts:  ()          => req("/eol/all-products"),
  listProducts: ()          => req("/eol/products"),
  addProduct:   (id, data)  => req(`/eol/products/${id}`, {method:"POST", body:JSON.stringify(data||{})}),
  updateProduct:(id, data)  => req(`/eol/products/${id}`, {method:"PUT", body:JSON.stringify(data)}),
  deleteProduct:(id)        => req(`/eol/products/${id}`, {method:"DELETE"}),
  syncProduct:  (id)        => req(`/eol/products/${id}/sync`, {method:"POST"}),
  syncAll:      ()          => req("/eol/sync-all", {method:"POST"}),
  listCycles:   (id)        => req(`/eol/products/${id}/cycles`),
  updateCycle:  (pid,cid,d) => req(`/eol/products/${pid}/cycles/${cid}`, {method:"PUT", body:JSON.stringify(d)}),
  assetStatus:  ()          => req("/eol/asset-status"),
}
```

## Seed inicial (init_db.py)
4 productos con ciclos estáticos (para funcionar sin conexión a internet en dev):
- ubuntu: 24.04(ok), 22.04(ok), 20.04(warning), 18.04(eol)
- rhel: 9(ok), 8(warning), 7(eol)
- postgresql: 16(ok), 15(warning), 13(eol)
- python: 3.12(ok), 3.11(ok), 3.9(warning)

---

## EolPage — Mejoras implementadas

### Tabla principal
- Columna "Ciclos" renombrada a "Versiones"
- Badges "N EOL →" y "N próximos →" en columna EOL/Advertencias son **clicables**
  → abren modal `AssetsEolModal` filtrando assets por ese estado

### Modal al pulsar fila del producto → `ProductDetail`
- Tabla de versiones con columnas: Versión | Lanzamiento | EOL oficial | Override EOL | Días | Estado | Sync | [Editar]
- Cabecera con badges clicables de resumen (sin soporte / próximos / soportados)
  → abren modal `AssetsEolModal` interno

### Modal `AssetsEolModal`
- Se abre desde badges clicables (tabla principal y detalle de producto)
- Parámetros: productId, productName, status (eol|warning|ok)
- Llama a `GET /v1/eol/products/{product_id}/assets?status=eol|warning|ok`
- Muestra tabla: Activo | Tipo (AssetTypeBadge) | OS/Motor BD | IPs

### GET /v1/eol/products/{product_id}/assets
Filtro: `?status=eol|warning|ok` → busca assets con etiqueta EOL KO/WARN/OK
Devuelve: `[{id, name, type, ips, os, db_engine, db_version, eol_tags}]`
