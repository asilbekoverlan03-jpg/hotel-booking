import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">🏨 HotelBooking</Link>
      </div>
      <div className="navbar-links">
        <Link to="/">Отели</Link>
        {user ? (
          <>
            <Link to="/bookings">Мои бронирования</Link>
            <Link to="/profile">Профиль</Link>
            <button onClick={handleLogout} className="btn-link">Выйти</button>
          </>
        ) : (
          <>
            <Link to="/login">Войти</Link>
            <Link to="/register" className="btn-primary-sm">Регистрация</Link>
          </>
        )}
      </div>
    </nav>
  )
}
