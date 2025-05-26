from rest_framework import permissions


class IsOwnerOrReadPublic(permissions.BasePermission):
    """
    Разрешение, которое позволяет:
    - Владельцу привычки выполнять любые действия (GET, POST, PUT, PATCH, DELETE)
    - Анонимным или другим пользователям читать только публичные привычки (GET)
    - Остальные действия запрещены для не-владельцев
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение, если привычка публичная и запрос безопасный (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user

        # Для всех остальных методов разрешаем только владельцу
        return obj.user == request.user
