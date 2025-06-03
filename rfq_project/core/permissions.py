from rest_framework.permissions import BasePermission, SAFE_METHODS
class ismateradmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'master_admin'
        )
    
class isclientadmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'client_admin'
        )
        # if not request.user or not request.user.is_authenticated:
        #     return False
        # if request.method == 'POST':
        #     return request.user.role == 'master_admin'
        # if request.method in SAFE_METHODS:
        #     return True
        # return request.user.role == 'master_admin'


