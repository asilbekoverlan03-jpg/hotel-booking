from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


# ─── Пользователь ──────────────────────────────────────────────────────────────

class UserProfile(AbstractUser):
    """Расширенная модель пользователя с дополнительными полями профиля."""
    phone_number = models.CharField('Телефон', max_length=20, blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    country = models.CharField('Страна', max_length=100, blank=True)
    date_register = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


# ─── Тип номера ────────────────────────────────────────────────────────────────

class RoomType(models.Model):
    """Тип номера: стандарт, делюкс, сьют, семейный."""

    STANDARD = 'standard'
    DELUXE = 'deluxe'
    SUITE = 'suite'
    FAMILY = 'family'

    NAME_CHOICES = [
        (STANDARD, 'Стандарт'),
        (DELUXE, 'Делюкс'),
        (SUITE, 'Сьют'),
        (FAMILY, 'Семейный'),
    ]

    name = models.CharField('Название', max_length=20, choices=NAME_CHOICES, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Тип номера'
        verbose_name_plural = 'Типы номеров'

    def __str__(self):
        return self.get_name_display()


# ─── Отель ─────────────────────────────────────────────────────────────────────

class Hotel(models.Model):
    """Модель отеля."""
    name = models.CharField('Название', max_length=200)
    address = models.CharField('Адрес', max_length=300)
    city = models.CharField('Город', max_length=100)
    country = models.CharField('Страна', max_length=100)
    stars = models.PositiveSmallIntegerField(
        'Звёзды',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField('Описание', blank=True)
    photo = models.ImageField('Фото', upload_to='hotels/', blank=True, null=True)
    has_parking = models.BooleanField('Парковка', default=False)
    has_wifi = models.BooleanField('Wi-Fi', default=False)

    class Meta:
        verbose_name = 'Отель'
        verbose_name_plural = 'Отели'
        ordering = ['-stars', 'name']

    def __str__(self):
        return f'{self.name} ({self.city})'

    def get_avg_rating(self):
        """Возвращает средний рейтинг отеля по отзывам или None."""
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        total = sum(r.stars for r in reviews)
        return round(total / reviews.count(), 1)


# ─── Номер ─────────────────────────────────────────────────────────────────────

class Room(models.Model):
    """Номер в отеле."""
    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE,
        related_name='rooms', verbose_name='Отель'
    )
    room_type = models.ForeignKey(
        RoomType, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='rooms', verbose_name='Тип номера'
    )
    room_number = models.CharField('Номер комнаты', max_length=10)
    price_per_night = models.DecimalField('Цена за ночь', max_digits=10, decimal_places=2)
    capacity = models.PositiveSmallIntegerField('Вместимость', default=2)
    description = models.TextField('Описание', blank=True)
    is_available = models.BooleanField('Доступен', default=True)

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'
        unique_together = [('hotel', 'room_number')]
        ordering = ['price_per_night']

    def __str__(self):
        return f'#{self.room_number} — {self.hotel.name}'


# ─── Изображения номера ────────────────────────────────────────────────────────

class RoomImage(models.Model):
    """Дополнительные фотографии номера."""
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE,
        related_name='images', verbose_name='Номер'
    )
    image = models.ImageField('Изображение', upload_to='rooms/')

    class Meta:
        verbose_name = 'Фото номера'
        verbose_name_plural = 'Фото номеров'

    def __str__(self):
        return f'Фото для {self.room}'


# ─── Бронирование ──────────────────────────────────────────────────────────────

class Booking(models.Model):
    """Бронирование номера."""

    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_CONFIRMED, 'Подтверждено'),
        (STATUS_CANCELLED, 'Отменено'),
        (STATUS_COMPLETED, 'Завершено'),
    ]

    guest = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='bookings', verbose_name='Гость'
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE,
        related_name='bookings', verbose_name='Номер'
    )
    check_in = models.DateField('Дата заезда')
    check_out = models.DateField('Дата выезда')
    guests_count = models.PositiveSmallIntegerField('Количество гостей', default=1)
    status = models.CharField(
        'Статус', max_length=20,
        choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_date']

    def __str__(self):
        return f'Бронь {self.id}: {self.guest} → {self.room} ({self.check_in} – {self.check_out})'

    def get_nights(self):
        """Количество ночей пребывания."""
        return (self.check_out - self.check_in).days

    def get_total_price(self):
        """Итоговая стоимость бронирования."""
        nights = self.get_nights()
        if nights <= 0:
            return 0
        return self.room.price_per_night * nights


# ─── Отзыв об отеле ────────────────────────────────────────────────────────────

class HotelReview(models.Model):
    """Отзыв пользователя об отеле."""
    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Отель'
    )
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Пользователь'
    )
    stars = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField('Комментарий', blank=True)
    created_date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_date']
        # Один пользователь — один отзыв на отель
        unique_together = [('hotel', 'user')]

    def __str__(self):
        return f'{self.user} → {self.hotel}: {self.stars}★'
