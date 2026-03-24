# Frontend Spec — Inventory Master

## InventoryPage (pages/InventoryPage.jsx)

### Tabs en cabecera
```jsx
const tabs = [
  {to: "/", label: "Inventario"},
  {to: "/certificates", label: "Certificados 🔒"}
]
// Tab activo: border-red-600 text-red-700 font-semibold -mb-px
// Tab inactivo: border-transparent text-gray-500 hover:text-gray-700
```

### Tabla
- Cada <tr>: className="table-row-alt transition-colors ${selected ? 'selected' : ''}"
- Columnas: checkbox | Nombre | IPs | Tipo | Vendor | Fuente | Compliance | Backup | Etiquetas
- Nombre: <Link to={/assets/${id}}> clickable

### Compliance badges
Usar <ComplianceSummary asset={a} /> que renderiza los 6 indicadores con getBadgeClass().

### Ordenación
Estado: sortBy + sortOrder. Click en ColHead → alterna asc/desc.
Icono SortIcon muestra ↑ o ↓ según estado.

### Bulk tags
Checkboxes por fila. Botón "Asignar etiquetas (N)" visible cuando selected.size > 0.
Modal con lista de etiquetas manuales disponibles.

### Historificación
Select de snapshot → llama a GET /v1/assets?as_of=datetime. Botón "Volver a Live".

### TanStack Query
```jsx
const { data, isLoading } = useQuery({
  queryKey: ["assets", params],
  queryFn: () => assetsApi.list(params),
})
```
Invalidar con: queryClient.invalidateQueries({ queryKey: ["assets"], exact: false })
