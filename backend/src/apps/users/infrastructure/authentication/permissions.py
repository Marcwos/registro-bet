from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Permiso que solo permite acceso a usuarios con rol admin"""

    def has_permission(self, request, view):
        return bool(hasattr(request.user, "role") and request.user.role == "admin")
