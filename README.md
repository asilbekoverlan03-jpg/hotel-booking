# Бронирование отелей

Сервис бронирования отелей (аналог Booking.com): отели, номера, бронирования и отзывы.

## Стек

Python, Django, Django REST Framework, React (Vite)

## Запуск

### Backend (Windows PowerShell)

```powershell
# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Заполнить тестовыми данными (5 отелей, 12 номеров, 2 пользователя)
python manage.py seed_data

# Запустить сервер на порту 8002
python manage.py runserver 8002
```

Backend доступен по адресам:
- API: http://127.0.0.1:8002/api/
- Swagger: http://127.0.0.1:8002/api/docs/
- Админ-панель: http://127.0.0.1:8002/admin/

### Frontend

```powershell
cd frontend

# Скопировать конфиг и при необходимости отредактировать
cp .env.example .env

# Установить зависимости
npm install

# Запустить dev-сервер
npm run dev
```

Frontend доступен на: http://localhost:5173

### Переменные окружения

Скопируйте `.env.example` в `.env` в корне проекта:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## Что сделано

- Модели отелей (`Hotel`), номеров (`Room`), фото номеров (`RoomImage`), бронирований (`Booking`) и отзывов (`HotelReview`)
- Кастомная модель пользователя (`UserProfile`) на базе `AbstractUser`
- REST API на Django REST Framework: CRUD для всех моделей, JWT-авторизация, фильтрация, поиск, пагинация
- Валидация бронирований: проверка дат, вместимости, доступности номера и пересечения с существующими бронями
- Swagger-документация по адресу `/api/docs/`
- Подключение API к фронтенду на React (Vite): список отелей с фильтрами, страница отеля, форма бронирования, мои бронирования, профиль, авторизация

## Тестовые пользователи (после seed_data)

| Логин | Пароль |
|-------|--------|
| alice | password123 |
| bob   | password123 |
