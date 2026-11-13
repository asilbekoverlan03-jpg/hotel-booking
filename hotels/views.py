from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as df
from django.db.models import Min

from .models import UserProfile, RoomType, Hotel, Room, Booking, HotelReview
from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    RoomTypeSerializer, HotelListSerializer, HotelDetailSerializer,
    RoomSerializer, BookingSerializer, HotelReviewSerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


# ─── Авторизация ───────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — регистрация нового пользователя."""
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/me/ — профиль текущего пользователя."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ─── Фильтры ───────────────────────────────────────────────────────────────────

class HotelFilter(df.FilterSet):
    """Фильтры для списка отелей."""
    min_stars = df.NumberFilter(field_name='stars', lookup_expr='gte')
    max_stars = df.NumberFilter(field_name='stars', lookup_expr='lte')
    # Фильтр по минимальной цене номера
    min_price = df.NumberFilter(method='filter_min_price')
    max_price = df.NumberFilter(method='filter_max_price')

    class Meta:
        model = Hotel
        fields = ['city', 'country', 'stars', 'has_parking', 'has_wifi']

    def filter_min_price(self, queryset, name, value):
        return queryset.filter(rooms__price_per_night__gte=value).distinct()

    def filter_max_price(self, queryset, name, value):
        return queryset.filter(rooms__price_per_night__lte=value).distinct()


class RoomFilter(df.FilterSet):
    """Фильтры для списка номеров."""
    min_price = df.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = df.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    min_capacity = df.NumberFilter(field_name='capacity', lookup_expr='gte')

    class Meta:
        model = Room
        fields = ['hotel', 'room_type', 'is_available', 'capacity']


# ─── Отели ─────────────────────────────────────────────────────────────────────

class HotelViewSet(viewsets.ModelViewSet):
    """
    CRUD для отелей.
    Чтение — для всех; создание/изменение/удаление — только для администраторов.
    """
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = HotelFilter
    search_fields = ['name', 'city', 'country', 'description']
    ordering_fields = ['stars', 'name']
    ordering = ['-stars']

    def get_queryset(self):
        # prefetch_related/select_related для оптимизации N+1 запросов
        return Hotel.objects.prefetch_related(
            'rooms__images', 'rooms__room_type', 'reviews__user'
        ).annotate(
            min_price=Min('rooms__price_per_night')
        )

    def get_serializer_class(self):
        # На detail-странице отдаём полный сериализатор
        if self.action == 'retrieve':
            return HotelDetailSerializer
        return HotelListSerializer


# ─── Номера ────────────────────────────────────────────────────────────────────

class RoomViewSet(viewsets.ModelViewSet):
    """
    CRUD для номеров.
    Чтение — для всех; изменение — только для администраторов.
    """
    serializer_class = RoomSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = RoomFilter
    ordering_fields = ['price_per_night', 'capacity']
    ordering = ['price_per_night']

    def get_queryset(self):
        return Room.objects.select_related(
            'hotel', 'room_type'
        ).prefetch_related('images')


# ─── Типы номеров ──────────────────────────────────────────────────────────────

class RoomTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/room-types/ — справочник типов номеров, только чтение."""
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [AllowAny]


# ─── Бронирования ──────────────────────────────────────────────────────────────

class BookingViewSet(viewsets.ModelViewSet):
    """
    CRUD для бронирований.
    Пользователь видит только свои брони.
    POST /api/bookings/{id}/cancel/ — отмена брони.
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related(
            'guest', 'room__hotel', 'room__room_type'
        ).prefetch_related('room__images')

        # Администратор видит все брони, обычный пользователь — только свои
        if user.is_staff:
            return qs
        return qs.filter(guest=user)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """POST /api/bookings/{id}/cancel/ — отмена бронирования."""
        booking = self.get_object()

        if booking.status in [Booking.STATUS_CANCELLED, Booking.STATUS_COMPLETED]:
            return Response(
                {'detail': 'Невозможно отменить бронирование с текущим статусом.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=['status'])
        return Response(BookingSerializer(booking, context={'request': request}).data)


# ─── Отзывы ────────────────────────────────────────────────────────────────────

class HotelReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD для отзывов.
    Создание — только авторизованным; редактирование/удаление — своих отзывов.
    """
    serializer_class = HotelReviewSerializer
    filterset_fields = ['hotel']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrAdmin()]

    def get_queryset(self):
        return HotelReview.objects.select_related('user', 'hotel')
