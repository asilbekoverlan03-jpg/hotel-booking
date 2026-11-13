import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import HeroBanner from './components/HeroBanner'
import PrivateRoute from './components/PrivateRoute'

import HotelsPage from './pages/HotelsPage'
import HotelDetailPage from './pages/HotelDetailPage'
import BookingPage from './pages/BookingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import MyBookingsPage from './pages/MyBookingsPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <HeroBanner />
        <main className="container">
          <Routes>
            {/* Публичные маршруты */}
            <Route path="/" element={<HotelsPage />} />
            <Route path="/hotels/:id" element={<HotelDetailPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Защищённые маршруты — только для авторизованных */}
            <Route
              path="/booking/:roomId"
              element={<PrivateRoute><BookingPage /></PrivateRoute>}
            />
            <Route
              path="/bookings"
              element={<PrivateRoute><MyBookingsPage /></PrivateRoute>}
            />
            <Route
              path="/profile"
              element={<PrivateRoute><ProfilePage /></PrivateRoute>}
            />
          </Routes>
        </main>
      </BrowserRouter>
    </AuthProvider>
  )
}
