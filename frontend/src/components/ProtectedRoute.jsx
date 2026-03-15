import { Navigate, useLocation } from 'react-router-dom'

/**
 * Protección de rutas por autenticación y roles.
 * Redirige a /login si no hay token, o muestra error si no tiene roles requeridos.
 */
export default function ProtectedRoute({ children, requiredRoles = [] }) {
  const location = useLocation()
  // TODO: integrar con Keycloak/OIDC y leer roles del JWT
  const isAuthenticated = !!sessionStorage.getItem('tfg_authenticated')
  const userRoles = JSON.parse(sessionStorage.getItem('tfg_user_roles') || '[]')

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (requiredRoles.length > 0 && !requiredRoles.some(role => userRoles.includes(role))) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Acceso Denegado</h1>
          <p className="text-gray-600">No tienes permisos para acceder a esta página.</p>
        </div>
      </div>
    )
  }

  return children
}
