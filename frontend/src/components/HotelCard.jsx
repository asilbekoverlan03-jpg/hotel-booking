import { Link } from 'react-router-dom'

// Отображает звёзды отеля как unicode-символы
function Stars({ count }) {
  return (
    <span className="stars" title={`${count} звёзд`}>
      {'★'.repeat(count)}{'☆'.repeat(5 - count)}
    </span>
  )
}

export default function HotelCard({ hotel }) {
  const photoUrl = hotel.photo
    ? (hotel.photo.startsWith('http') ? hotel.photo : `http://127.0.0.1:8002${hotel.photo}`)
    : null

  return (
    <div className="hotel-card">
      <div className="hotel-card-photo">
        {photoUrl
          ? <img src={photoUrl} alt={hotel.name} />
          : <div className="hotel-card-no-photo">🏨</div>
        }
      </div>
      <div className="hotel-card-body">
        <h3>{hotel.name}</h3>
        <p className="hotel-card-location">📍 {hotel.city}, {hotel.country}</p>
        <Stars count={hotel.stars} />
        <div className="hotel-card-meta">
          {hotel.avg_rating && (
            <span className="badge badge-rating">⭐ {hotel.avg_rating}</span>
          )}
          {hotel.has_wifi && <span className="badge">Wi-Fi</span>}
          {hotel.has_parking && <span className="badge">Парковка</span>}
        </div>
        {hotel.min_price && (
          <p className="hotel-card-price">от {hotel.min_price.toLocaleString('ru-RU')} ₽/ночь</p>
        )}
        <Link to={`/hotels/${hotel.id}`} className="btn-primary">Подробнее</Link>
      </div>
    </div>
  )
}
