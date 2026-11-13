import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const { registerUser } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    phone_number: '',
    country: '',
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
    setErrors((prev) => ({ ...prev, [e.target.name]: '' }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setErrors({})
    try {
      await registerUser(form)
      navigate('/')
    } catch (err) {
      const data = err.response?.data
      if (data && typeof data === 'object') {
        // Разбираем ошибки по полям от DRF
        const fieldErrors = {}
        Object.entries(data).forEach(([key, val]) => {
          fieldErrors[key] = Array.isArray(val) ? val[0] : val
        })
        setErrors(fieldErrors)
      } else {
        setErrors({ non_field_errors: 'Ошибка регистрации. Попробуйте ещё раз.' })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page page-narrow">
      <h1>Регистрация</h1>
      {errors.non_field_errors && <div className="error-msg">{errors.non_field_errors}</div>}
      <form onSubmit={handleSubmit} className="form">
        <label>
          Логин *
          <input type="text" name="username" value={form.username} onChange={handleChange} required autoComplete="username" />
          {errors.username && <span className="field-error">{errors.username}</span>}
        </label>
        <label>
          Email *
          <input type="email" name="email" value={form.email} onChange={handleChange} required autoComplete="email" />
          {errors.email && <span className="field-error">{errors.email}</span>}
        </label>
        <label>
          Пароль *
          <input type="password" name="password" value={form.password} onChange={handleChange} required autoComplete="new-password" />
          {errors.password && <span className="field-error">{errors.password}</span>}
        </label>
        <label>
          Телефон
          <input type="tel" name="phone_number" value={form.phone_number} onChange={handleChange} placeholder="+79001234567" />
          {errors.phone_number && <span className="field-error">{errors.phone_number}</span>}
        </label>
        <label>
          Страна
          <input type="text" name="country" value={form.country} onChange={handleChange} placeholder="Россия" />
          {errors.country && <span className="field-error">{errors.country}</span>}
        </label>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Регистрирую...' : 'Зарегистрироваться'}
        </button>
      </form>
      <p className="form-footer">
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </div>
  )
}
