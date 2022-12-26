from rest_framework import permissions

# from user.models import ADMIN


class IsOwnerOnly(permissions.BasePermission):
    """
    Только владелец.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj.username == request.user.username
            and obj.email == request.user.email
        )


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return (
            request.method in permissions.SAFE_METHODS
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Кастомное разрешение,
    только автор имеет право на редактирование."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )
