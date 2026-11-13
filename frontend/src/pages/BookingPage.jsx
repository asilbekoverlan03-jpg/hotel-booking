import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getRooms, createBooking } from '../api/hotels'

export default function BookingPage() {
  const { roomId } = useParams()
  const navigate = useNavigate()

  const [room, setRoom] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState({})
  const [globalError, setGlobalError] = useState('')

  const today = new Date().toISOString().split('T')[0]
  const [form, setForm] = useState({
    check_in: '',
    check_out: '',
    guests_count: 1,
  })

  useEffect(() => {
    getRooms({ hotel: undefined })
      .then(({ data }) => {
        const found = data.results.find((r) => r.id === parseInt(roomId))
        setRoom(found || null)
      })
      .catch(() => setGlobalError('Не удалось загрузить информацию о номере.'))
      .finally(() => setLoading(false))
  }, [roomId])

  // Вычисляем ночи и итоговую цену на лету
  const nights =
    form.check_in && form.check_out
      ? Math.max(
          0,
          Math.round(
            (new Date(form.check_out) - new Date(form.check_in)) / 86400000
          )
        )
      : 0

  const totalPrice = room ? nights * parseFloat(room.price_per_night) : 0

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
    setErrors((prev) => ({ ...prev, [name]: '' }))
    setGlobalError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setErrors({})
    setGlobalError('')

    try {
      await createBooking({
        room: parseInt(roomId),
        check_in: form.check_in,
        check_out: form.check_out,
        guests_count: parseInt(form.guests_count),
      })
      navigate('/bookings', { state: { success: true } })
    } catch (err) {
      const data = err.response?.data
      if (data) {
        // Разбираем ошибки валидации с бэкенда по полям
        const fieldErrors = {}
        Object.entries(data).forEach(([key, val]) => {
          fieldErrors[key] = Array.isArray(val) ? val[0] : val
        })
        setErrors(fieldErrors)
        setGlobalError(fieldErrors.non_field_errors || '')
      } else {
        setGlobalError('Ошибка при создании бронирования.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="loading">Загрузка...</div>
  if (!room) return <div className="error-msg">Номер не найден.</div>

  return (
    <div className="page page-narrow">
      <h1>Бронирование номера</h1>

      {/* Краткая информация о номере */}
      <div className="booking-room-info">
        <h3>№ {room.room_number} — {room.room_type?.name_display || 'Стандарт'}</h3>
        <p>{parseFloat(room.price_per_night).toLocaleString('ru-RU')} ₽/ночь · до {room.capacity} гостей</p>
        {room.description && <p>{room.description}</p>}
      </div>

      {globalError && <div className="error-msg">{globalError}</div>}

      <form onSubmit={handleSubmit} className="form">
        <label>
          Дата заезда
          <input
            type="date"
            name="check_in"
            value={form.check_in}
            min={today}
            onChange={handleChange}
            required
          />
          {errors.check_in && <span className="field-error">{errors.check_in}</span>}
        </label>

        <label>
          Дата выезда
          <input
            type="date"
            name="check_out"
            value={form.check_out}
            min={form.check_in || today}
            onChange={handleChange}
            required
          />
          {errors.check_out && <span className="field-error">{errors.check_out}</span>}
        </label>

        <label>
          Количество гостей
          <input
            type="number"
            name="guests_count"
            value={form.guests_count}
            min={1}
            max={room.capacity}
            onChange={handleChange}
            required
          />
          {errors.guests_count && <span className="field-error">{errors.guests_count}</span>}
        </label>

        {/* Предварительный расчёт стоимости */}
        {nights > 0 && (
          <div className="booking-summary">
            <p>🌙 Ночей: <strong>{nights}</strong></p>
            <p>💰 Итого: <strong>{totalPrice.toLocaleString('ru-RU')} ₽</strong></p>
          </div>
        )}

        <button type="submit" className="btn-primary" disabled={submitting || nights === 0}>
          {submitting ? 'Бронирую...' : 'Подтвердить бронирование'}
        </button>
      </form>
    </div>
  )
}
