from rest_framework import permissions


class AuthorEditPermissionOnly(permissions.BasePermission):
    """
    Разрешение на редактирование объекта только для его автора.
    Остальные пользователи могут только просматривать.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        # Остальные действия — только если пользователь является автором объекта
        return getattr(obj, "author", None) == request.user
