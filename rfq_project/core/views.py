from rest_framework import generics
from .models import CustomUser,Commodity
from .serializers import CustomUserSerializer,EndUserCreateSerializer,SupplierCreateSerializer,CustomTokenObtainPairSerializer,CommoditySerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import isclientadmin
from rest_framework import filters
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
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

# class ListClientAdminView(generics.ListAPIView):
#     serializer_class = CustomUserSerializer
#     permission_classes = [IsAuthenticated,ismateradmin]

#     def get_queryset(self):
#         return CustomUser.objects.filter(role='client_admin')

class ListEndUserView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,isclientadmin]

    def get_queryset(self):
        return CustomUser.objects.filter(role='end_user')

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