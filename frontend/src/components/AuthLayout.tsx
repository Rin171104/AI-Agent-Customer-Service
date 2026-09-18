import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../services/auth'

export default function AuthLayout() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  if (user) {
    return <Navigate to={user.role === 'OWNER' ? '/owner' : '/customer'} replace />
  }

  return <Outlet />
}
