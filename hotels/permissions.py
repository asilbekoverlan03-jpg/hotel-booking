from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Администратор может делать всё.
    Остальные — только безопасные методы (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Владелец объекта или администратор может редактировать/удалять.
    Для чтения — любой авторизованный.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        # Для бронирований проверяем поле guest, для отзывов — user
        owner = getattr(obj, 'guest', None) or getattr(obj, 'user', None)
        return owner == request.user
