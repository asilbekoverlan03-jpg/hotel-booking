import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { getBookings, cancelBooking } from '../api/hotels'

// Метка статуса бронирования
const STATUS_LABELS = {
  pending: { label: 'Ожидает', cls: 'badge-warning' },
  confirmed: { label: 'Подтверждено', cls: 'badge-success' },
  cancelled: { label: 'Отменено', cls: 'badge-danger' },
  completed: { label: 'Завершено', cls: 'badge-info' },
}

export default function MyBookingsPage() {
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [cancellingId, setCancellingId] = useState(null)

  // Сообщение об успешном создании брони (из BookingPage)
  const location = useLocation()
  const justCreated = location.state?.success

  useEffect(() => {
    fetchBookings()
  }, [])

  const fetchBookings = async () => {
    setLoading(true)
    try {
      const { data } = await getBookings()
      setBookings(data.results)
    } catch {
      setError('Не удалось загрузить бронирования.')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (id) => {
    if (!window.confirm('Отменить бронирование?')) return
    setCancellingId(id)
    try {
      const { data } = await cancelBooking(id)
      // Обновляем статус в списке без перезагрузки
      setBookings((prev) => prev.map((b) => (b.id === id ? data : b)))
    } catch {
      alert('Не удалось отменить бронирование.')
    } finally {
      setCancellingId(null)
    }
  }

  if (loading) return <div className="loading">Загрузка...</div>

  return (
    <div className="page">
      <h1>Мои бронирования</h1>

      {justCreated && <div className="success-msg">✓ Бронирование успешно создано!</div>}
      {error && <div className="error-msg">{error}</div>}

      {bookings.length === 0 ? (
        <p>У вас пока нет бронирований.</p>
      ) : (
        <div className="bookings-list">
          {bookings.map((b) => {
            const statusInfo = STATUS_LABELS[b.status] || { label: b.status, cls: '' }
            return (
              <div key={b.id} className="booking-card">
                <div className="booking-card-header">
                  <h3>{b.room_detail?.hotel?.name || 'Отель'} — Номер #{b.room_detail?.room_number}</h3>
                  <span className={`badge ${statusInfo.cls}`}>{statusInfo.label}</span>
                </div>
                <div className="booking-card-details">
                  <p>📅 {b.check_in} → {b.check_out}</p>
                  <p>🌙 Ночей: {b.nights}</p>
                  <p>👥 Гостей: {b.guests_count}</p>
                  <p>💰 Итого: <strong>{parseFloat(b.total_price).toLocaleString('ru-RU')} ₽</strong></p>
                  <p>Тип: {b.room_detail?.room_type?.name_display || '—'}</p>
                </div>
                {(b.status === 'pending' || b.status === 'confirmed') && (
                  <button
                    className="btn-danger"
                    onClick={() => handleCancel(b.id)}
                    disabled={cancellingId === b.id}
                  >
                    {cancellingId === b.id ? 'Отменяю...' : 'Отменить'}
                  </button>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
