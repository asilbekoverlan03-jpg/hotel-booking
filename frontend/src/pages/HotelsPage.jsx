import { useState, useEffect } from 'react'
import { getHotels } from '../api/hotels'
import HotelCard from '../components/HotelCard'

export default function HotelsPage() {
  const [hotels, setHotels] = useState([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Параметры фильтрации
  const [filters, setFilters] = useState({
    search: '',
    city: '',
    stars: '',
    has_wifi: '',
    has_parking: '',
    ordering: '',
    page: 1,
  })

  useEffect(() => {
    fetchHotels()
  }, [filters])

  const fetchHotels = async () => {
    setLoading(true)
    setError('')
    try {
      // Убираем пустые параметры перед отправкой
      const params = Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== '')
      )
      const { data } = await getHotels(params)
      setHotels(data.results)
      setCount(data.count)
    } catch {
      setError('Не удалось загрузить список отелей.')
    } finally {
      setLoading(false)
    }
  }

  const handleFilter = (e) => {
    const { name, value } = e.target
    setFilters((prev) => ({ ...prev, [name]: value, page: 1 }))
  }

  const totalPages = Math.ceil(count / 12)

  return (
    <div className="page">
      <h2 style={{ marginBottom: '16px' }}>Поиск отелей</h2>

      {/* Фильтры */}
      <div className="filters-bar">
        <input
          name="search"
          placeholder="🔍 Поиск по названию..."
          value={filters.search}
          onChange={handleFilter}
          className="filter-input"
        />
        <input
          name="city"
          placeholder="Город"
          value={filters.city}
          onChange={handleFilter}
          className="filter-input"
        />
        <select name="stars" value={filters.stars} onChange={handleFilter} className="filter-select">
          <option value="">Все звёзды</option>
          {[5, 4, 3, 2, 1].map((s) => (
            <option key={s} value={s}>{s} ★</option>
          ))}
        </select>
        <select name="has_wifi" value={filters.has_wifi} onChange={handleFilter} className="filter-select">
          <option value="">Wi-Fi: любой</option>
          <option value="true">Есть Wi-Fi</option>
          <option value="false">Нет Wi-Fi</option>
        </select>
        <select name="has_parking" value={filters.has_parking} onChange={handleFilter} className="filter-select">
          <option value="">Парковка: любая</option>
          <option value="true">Есть парковка</option>
          <option value="false">Нет парковки</option>
        </select>
        <select name="ordering" value={filters.ordering} onChange={handleFilter} className="filter-select">
          <option value="">Сортировка</option>
          <option value="-stars">Сначала 5★</option>
          <option value="stars">Сначала 1★</option>
          <option value="min_price">Дешевле</option>
          <option value="-min_price">Дороже</option>
        </select>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {loading ? (
        <div className="loading">Загрузка...</div>
      ) : (
        <>
          <p className="results-count">Найдено: {count}</p>
          <div className="hotels-grid">
            {hotels.map((h) => <HotelCard key={h.id} hotel={h} />)}
          </div>

          {/* Пагинация */}
          {totalPages > 1 && (
            <div className="pagination">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  className={`page-btn ${filters.page === p ? 'active' : ''}`}
                  onClick={() => setFilters((prev) => ({ ...prev, page: p }))}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
