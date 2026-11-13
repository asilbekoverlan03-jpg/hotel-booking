import api from './axios'

// ─── Отели ─────────────────────────────────────────────────────────────────
export const getHotels = (params) => api.get('/hotels/', { params })
export const getHotel = (id) => api.get(`/hotels/${id}/`)

// ─── Номера ─────────────────────────────────────────────────────────────────
export const getRooms = (params) => api.get('/rooms/', { params })

// ─── Типы номеров ────────────────────────────────────────────────────────────
export const getRoomTypes = () => api.get('/room-types/')

// ─── Бронирования ────────────────────────────────────────────────────────────
export const getBookings = () => api.get('/bookings/')
export const createBooking = (data) => api.post('/bookings/', data)
export const cancelBooking = (id) => api.post(`/bookings/${id}/cancel/`)

// ─── Отзывы ──────────────────────────────────────────────────────────────────
export const getReviews = (hotelId) => api.get('/reviews/', { params: { hotel: hotelId } })
export const createReview = (data) => api.post('/reviews/', data)

// ─── Авторизация ─────────────────────────────────────────────────────────────
export const register = (data) => api.post('/auth/register/', data)
export const login = (data) => api.post('/auth/login/', data)
export const refreshToken = (refresh) => api.post('/auth/refresh/', { refresh })
export const getMe = () => api.get('/auth/me/')
export const updateMe = (data) => api.patch('/auth/me/', data)
