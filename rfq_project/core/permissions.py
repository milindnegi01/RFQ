from rest_framework.permissions import BasePermission, SAFE_METHODS

class isclientadmin(BasePermission):
    def has_permission(self, request, view):
        print(f"Checking permissions for user: {request.user.username}")
        print(f"User role: {request.user.role}")
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'client_admin'
        )