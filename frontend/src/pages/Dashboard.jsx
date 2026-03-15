import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Search,
  Filter,
  Tag,
  Shield,
  HardDrive,
  Wifi,
  Server,
  Router,
  CheckCircle,
  XCircle,
  Clock,
  Users
} from 'lucide-react'
import { api } from '../services/api'

const typeIcons = {
  server_physical: Server,
  server_virtual: Server,
  switch: Router,
  router: Router,
  ap: Wifi
}

const typeLabels = {
  server_physical: 'Servidor Físico',
  server_virtual: 'Servidor Virtual',
  switch: 'Switch',
  router: 'Router',
  ap: 'Access Point'
}

export default function Dashboard() {
  const [filters, setFilters] = useState({
    type: '',
    vendor: '',
    source: '',
    search: '',
    tagId: ''
  })
  const [selectedAssets, setSelectedAssets] = useState([])
  const [showTagModal, setShowTagModal] = useState(false)

  const queryClient = useQueryClient()

  // Query para obtener assets
  const { data: assetsData, isLoading: assetsLoading } = useQuery({
    queryKey: ['assets', filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })
      const response = await api.get(`/assets?${params}`)
      return response.data
    }
  })

  // Query para obtener tags
  const { data: tagsData } = useQuery({
    queryKey: ['tags'],
    queryFn: () => api.get('/tags').then(res => res.data)
  })

  // Mutation para asignar tags masivamente
  const bulkTagMutation = useMutation({
    mutationFn: (data) => api.post('/assets/bulk-tags', data),
    onSuccess: () => {
      queryClient.invalidateQueries(['assets'])
      setSelectedAssets([])
      setShowTagModal(false)
    }
  })

  const assets = assetsData?.items || []
  const tags = tagsData?.items || []

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleBulkTag = async (tagIds) => {
    if (selectedAssets.length === 0) return

    await bulkTagMutation.mutateAsync({
      asset_ids: selectedAssets,
      tag_ids: tagIds
    })
  }

  const getComplianceBadge = (asset) => {
    const checks = [
      { key: 'edr_installed', label: 'EDR' },
      { key: 'monitored', label: 'Mon' },
      { key: 'logs_enabled', label: 'Logs' }
    ]

    const passed = checks.filter(check => asset[check.key]).length
    const total = checks.length

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        passed === total ? 'bg-green-100 text-green-800' :
        passed >= total/2 ? 'bg-yellow-100 text-yellow-800' :
        'bg-red-100 text-red-800'
      }`}>
        {passed}/{total} OK
      </span>
    )
  }

  const getBackupStatus = (lastBackup) => {
    if (!lastBackup) return <XCircle className="w-4 h-4 text-red-500" />

    const hours = (new Date() - new Date(lastBackup)) / (1000 * 60 * 60)
    return hours < 24 ?
      <CheckCircle className="w-4 h-4 text-green-500" /> :
      <Clock className="w-4 h-4 text-yellow-500" />
  }

  if (assetsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Inventario de Activos</h2>
        <div className="flex gap-2">
          {selectedAssets.length > 0 && (
            <button
              onClick={() => setShowTagModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Tag className="w-4 h-4" />
              Asignar Etiquetas ({selectedAssets.length})
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Nombre o IP..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="pl-10 w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Todos</option>
              <option value="server_physical">Servidor Físico</option>
              <option value="server_virtual">Servidor Virtual</option>
              <option value="switch">Switch</option>
              <option value="router">Router</option>
              <option value="ap">Access Point</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Vendor</label>
            <input
              type="text"
              placeholder="Fabricante..."
              value={filters.vendor}
              onChange={(e) => handleFilterChange('vendor', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fuente</label>
            <select
              value={filters.source}
              onChange={(e) => handleFilterChange('source', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Todas</option>
              <option value="VMware">VMware</option>
              <option value="ServiceNow">ServiceNow</option>
              <option value="EDR">EDR</option>
              <option value="Monitorización">Monitorización</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Etiqueta</label>
            <select
              value={filters.tagId}
              onChange={(e) => handleFilterChange('tagId', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Todas</option>
              {tags.map(tag => (
                <option key={tag.id} value={tag.id}>{tag.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Assets Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedAssets(assets.map(a => a.id))
                      } else {
                        setSelectedAssets([])
                      }
                    }}
                    checked={selectedAssets.length === assets.length && assets.length > 0}
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Activo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IPs
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cumplimiento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Backup
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Etiquetas
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {assets.map((asset) => {
                const TypeIcon = typeIcons[asset.type] || Server
                return (
                  <tr key={asset.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedAssets.includes(asset.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedAssets(prev => [...prev, asset.id])
                          } else {
                            setSelectedAssets(prev => prev.filter(id => id !== asset.id))
                          }
                        }}
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <TypeIcon className="w-5 h-5 text-gray-400 mr-2" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">{asset.name}</div>
                          <div className="text-sm text-gray-500">{asset.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{typeLabels[asset.type]}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {asset.ips?.slice(0, 2).join(', ')}
                        {asset.ips?.length > 2 && ` +${asset.ips.length - 2} más`}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {asset.vendor}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getComplianceBadge(asset)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getBackupStatus(asset.last_backup)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-wrap gap-1">
                        {asset.tags?.map(tag => (
                          <span
                            key={tag.id}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                            style={{
                              backgroundColor: tag.color_code + '20',
                              color: tag.color_code,
                              border: `1px solid ${tag.color_code}40`
                            }}
                          >
                            {tag.name}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {assets.length === 0 && (
          <div className="text-center py-12">
            <Server className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No hay activos</h3>
            <p className="mt-1 text-sm text-gray-500">
              No se encontraron activos con los filtros aplicados.
            </p>
          </div>
        )}
      </div>

      {/* Modal para asignar tags */}
      {showTagModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-medium mb-4">Asignar Etiquetas</h3>
            <p className="text-sm text-gray-600 mb-4">
              Selecciona las etiquetas a asignar a {selectedAssets.length} activo(s):
            </p>

            <div className="space-y-2 mb-6">
              {tags.filter(tag => tag.origin === 'manual').map(tag => (
                <label key={tag.id} className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2"
                    onChange={(e) => {
                      // Aquí iría la lógica para seleccionar tags
                    }}
                  />
                  <span
                    className="px-2 py-1 rounded text-sm"
                    style={{
                      backgroundColor: tag.color_code + '20',
                      color: tag.color_code
                    }}
                  >
                    {tag.name}
                  </span>
                </label>
              ))}
            </div>

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowTagModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleBulkTag([])} // TODO: pasar los tags seleccionados
                disabled={bulkTagMutation.isLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {bulkTagMutation.isLoading ? 'Asignando...' : 'Asignar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
