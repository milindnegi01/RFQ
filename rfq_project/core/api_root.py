from rest_framework.views import APIView
from rest_framework.response import Response
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from .permissions import isclientadmin
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)

class CustomAPIRootView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise AuthenticationFailed('Authentication credentials were not provided.')
        
        # Debug information
        print("\n=== User Information ===")
        print(f"Username: {request.user.username}")
        print(f"Role: {request.user.role}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"Is active: {request.user.is_active}")
        print("======================\n")
        
        ret = {}
        
        # Add user info to response for debugging
        ret['debug_info'] = {
            'username': request.user.username,
            'role': request.user.role,
            'is_authenticated': request.user.is_authenticated,
            'is_active': request.user.is_active
        }
        
        # Common endpoints for all authenticated users
        ret['Logout'] = request.build_absolute_uri(reverse('logout'))
        
        # Strictly check user role and show only relevant endpoints
        if request.user.role == 'client_admin':
            print("Adding client admin endpoints")
            # Client admin can only see and access these endpoints
            ret['Create End User'] = request.build_absolute_uri(reverse('end-user-create'))
            ret['List End Users'] = request.build_absolute_uri(reverse('end-user-list'))
            ret['Create Supplier'] = request.build_absolute_uri(reverse('supplier-create'))
            ret['List Suppliers'] = request.build_absolute_uri(reverse('supplier-list'))
            ret['List Commodities'] = request.build_absolute_uri(reverse('list-commodities'))
            ret['Create Commodity'] = request.build_absolute_uri(reverse('create-commodity'))
            # ret['List All RFQs'] = request.build_absolute_uri(reverse('rfq-import-list'))
            ret['View End User RFQs'] = request.build_absolute_uri(reverse('clientadmin-view-rfq-imports')) 
            ret['Create RFQ Management'] = request.build_absolute_uri(reverse('create-rfq-management'))
            ret['List RFQ Management'] = request.build_absolute_uri(reverse('list-rfq-management'))


        elif request.user.role == 'end_user':
            ret['Create RFQ Entry'] = request.build_absolute_uri(reverse ('rfq-import-create'))
            ret['List My RFQs'] = request.build_absolute_uri(reverse('rfq-import-list'))
    
        else:
            print(f"User role {request.user.role} is not authorized admin")
            
        return Response(ret)