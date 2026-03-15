import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2, Tag as TagIcon } from 'lucide-react'
import { tagsApi } from '../services/api'

export default function Tags() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingTag, setEditingTag] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    color_code: '#3B82F6',
    description: ''
  })

  const queryClient = useQueryClient()

  const { data: tagsData, isLoading } = useQuery({
    queryKey: ['tags'],
    queryFn: () => tagsApi.getTags()
  })

  const createMutation = useMutation({
    mutationFn: tagsApi.createTag,
    onSuccess: () => {
      queryClient.invalidateQueries(['tags'])
      setShowCreateModal(false)
      resetForm()
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => tagsApi.updateTag(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['tags'])
      setEditingTag(null)
      resetForm()
    }
  })

  const deleteMutation = useMutation({
    mutationFn: tagsApi.deleteTag,
    onSuccess: () => {
      queryClient.invalidateQueries(['tags'])
    }
  })

  const tags = tagsData?.data?.items || []

  const resetForm = () => {
    setFormData({ name: '', color_code: '#3B82F6', description: '' })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (editingTag) {
      await updateMutation.mutateAsync({ id: editingTag.id, data: formData })
    } else {
      await createMutation.mutateAsync(formData)
    }
  }

  const handleEdit = (tag) => {
    setEditingTag(tag)
    setFormData({
      name: tag.name,
      color_code: tag.color_code,
      description: tag.description || ''
    })
  }

  const handleDelete = async (tag) => {
    if (window.confirm(`¿Eliminar la etiqueta "${tag.name}"? Se desvinculará de ${tag.asset_count || 0} activos.`)) {
      await deleteMutation.mutateAsync(tag.id)
    }
  }

  if (isLoading) {
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
        <h2 className="text-2xl font-bold text-gray-900">Gestión de Etiquetas</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Nueva Etiqueta
        </button>
      </div>

      {/* Tags Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tags.map((tag) => (
          <div key={tag.id} className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded-full border-2 border-white shadow-sm"
                  style={{ backgroundColor: tag.color_code }}
                />
                <h3 className="font-medium text-gray-900">{tag.name}</h3>
              </div>
              <div className="flex gap-1">
                <button
                  onClick={() => handleEdit(tag)}
                  className="text-gray-400 hover:text-blue-600 p-1"
                  disabled={tag.origin === 'system'}
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(tag)}
                  className="text-gray-400 hover:text-red-600 p-1"
                  disabled={tag.origin === 'system'}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {tag.description && (
              <p className="text-sm text-gray-600 mb-3">{tag.description}</p>
            )}

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span className={`px-2 py-1 rounded ${
                tag.origin === 'system' ? 'bg-gray-100 text-gray-800' : 'bg-blue-100 text-blue-800'
              }`}>
                {tag.origin === 'system' ? 'Sistema' : 'Manual'}
              </span>
              <span>{tag.asset_count || 0} activos</span>
            </div>
          </div>
        ))}
      </div>

      {tags.length === 0 && (
        <div className="text-center py-12">
          <TagIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No hay etiquetas</h3>
          <p className="mt-1 text-sm text-gray-500">
            Crea tu primera etiqueta para organizar los activos.
          </p>
        </div>
      )}

      {/* Create/Edit Modal */}
      {(showCreateModal || editingTag) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-medium mb-4">
              {editingTag ? 'Editar Etiqueta' : 'Nueva Etiqueta'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Nombre de la etiqueta"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Color
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={formData.color_code}
                    onChange={(e) => setFormData(prev => ({ ...prev, color_code: e.target.value }))}
                    className="w-12 h-8 border border-gray-300 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={formData.color_code}
                    onChange={(e) => setFormData(prev => ({ ...prev, color_code: e.target.value }))}
                    className="flex-1 border border-gray-300 rounded-md px-3 py-2 font-mono text-sm"
                    placeholder="#3B82F6"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  rows={3}
                  placeholder="Descripción opcional..."
                />
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false)
                    setEditingTag(null)
                    resetForm()
                  }}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isLoading || updateMutation.isLoading}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {createMutation.isLoading || updateMutation.isLoading ?
                    'Guardando...' :
                    (editingTag ? 'Actualizar' : 'Crear')
                  }
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}