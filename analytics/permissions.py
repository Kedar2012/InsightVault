from rest_framework.permissions import BasePermission

class IsAnalystOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) in ["analyst", "admin"]
        )
