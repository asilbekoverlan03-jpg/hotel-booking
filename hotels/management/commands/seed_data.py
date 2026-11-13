"""
Management command для заполнения БД тестовыми данными.
Запуск: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from hotels.models import UserProfile, RoomType, Hotel, Room, Booking, HotelReview
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными: отели, номера, пользователи, брони, отзывы'

    def handle(self, *args, **kwargs):
        self.stdout.write('Очищаю старые тестовые данные...')
        HotelReview.objects.all().delete()
        Booking.objects.all().delete()
        Room.objects.all().delete()
        Hotel.objects.all().delete()
        RoomType.objects.all().delete()
        UserProfile.objects.filter(is_superuser=False).delete()

        # ─── Типы номеров ──────────────────────────────────────────────────────
        self.stdout.write('Создаю типы номеров...')
        standard = RoomType.objects.create(name='standard', description='Стандартный номер с базовыми удобствами')
        deluxe = RoomType.objects.create(name='deluxe', description='Улучшенный номер с панорамным видом')
        suite = RoomType.objects.create(name='suite', description='Просторный сьют с гостиной')
        family = RoomType.objects.create(name='family', description='Семейный номер для 4+ гостей')

        # ─── Пользователи ─────────────────────────────────────────────────────
        self.stdout.write('Создаю пользователей...')
        user1 = UserProfile.objects.create(
            username='alice',
            email='alice@example.com',
            password=make_password('password123'),
            phone_number='+79001234567',
            country='Россия',
        )
        user2 = UserProfile.objects.create(
            username='bob',
            email='bob@example.com',
            password=make_password('password123'),
            phone_number='+79007654321',
            country='Беларусь',
        )

        # ─── Отели ────────────────────────────────────────────────────────────
        self.stdout.write('Создаю отели...')
        hotels_data = [
            {
                'name': 'Grand Palace Hotel',
                'address': 'ул. Тверская, 1',
                'city': 'Москва',
                'country': 'Россия',
                'stars': 5,
                'description': 'Роскошный отель в центре Москвы с видом на Кремль.',
                'has_parking': True,
                'has_wifi': True,
            },
            {
                'name': 'Nevsky Inn',
                'address': 'Невский пр., 45',
                'city': 'Санкт-Петербург',
                'country': 'Россия',
                'stars': 4,
                'description': 'Уютный отель на главном проспекте Петербурга.',
                'has_parking': False,
                'has_wifi': True,
            },
            {
                'name': 'Sochi Beach Resort',
                'address': 'ул. Приморская, 12',
                'city': 'Сочи',
                'country': 'Россия',
                'stars': 4,
                'description': 'Курортный отель у Черного моря.',
                'has_parking': True,
                'has_wifi': True,
            },
            {
                'name': 'Kazan Tower Hotel',
                'address': 'ул. Баумана, 8',
                'city': 'Казань',
                'country': 'Россия',
                'stars': 3,
                'description': 'Современный бизнес-отель в историческом центре.',
                'has_parking': True,
                'has_wifi': True,
            },
            {
                'name': 'Siberian Lodge',
                'address': 'ул. Ленина, 22',
                'city': 'Новосибирск',
                'country': 'Россия',
                'stars': 3,
                'description': 'Комфортный отель для деловых поездок.',
                'has_parking': False,
                'has_wifi': True,
            },
        ]

        hotels = [Hotel.objects.create(**data) for data in hotels_data]

        # ─── Номера ───────────────────────────────────────────────────────────
        self.stdout.write('Создаю номера...')
        rooms_data = [
            # Grand Palace
            {'hotel': hotels[0], 'room_type': standard, 'room_number': '101', 'price_per_night': 5000, 'capacity': 2},
            {'hotel': hotels[0], 'room_type': deluxe,   'room_number': '201', 'price_per_night': 8000, 'capacity': 2},
            {'hotel': hotels[0], 'room_type': suite,    'room_number': '301', 'price_per_night': 15000, 'capacity': 3},
            {'hotel': hotels[0], 'room_type': family,   'room_number': '401', 'price_per_night': 12000, 'capacity': 5},
            # Nevsky Inn
            {'hotel': hotels[1], 'room_type': standard, 'room_number': '101', 'price_per_night': 3500, 'capacity': 2},
            {'hotel': hotels[1], 'room_type': deluxe,   'room_number': '201', 'price_per_night': 6000, 'capacity': 2},
            # Sochi Beach
            {'hotel': hotels[2], 'room_type': standard, 'room_number': '101', 'price_per_night': 4000, 'capacity': 2},
            {'hotel': hotels[2], 'room_type': suite,    'room_number': '201', 'price_per_night': 9000, 'capacity': 3},
            {'hotel': hotels[2], 'room_type': family,   'room_number': '301', 'price_per_night': 7500, 'capacity': 4},
            # Kazan Tower
            {'hotel': hotels[3], 'room_type': standard, 'room_number': '101', 'price_per_night': 2500, 'capacity': 2},
            {'hotel': hotels[3], 'room_type': deluxe,   'room_number': '201', 'price_per_night': 4000, 'capacity': 2},
            # Siberian Lodge
            {'hotel': hotels[4], 'room_type': standard, 'room_number': '101', 'price_per_night': 2000, 'capacity': 2},
        ]

        rooms = [Room.objects.create(**data) for data in rooms_data]

        # ─── Бронирования ─────────────────────────────────────────────────────
        self.stdout.write('Создаю бронирования...')
        today = date.today()
        Booking.objects.create(
            guest=user1,
            room=rooms[0],
            check_in=today + timedelta(days=5),
            check_out=today + timedelta(days=8),
            guests_count=2,
            status=Booking.STATUS_CONFIRMED,
        )
        Booking.objects.create(
            guest=user2,
            room=rooms[4],
            check_in=today + timedelta(days=10),
            check_out=today + timedelta(days=14),
            guests_count=1,
            status=Booking.STATUS_PENDING,
        )

        # ─── Отзывы ───────────────────────────────────────────────────────────
        self.stdout.write('Создаю отзывы...')
        HotelReview.objects.create(hotel=hotels[0], user=user1, stars=5, comment='Великолепный отель, сервис на высшем уровне!')
        HotelReview.objects.create(hotel=hotels[0], user=user2, stars=4, comment='Очень хороший отель, немного шумновато.')
        HotelReview.objects.create(hotel=hotels[1], user=user1, stars=4, comment='Удобное расположение, чистые номера.')
        HotelReview.objects.create(hotel=hotels[2], user=user2, stars=5, comment='Лучший отпуск в моей жизни!')

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Создано: {len(hotels)} отелей, {len(rooms)} номеров, '
            f'2 пользователя (alice/password123, bob/password123), '
            f'2 брони, 4 отзыва.'
        ))
