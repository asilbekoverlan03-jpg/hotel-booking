from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, RoomType, Hotel, Room, RoomImage, Booking, HotelReview


# ─── Пользователь ──────────────────────────────────────────────────────────────

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone_number', 'country', 'is_staff', 'date_register']
    list_filter = ['is_staff', 'country']
    search_fields = ['username', 'email', 'phone_number']
    # Добавляем наши поля в форму редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('phone_number', 'avatar', 'country')}),
    )


# ─── Тип номера ────────────────────────────────────────────────────────────────

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


# ─── Отель ─────────────────────────────────────────────────────────────────────

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'stars', 'has_parking', 'has_wifi']
    list_filter = ['stars', 'country', 'has_parking', 'has_wifi']
    search_fields = ['name', 'city', 'country']


# ─── Фото номера (inline) ──────────────────────────────────────────────────────

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1


# ─── Номер ─────────────────────────────────────────────────────────────────────

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hotel', 'room_type', 'price_per_night', 'capacity', 'is_available']
    list_filter = ['hotel', 'room_type', 'is_available']
    search_fields = ['room_number', 'hotel__name']
    inlines = [RoomImageInline]


# ─── Бронирование ──────────────────────────────────────────────────────────────

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'guest', 'room', 'check_in', 'check_out', 'status', 'created_date']
    list_filter = ['status', 'check_in', 'check_out']
    search_fields = ['guest__username', 'room__room_number', 'room__hotel__name']
    date_hierarchy = 'created_date'
    readonly_fields = ['created_date']


# ─── Отзыв ─────────────────────────────────────────────────────────────────────

@admin.register(HotelReview)
class HotelReviewAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'user', 'stars', 'created_date']
    list_filter = ['stars', 'hotel']
    search_fields = ['hotel__name', 'user__username', 'comment']
    readonly_fields = ['created_date']
