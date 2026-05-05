from rest_framework.permissions import BasePermission

class IsEndUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.is_staff
            and getattr(request.user, "role", None) == "end_user"
        )
        
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

class IsAdminOrAnalyst(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_superuser
                or getattr(request.user, "role", None) == "analyst"
            )
        )
