from rest_framework import generics
from .models import CustomUser
from .serializers import CustomUserSerializer,ClientAdminCreateSerializer,EndUserCreateSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import ismateradmin,isclientadmin
from rest_framework import filters
from rest_framework.authtoken.views import ObtainAuthToken

#Master Admin rights        
class CreateMasterAdminView(generics.ListCreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,ismateradmin]

    def perform_create(self, serializer):
        serializer.save(role='master_admin')

class CreateClientAdminView(generics.CreateAPIView):
    serializer_class = ClientAdminCreateSerializer
    permission_classes = [IsAuthenticated,ismateradmin]

    def perform_create(self, serializer):
        serializer.save(role='client_admin')

class CreateSupplierView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,ismateradmin |isclientadmin]

    def perform_create(self, serializer):
        serializer.save(role='supplier')

class CreateEndUserView(generics.CreateAPIView):
    serializer_class = EndUserCreateSerializer
    permission_classes = [IsAuthenticated,ismateradmin | isclientadmin]

    def perform_create(self, serializer):
        serializer.save(role='end_user')

class ListClientAdminView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,ismateradmin]

    def get_queryset(self):
        return CustomUser.objects.filter(role='client_admin')

class ListEndUserView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,ismateradmin | isclientadmin]

    def get_queryset(self):
        return CustomUser.objects.filter(role='end_user')

class ListSupplierView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,ismateradmin,isclientadmin]

    def get_queryset(self):
        return CustomUser.objects.filter(role='supplier')
    
##CRUD OPERATION FOR ADMIN 
class RetrieveUserView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,ismateradmin | isclientadmin]
    def get_queryset(self):
        if self.request.user.role == 'client_admin':
            return CustomUser.objects.filter(organization=self.request.user.organization,role__in=['supplier','end_user'])
        return CustomUser.objects.all()

class UpdateUserView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,ismateradmin | isclientadmin]
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
    permission_classes = [IsAuthenticated,ismateradmin | isclientadmin]
    def get_queryset(self):
        if self.request.user.role == 'client_admin':
            return CustomUser.objects.filter(organization=self.request.user.organization,role__in=['supplier','end_user'])
        return CustomUser.objects.all()

class OrganizationUserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated,ismateradmin | isclientadmin]
    def get_queryset(self):
        org = self.kwargs['org_name']
        if self.request.user.role == 'client_admin':
            if org != self.request.user.organization:
                raise CustomUser.objects.none()
            return CustomUser.objects.filter(organization=org,role__in=['supplier','end_user'])
        return CustomUser.objects.filter(organization=org,role__in=['client_admin','supplier','end_user'])

# Create your views here.
    