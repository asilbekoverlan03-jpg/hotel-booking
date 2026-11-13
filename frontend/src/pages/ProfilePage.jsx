import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { updateMe } from '../api/hotels'

export default function ProfilePage() {
  const { user, setUser } = useAuth()

  const [form, setForm] = useState({
    email: user?.email || '',
    phone_number: user?.phone_number || '',
    country: user?.country || '',
  })
  const [avatarFile, setAvatarFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
    setSuccess(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess(false)

    try {
      // Если загружен аватар — отправляем multipart/form-data
      let payload
      if (avatarFile) {
        payload = new FormData()
        Object.entries(form).forEach(([k, v]) => payload.append(k, v))
        payload.append('avatar', avatarFile)
      } else {
        payload = form
      }

      const { data } = await updateMe(payload)
      setUser(data)
      setSuccess(true)
    } catch (err) {
      const d = err.response?.data
      setError(d ? Object.values(d).flat().join(' ') : 'Ошибка сохранения.')
    } finally {
      setLoading(false)
    }
  }

  const avatarUrl = user?.avatar
    ? (user.avatar.startsWith('http') ? user.avatar : `http://127.0.0.1:8002${user.avatar}`)
    : null

  return (
    <div className="page page-narrow">
      <h1>Профиль</h1>

      <div className="profile-header">
        {avatarUrl
          ? <img src={avatarUrl} alt="Аватар" className="avatar" />
          : <div className="avatar-placeholder">👤</div>
        }
        <div>
          <h2>{user?.username}</h2>
          <p>Зарегистрирован: {user?.date_register
            ? new Date(user.date_register).toLocaleDateString('ru-RU')
            : '—'}
          </p>
        </div>
      </div>

      {success && <div className="success-msg">Профиль обновлён!</div>}
      {error && <div className="error-msg">{error}</div>}

      <form onSubmit={handleSubmit} className="form">
        <label>
          Email
          <input type="email" name="email" value={form.email} onChange={handleChange} />
        </label>
        <label>
          Телефон
          <input type="tel" name="phone_number" value={form.phone_number} onChange={handleChange} />
        </label>
        <label>
          Страна
          <input type="text" name="country" value={form.country} onChange={handleChange} />
        </label>
        <label>
          Аватар
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setAvatarFile(e.target.files[0] || null)}
          />
        </label>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Сохраняю...' : 'Сохранить изменения'}
        </button>
      </form>
    </div>
  )
}
