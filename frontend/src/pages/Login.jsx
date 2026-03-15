import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

/**
 * Login - primera versión: simula login local.
 * Siguiente iteración: flujo OIDC + PKCE contra Keycloak.
 */
export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState('')

  const from = location.state?.from?.pathname || '/'

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    // Simulación: cualquier usuario/pass para desarrollo
    sessionStorage.setItem('tfg_authenticated', 'true')
    navigate(from, { replace: true })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Iniciar sesión</h2>
        <p className="text-sm text-gray-500 mb-4">
          Primera versión: uso simulado. Próximamente Keycloak (OIDC + PKCE).
        </p>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="user" className="block text-sm font-medium text-gray-700 mb-1">
              Usuario
            </label>
            <input
              id="user"
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="usuario"
              autoComplete="username"
            />
          </div>
          <div className="mb-4">
            <label htmlFor="pass" className="block text-sm font-medium text-gray-700 mb-1">
              Contraseña
            </label>
            <input
              id="pass"
              type="password"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>
          {error && <p className="text-sm text-red-600 mb-2">{error}</p>}
          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
          >
            Entrar
          </button>
        </form>
      </div>
    </div>
  )
}
