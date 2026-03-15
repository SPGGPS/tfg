import { Link, Outlet } from 'react-router-dom'
import { HardDrive, Tag, Shield } from 'lucide-react'

export default function Layout() {
  // TODO: obtener roles del contexto de autenticación
  const userRoles = JSON.parse(sessionStorage.getItem('tfg_user_roles') || '["viewer"]')
  const isAdmin = userRoles.includes('admin')

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-800">TFG - CMDB</h1>
          <div className="text-sm text-gray-500">
            Rol: {userRoles.join(', ')}
          </div>
        </div>
      </header>
      <aside className="fixed left-0 top-14 bottom-0 w-56 bg-white border-r border-gray-200 p-4">
        <nav className="space-y-1">
          <Link to="/" className="flex items-center gap-2 px-3 py-2 rounded-md bg-gray-100 text-gray-900 font-medium">
            <HardDrive className="w-4 h-4" />
            Inventario
          </Link>
          <Link to="/tags" className="flex items-center gap-2 px-3 py-2 rounded-md text-gray-600 hover:bg-gray-50">
            <Tag className="w-4 h-4" />
            Etiquetas
          </Link>
          {isAdmin && (
            <Link to="/audit" className="flex items-center gap-2 px-3 py-2 rounded-md text-gray-600 hover:bg-gray-50">
              <Shield className="w-4 h-4" />
              Auditoría
            </Link>
          )}
        </nav>
      </aside>
      <main className="ml-56 pt-14 p-6">
        <Outlet />
      </main>
    </div>
  )
}
