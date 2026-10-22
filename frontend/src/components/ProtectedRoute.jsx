import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export default function ProtectedRoute({ children, roles }) {
  const { user } = useAuth()
  if (!localStorage.getItem('hrms_token')) return <Navigate to="/login" replace />
  if (user && roles && !roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}
