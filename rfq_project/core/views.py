from rest_framework import generics
from .models import CustomUser,Commodity,RFQImportData,RFQManagement,EndUserProfile, ClientAdminProfile
from .serializers import CustomUserSerializer,EndUserCreateSerializer,SupplierCreateSerializer,CustomTokenObtainPairSerializer,CommoditySerializer,RFQImportDataSerializer,RFQManagementSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import isclientadmin,isenduser
from rest_framework import filters,status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
import logging
logger = logging.getLogger(__name__)

class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        print(f"\n=== Login Attempt ===")
        print(f"Username: {username}")
        
        # Try to authenticate the user
        user = authenticate(username=username, password=password)
        if user:
            print(f"User authenticated: {user.username}")
            print(f"User role: {user.role}")
        else:
            print("Authentication failed")
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data['access']
            refresh_token = response.data['refresh']
            
            # Create a new response for redirect
            redirect_response = HttpResponseRedirect(reverse('api-root'))
            
            # Set cookies in the redirect response
            redirect_response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE'],
                access_token,
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
            )
            redirect_response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                refresh_token,
                expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
            )
            
            # Set the Authorization header
            redirect_response['Authorization'] = f'Bearer {access_token}'
            
            return redirect_response
            
        return response
class LogoutView(APIView):
    def post(self,request):
        response = Response()
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        response.data = {'message':'Successfully logged out'}
        return response

#Master Admin rights        
# class CreateMasterAdminView(generics.ListCreateAPIView):
#     serializer_class = CustomUserSerializer
#     permission_classes = [IsAuthenticated,ismateradmin]

#     def perform_create(self, serializer):
#         serializer.save(role='master_admin')

# class CreateClientAdminView(generics.CreateAPIView):
#     serializer_class = ClientAdminCreateSerializer
#     permission_classes = [IsAuthenticated,ismateradmin]

#     def perform_create(self, serializer):
#         serializer.save(role='client_admin')

class CreateSupplierView(generics.CreateAPIView):
    serializer_class = SupplierCreateSerializer
    permission_classes = [IsAuthenticated,isclientadmin]

    def perform_create(self, serializer):
        serializer.save(role='supplier')

class CreateEndUserView(generics.CreateAPIView):
    serializer_class = EndUserCreateSerializer
    permission_classes = [IsAuthenticated,isclientadmin]

    def perform_create(self, serializer):
        serializer.save(role='end_user')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

# class ListClientAdminView(generics.ListAPIView):
#     serializer_class = CustomUserSerializer
#     permission_classes = [IsAuthenticated,ismateradmin]

#     def get_queryset(self):
#         return CustomUser.objects.filter(role='client_admin')

class ListEndUserView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,isclientadmin]

    def get_queryset(self):
        # Only return end users from the client admin's organization
        return CustomUser.objects.filter(
            role='end_user',
            organization=self.request.user.organization
        )

class ListSupplierView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,isclientadmin]

    def get_queryset(self):
        return CustomUser.objects.filter(role='supplier')
    
##client admin crud operations
class RetrieveEndUserView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,isclientadmin]
    def get_queryset(self):
        if self.request.user.role == 'client_admin':
            return CustomUser.objects.filter(organization=self.request.user.organization,role__in=['supplier','end_user'])
        return CustomUser.objects.all()

class UpdateUserView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,isclientadmin]
    def get_queryset(self):
        if self.request.user.role == 'client_admin':
            return CustomUser.objects.filter(organization=self.request.user.organization,role__in=['supplier','end_user'])
        return CustomUser.objects.all()

    def perform_update(self, serializer):
        instance = serializer.save()
        print(f"User {instance.username} updated with new role:{instance.role}")

class DeleteUserView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,isclientadmin]
    def get_queryset(self):
        if self.request.user.role == 'client_admin':
            return CustomUser.objects.filter(organization=self.request.user.organization,role__in=['supplier','end_user'])
        return CustomUser.objects.all()

class OrganizationUserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,isclientadmin]
    def get_queryset(self):
        org = self.kwargs['org_name']
        if self.request.user.role == 'client_admin':
            if org != self.request.user.organization:
                raise CustomUser.objects.none()
            return CustomUser.objects.filter(organization=org,role__in=['supplier','end_user'])
        return CustomUser.objects.filter(organization=org,role__in=['client_admin','supplier','end_user'])


# from django.shortcuts import render
# def login(request):
#     return render(request,'login.html')

##master admin and client admin can manage commodities 
class CreateCommodityView(generics.CreateAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer
    permission_classes = [IsAuthenticated , isclientadmin]

class ListCommodityView(generics.ListAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer
    permission_classes = [IsAuthenticated, isclientadmin]

class UpdateCommodityView(generics.UpdateAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer
    permission_classes = [IsAuthenticated , isclientadmin]

# class DeleteCommodityView(generics.DestroyAPIView):
#     queryset = Commodity.objects.all()
#     serializer_class = CommoditySerializer
#     permission_classes = [IsAuthenticated, ismateradmin]
from rest_framework.exceptions import ValidationError
##end - user
class CreateRFQImportView(generics.CreateAPIView):
    queryset = RFQImportData.objects.all()
    serializer_class = RFQImportDataSerializer
    permission_classes = [IsAuthenticated, isenduser]  # Custom permission

    def perform_create(self, serializer):
        # Ensure the end user has an organization set
        if not self.request.user.organization:
            raise ValidationError("End user must have an organization set")
        
        # Add debug logging
        print(f"Creating RFQ for user: {self.request.user.username}")
        print(f"User organization: {self.request.user.organization}")
        
        rfq = serializer.save(created_by=self.request.user)
        print(f"Created RFQ with ID: {rfq.id}")
        print(f"RFQ organization: {rfq.created_by.organization}")

class ListRFQImportView(generics.ListAPIView):
    serializer_class = RFQImportDataSerializer
    permission_classes = [IsAuthenticated, isenduser]

    def get_queryset(self):
        print(f"Listing RFQs for user: {self.request.user.username}")
        print(f"User role: {self.request.user.role}")
        print(f"User organization: {self.request.user.organization}")
        
        if self.request.user.role == 'client_admin':
            # Show all RFQs from the client admin's organization
            queryset = RFQImportData.objects.filter(
                created_by__organization=self.request.user.organization
            ).select_related('created_by')
            print(f"Found {queryset.count()} RFQs for client admin")
            return queryset
        elif self.request.user.role == 'end_user':
            # Show only RFQs created by the end user
            queryset = RFQImportData.objects.filter(created_by=self.request.user)
            print(f"Found {queryset.count()} RFQs for end user")
            return queryset
        return RFQImportData.objects.none()
##new one hehe
class ClientAdminRFQImportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if user.role != 'client_admin':
            return Response({'error': 'Only client admins can view this data'}, status=403)

        try:
            client_admin_profile = ClientAdminProfile.objects.get(user=user)
        except ClientAdminProfile.DoesNotExist:
            return Response({'error': 'Client admin profile not found'}, status=404)

        # Get all end users assigned to this client admin
        end_user_profiles = EndUserProfile.objects.filter(client_admin=client_admin_profile)
        end_user_ids = [profile.user.id for profile in end_user_profiles]

        # Get RFQs created by these end users
        rfqs = RFQImportData.objects.filter(created_by__id__in=end_user_ids)

        serializer = RFQImportDataSerializer(rfqs, many=True)
        return Response(serializer.data)
    
class RFQManagementCreateView(generics.CreateAPIView):
    queryset = RFQManagement.objects.all()
    serializer_class = RFQManagementSerializer
    permission_classes = [IsAuthenticated, isclientadmin]

class RFQManagementListView(generics.ListAPIView):
    queryset = RFQManagement.objects.all()
    serializer_class = RFQManagementSerializer
    permission_classes = [IsAuthenticated, isclientadmin]

class RFQManagementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RFQManagement.objects.all()
    serializer_class = RFQManagementSerializer
    permission_classes = [IsAuthenticated, isclientadmin]
class AutoPromoteRFQView(APIView):
    permission_classes = [IsAuthenticated, isclientadmin]

    def post(self, request, *args, **kwargs):
        rfq_import_id = request.data.get('rfq_import')

        if not rfq_import_id:
            return Response({'error': 'rfq_import ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        rfq_import = get_object_or_404(RFQImportData, id=rfq_import_id)

        # Optional: Check if it’s already promoted
        if RFQManagement.objects.filter(rfq_import=rfq_import).exists():
            return Response({'error': 'This RFQ has already been promoted'}, status=status.HTTP_400_BAD_REQUEST)

        # Auto-copy values from RFQImportData into RFQManagementTable
        rfq_management = RFQManagement.objects.create(
            rfq_import=rfq_import,
            title=rfq_import.title,
            client_pr_number=rfq_import.client_pr_number,
            client_requestor_name=rfq_import.client_requestor_name,
            client_requestor_id=rfq_import.client_requestor_id,
            shipping_address=rfq_import.shipping_address,
            currency=rfq_import.currency,
            commodity_code=rfq_import.commodity_code,
            supplier_name=rfq_import.supplier_name,
            manufacturer_name=rfq_import.manufacturer_name,
            manufacturer_part_number=rfq_import.manufacturer_part_number,
            description=rfq_import.description,
            unit_price=rfq_import.unit_price,
            need_by_date=rfq_import.need_by_date,
            # Add more fields if needed
        )

        serializer = RFQManagementSerializer(rfq_management)
        return Response(serializer.data, status=status.HTTP_201_CREATED)