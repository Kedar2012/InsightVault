from rest_framework.permissions import BasePermission

class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.is_staff
            and getattr(request.user, "role", None) == "analyst"
        )
class IsSupport(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.is_staff
            and getattr(request.user, "role", None) == "support"
        )
class IsSupportOrAnalyst(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.is_staff
            and getattr(request.user, "role", None) in ["support", "analyst"]
        )
