import { useLocation } from 'react-router-dom'

/**
 * Hero-баннер на всю ширину экрана.
 * Отображается только на главной странице (путь "/").
 */
export default function HeroBanner() {
  const { pathname } = useLocation()

  // Показываем только на главной
  if (pathname !== '/') return null

  return (
    <div className="hero">
      <div className="hero-content">
        <h1 className="hero-title">Найдите идеальный отель</h1>
        <p className="hero-subtitle">Бронируйте номера по всему миру</p>
      </div>
    </div>
  )
}
