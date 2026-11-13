from datetime import date
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, RoomType, Hotel, Room, RoomImage, Booking, HotelReview


# ─── Пользователь ──────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """Регистрация нового пользователя."""
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'phone_number', 'country']

    def create(self, validated_data):
        # Создаём пользователя через set_password, чтобы пароль был захеширован
        user = UserProfile(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            country=validated_data.get('country', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Профиль пользователя (чтение и редактирование)."""

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'phone_number', 'avatar', 'country', 'date_register']
        read_only_fields = ['id', 'username', 'date_register']


# ─── Тип номера ────────────────────────────────────────────────────────────────

class RoomTypeSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = RoomType
        fields = ['id', 'name', 'name_display', 'description']


# ─── Изображения номера ────────────────────────────────────────────────────────

class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['id', 'image']


# ─── Номер ─────────────────────────────────────────────────────────────────────

class RoomSerializer(serializers.ModelSerializer):
    """Полный сериализатор номера с типом и фотографиями."""
    images = RoomImageSerializer(many=True, read_only=True)
    room_type = RoomTypeSerializer(read_only=True)
    room_type_id = serializers.PrimaryKeyRelatedField(
        queryset=RoomType.objects.all(), source='room_type', write_only=True, required=False
    )

    class Meta:
        model = Room
        fields = [
            'id', 'hotel', 'room_number', 'price_per_night', 'capacity',
            'description', 'is_available', 'room_type', 'room_type_id', 'images',
        ]


# ─── Отзыв ─────────────────────────────────────────────────────────────────────

class HotelReviewSerializer(serializers.ModelSerializer):
    """Отзыв об отеле. user подставляется из request автоматически."""
    user = UserProfileSerializer(read_only=True)
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = HotelReview
        fields = ['id', 'hotel', 'user', 'user_id', 'stars', 'comment', 'created_date']
        read_only_fields = ['id', 'created_date']

    def create(self, validated_data):
        # user_id → переименовываем в user для модели
        validated_data['user'] = validated_data.pop('user_id')
        return super().create(validated_data)


# ─── Отель (список) ────────────────────────────────────────────────────────────

class HotelListSerializer(serializers.ModelSerializer):
    """Краткая карточка отеля для списка: рейтинг и минимальная цена."""
    avg_rating = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'city', 'country', 'stars', 'photo',
            'avg_rating', 'min_price', 'has_parking', 'has_wifi',
        ]

    def get_avg_rating(self, obj):
        return obj.get_avg_rating()

    def get_min_price(self, obj):
        """Минимальная цена среди доступных номеров."""
        rooms = obj.rooms.filter(is_available=True)
        if not rooms.exists():
            return None
        return float(min(r.price_per_night for r in rooms))


# ─── Отель (детали) ────────────────────────────────────────────────────────────

class HotelDetailSerializer(HotelListSerializer):
    """Полная карточка отеля с вложенными номерами и отзывами."""
    rooms = RoomSerializer(many=True, read_only=True)
    reviews = HotelReviewSerializer(many=True, read_only=True)

    class Meta(HotelListSerializer.Meta):
        fields = HotelListSerializer.Meta.fields + [
            'address', 'description', 'rooms', 'reviews',
        ]


# ─── Бронирование ──────────────────────────────────────────────────────────────

class BookingSerializer(serializers.ModelSerializer):
    """
    Сериализатор бронирования.
    guest берётся из request.user автоматически.
    nights и total_price — вычисляемые поля (read_only).
    """
    guest = UserProfileSerializer(read_only=True)
    # Скрытое поле — подставляем текущего пользователя при создании
    guest_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    nights = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    # Подробная информация о номере в ответе
    room_detail = RoomSerializer(source='room', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'guest', 'guest_id', 'room', 'room_detail',
            'check_in', 'check_out', 'guests_count',
            'status', 'created_date', 'nights', 'total_price',
        ]
        read_only_fields = ['id', 'status', 'created_date']

    def get_nights(self, obj):
        return obj.get_nights()

    def get_total_price(self, obj):
        return float(obj.get_total_price())

    def validate(self, data):
        room = data.get('room')
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        guests_count = data.get('guests_count', 1)

        # 1. Дата выезда строго позже даты заезда
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    'Дата выезда должна быть позже даты заезда.'
                )

        # 2. Дата заезда не в прошлом
        if check_in and check_in < date.today():
            raise serializers.ValidationError(
                'Дата заезда не может быть в прошлом.'
            )

        if room:
            # 3. Количество гостей не превышает вместимость номера
            if guests_count > room.capacity:
                raise serializers.ValidationError(
                    f'Номер вмещает максимум {room.capacity} гостей.'
                )

            # 4. Номер должен быть доступен
            if not room.is_available:
                raise serializers.ValidationError(
                    'Выбранный номер недоступен для бронирования.'
                )

            # 5. Нет пересечений дат с активными бронированиями
            if check_in and check_out:
                # Получаем id текущего объекта при обновлении (исключаем себя)
                instance_id = self.instance.id if self.instance else None

                overlapping = Booking.objects.filter(
                    room=room,
                    status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                )
                if instance_id:
                    overlapping = overlapping.exclude(id=instance_id)

                if overlapping.exists():
                    raise serializers.ValidationError(
                        'На выбранные даты номер уже забронирован.'
                    )

        return data

    def create(self, validated_data):
        # Переносим guest_id → guest
        validated_data['guest'] = validated_data.pop('guest_id')
        validated_data['status'] = Booking.STATUS_PENDING
        return super().create(validated_data)
