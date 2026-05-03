from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_staff
        )
class IsEndUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "enduser"

class IsSupportOrAnalyst(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["support", "analyst"]

