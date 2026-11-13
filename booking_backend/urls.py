"""
Главный URL-конфиг проекта.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from hotels.views import (
    RegisterView, MeView,
    HotelViewSet, RoomViewSet, RoomTypeViewSet,
    BookingViewSet, HotelReviewViewSet,
)

# ─── DRF Router ────────────────────────────────────────────────────────────────
router = DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'room-types', RoomTypeViewSet, basename='roomtype')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', HotelReviewViewSet, basename='review')

urlpatterns = [
    # Административная панель Django
    path('admin/', admin.site.urls),

    # ─── Auth endpoints ────────────────────────────────────────────────────────
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', MeView.as_view(), name='me'),

    # ─── API endpoints ─────────────────────────────────────────────────────────
    path('api/', include(router.urls)),

    # ─── Swagger / OpenAPI схема ───────────────────────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Раздача медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
