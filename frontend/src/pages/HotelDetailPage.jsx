import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getHotel, createReview } from '../api/hotels'
import { useAuth } from '../context/AuthContext'

function Stars({ count }) {
  return <span className="stars">{'★'.repeat(count)}{'☆'.repeat(5 - count)}</span>
}

export default function HotelDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()

  const [hotel, setHotel] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Форма отзыва
  const [reviewForm, setReviewForm] = useState({ stars: 5, comment: '' })
  const [reviewError, setReviewError] = useState('')
  const [reviewSuccess, setReviewSuccess] = useState(false)
  const [reviewLoading, setReviewLoading] = useState(false)

  useEffect(() => {
    loadHotel()
  }, [id])

  const loadHotel = async () => {
    setLoading(true)
    try {
      const { data } = await getHotel(id)
      setHotel(data)
    } catch {
      setError('Отель не найден.')
    } finally {
      setLoading(false)
    }
  }

  const handleReviewSubmit = async (e) => {
    e.preventDefault()
    setReviewError('')
    setReviewLoading(true)
    try {
      await createReview({ hotel: parseInt(id), ...reviewForm })
      setReviewSuccess(true)
      setReviewForm({ stars: 5, comment: '' })
      loadHotel() // перезагружаем чтобы отзыв появился
    } catch (err) {
      const data = err.response?.data
      // Выводим первую ошибку из ответа
      const msg = data?.non_field_errors?.[0] || data?.detail || JSON.stringify(data)
      setReviewError(msg || 'Ошибка при отправке отзыва.')
    } finally {
      setReviewLoading(false)
    }
  }

  if (loading) return <div className="loading">Загрузка...</div>
  if (error) return <div className="error-msg">{error}</div>
  if (!hotel) return null

  const photoUrl = hotel.photo
    ? (hotel.photo.startsWith('http') ? hotel.photo : `http://127.0.0.1:8002${hotel.photo}`)
    : null

  return (
    <div className="page">
      {/* Шапка отеля */}
      <div className="hotel-detail-header">
        {photoUrl && <img src={photoUrl} alt={hotel.name} className="hotel-detail-photo" />}
        <div className="hotel-detail-info">
          <h1>{hotel.name}</h1>
          <p className="hotel-card-location">📍 {hotel.address}, {hotel.city}, {hotel.country}</p>
          <Stars count={hotel.stars} />
          <div className="hotel-card-meta" style={{ marginTop: '8px' }}>
            {hotel.avg_rating && <span className="badge badge-rating">⭐ {hotel.avg_rating}</span>}
            {hotel.has_wifi && <span className="badge">Wi-Fi</span>}
            {hotel.has_parking && <span className="badge">Парковка</span>}
          </div>
          {hotel.description && <p className="hotel-description">{hotel.description}</p>}
        </div>
      </div>

      {/* Список номеров */}
      <section className="section">
        <h2>Номера</h2>
        {hotel.rooms.length === 0 ? (
          <p>Номеров пока нет.</p>
        ) : (
          <div className="rooms-grid">
            {hotel.rooms.map((room) => (
              <div key={room.id} className={`room-card ${!room.is_available ? 'room-unavailable' : ''}`}>
                <div className="room-card-header">
                  <span>№ {room.room_number}</span>
                  {room.room_type && <span className="badge">{room.room_type.name_display}</span>}
                  {!room.is_available && <span className="badge badge-danger">Занят</span>}
                </div>
                <p className="room-price">{parseFloat(room.price_per_night).toLocaleString('ru-RU')} ₽/ночь</p>
                <p>👥 До {room.capacity} гостей</p>
                {room.description && <p className="room-desc">{room.description}</p>}
                {room.is_available && (
                  <Link to={`/booking/${room.id}`} className="btn-primary">Забронировать</Link>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Отзывы */}
      <section className="section">
        <h2>Отзывы ({hotel.reviews.length})</h2>
        {hotel.reviews.length === 0 ? (
          <p>Отзывов пока нет. Будьте первым!</p>
        ) : (
          <div className="reviews-list">
            {hotel.reviews.map((r) => (
              <div key={r.id} className="review-card">
                <div className="review-header">
                  <strong>{r.user.username}</strong>
                  <Stars count={r.stars} />
                  <span className="review-date">{new Date(r.created_date).toLocaleDateString('ru-RU')}</span>
                </div>
                {r.comment && <p>{r.comment}</p>}
              </div>
            ))}
          </div>
        )}

        {/* Форма отзыва — только для авторизованных */}
        {user ? (
          <div className="review-form-wrap">
            <h3>Оставить отзыв</h3>
            {reviewSuccess && <div className="success-msg">Отзыв успешно добавлен!</div>}
            {reviewError && <div className="error-msg">{reviewError}</div>}
            <form onSubmit={handleReviewSubmit} className="form">
              <label>
                Оценка
                <select
                  value={reviewForm.stars}
                  onChange={(e) => setReviewForm((p) => ({ ...p, stars: parseInt(e.target.value) }))}
                >
                  {[5, 4, 3, 2, 1].map((s) => (
                    <option key={s} value={s}>{s} ★</option>
                  ))}
                </select>
              </label>
              <label>
                Комментарий
                <textarea
                  value={reviewForm.comment}
                  onChange={(e) => setReviewForm((p) => ({ ...p, comment: e.target.value }))}
                  rows={3}
                  placeholder="Расскажите о своём опыте..."
                />
              </label>
              <button type="submit" className="btn-primary" disabled={reviewLoading}>
                {reviewLoading ? 'Отправляю...' : 'Отправить отзыв'}
              </button>
            </form>
          </div>
        ) : (
          <p><Link to="/login">Войдите</Link>, чтобы оставить отзыв.</p>
        )}
      </section>
    </div>
  )
}
