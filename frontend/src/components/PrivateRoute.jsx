import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Защищённый маршрут — редиректит на /login если пользователь не авторизован.
 * Пока идёт проверка токена показываем заглушку.
 */
export default function PrivateRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) return <div className="loading">Загрузка...</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}
