import axios from 'axios'

// Базовый URL берётся из .env (VITE_API_URL)
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8002/api',
})

// ─── Request interceptor: подставляем access-токен ─────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ─── Response interceptor: при 401 пробуем refresh ─────────────────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    // Если 401 и запрос ещё не повторялся
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh')

      if (refresh) {
        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8002/api'}/auth/refresh/`,
            { refresh }
          )
          localStorage.setItem('access', data.access)
          if (data.refresh) localStorage.setItem('refresh', data.refresh)
          original.headers.Authorization = `Bearer ${data.access}`
          return api(original)
        } catch {
          // Refresh тоже не сработал — разлогиниваем
          localStorage.removeItem('access')
          localStorage.removeItem('refresh')
          window.location.href = '/login'
        }
      }
    }

    return Promise.reject(error)
  }
)

export default api
