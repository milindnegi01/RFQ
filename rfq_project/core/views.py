from rest_framework import generics
from .models import CustomUser,Commodity,RFQImportData,RFQManagement,EndUserProfile, ClientAdminProfile , RFQEvent ,Supplier,SupplierResponse,SupplierResponseToken
from .serializers import CustomUserSerializer,EndUserCreateSerializer,SupplierCreateSerializer,SupplierSerializer,CustomTokenObtainPairSerializer,CommoditySerializer,RFQImportDataSerializer,RFQManagementSerializer,RFQExportSerializer,RFQEventSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import isclientadmin,isenduser , IsAnonymous
from rest_framework import filters,status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
import logging
logger = logging.getLogger(__name__)
from core.utils.email_utils import send_rfq_email_to_supplier
from django.db import models
from rest_framework import serializers
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import jwt
from rest_framework.decorators import action
from core.utils.email_utils import send_award_email_with_order


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
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated,isclientadmin]

    def get_queryset(self):
        return Supplier.objects.all()
    
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


# Add this login view to handle redirect for authenticated users
def login(request):
    pass  # Remove or comment out this function

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

# --- NEW VIEW: RFQPromotionView ---
class RFQPromotionView(APIView):
    permission_classes = [IsAuthenticated, isclientadmin]

    class InputSerializer(serializers.Serializer):
        rfq_import_id = serializers.IntegerField()
        supplier_ids = serializers.ListField(
            child=serializers.IntegerField(), required=False
        )

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rfq_import_id = serializer.validated_data['rfq_import_id']
        supplier_ids = serializer.validated_data.get('supplier_ids', [])

        # Get RFQImportData instance
        try:
            rfq_import = RFQImportData.objects.get(id=rfq_import_id)
        except RFQImportData.DoesNotExist:
            return Response({'error': 'RFQImportData not found'}, status=404)

        # Authorization check
        if rfq_import.created_by.organization != request.user.organization:
            return Response({'error': 'Not authorized to promote this RFQ'}, status=403)

        # Get or create the draft event for this RFQImportData
        rfq_event, created = RFQEvent.objects.get_or_create(
            rfq_import=rfq_import,
            defaults={'status': 'opened'}
        )
        if not created:
            rfq_event.status = 'opened'
            rfq_event.save()

        # Assign suppliers (if you want to store them, you need a M2M field on RFQEvent or RFQImportData)
        from core.models import Supplier
        suppliers = Supplier.objects.filter(id__in=supplier_ids)
        # If you want to store suppliers on the event, you need to add a M2M field to RFQEvent. For now, just send emails.
        for supplier in suppliers:
            if supplier.email_address:
                # Create or get an RFQManagement instance for this supplier and rfq_import
                rfq_management, _ = RFQManagement.objects.get_or_create(
                    rfq_import=rfq_import,
                    supplier_name=supplier.supplier_name,
                    supplier_code=supplier.supplier_code,
                    client_pr_number=rfq_import.client_pr_number,
                    client_requestor_name=rfq_import.client_requestor_name,
                    client_requestor_id=rfq_import.client_requestor_id,
                    client_item_code="N/A",  # or appropriate value
                    title=rfq_import.title,
                    shipping_address=rfq_import.shipping_address,
                    currency=rfq_import.Currency,
                    rfq_type="N/A",  # or appropriate value
                    assignee="N/A",  # or appropriate value
                    serial_number=int(rfq_import.serial_no) if str(rfq_import.serial_no).isdigit() else 1,
                    description=rfq_import.description,
                    need_by_date=rfq_import.need_by_date,
                    supplier_part_number=rfq_import.supplier_part_number,
                    commodity_code=rfq_import.commodity_code,
                    uom=rfq_import.uom,
                    manufacturer_name=rfq_import.manufacturer_name,
                    manufacturer_part_number=rfq_import.manufacturer_part_number,
                    unit_price=float(rfq_import.unit_price),
                    lead_time="",
                    inco_terms="",
                    payment_terms="",
                    freight="",
                )
                send_rfq_email_to_supplier(rfq_import, supplier)
                
        return Response({'status': 'RFQ promoted and emails sent.'}, status=200)
class RFQManagementCreateView(generics.CreateAPIView):
    queryset = RFQManagement.objects.all()
    serializer_class = RFQManagementSerializer  # ✅ Make sure this line is present
    permission_classes = [IsAuthenticated, isclientadmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Now the instance is saved, and M2M fields are set
        instance = serializer.instance
        # send_rfq_email_to_supplier(instance)
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class RFQManagementListView(generics.ListAPIView):
    queryset = RFQManagement.objects.all()
    serializer_class = RFQManagementSerializer
    permission_classes = [IsAuthenticated, isclientadmin]

class RFQManagementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RFQManagement.objects.all()
    serializer_class = RFQManagementSerializer
    permission_classes = [IsAuthenticated, isclientadmin]

class CancelRFQView(APIView):
    permission_classes = [IsAuthenticated, isclientadmin]

    def post(self, request, pk):
        rfq = get_object_or_404(RFQManagement, pk=pk)
        rfq.status = 'cancelled'
        rfq.save()
        return Response({'status': 'cancelled'}, status=status.HTTP_200_OK)

class ArchiveRFQView(APIView):
    permission_classes = [IsAuthenticated, isclientadmin]

    def post(self, request, pk):
        rfq = get_object_or_404(RFQManagement, pk=pk)
        rfq.status = 'archived'
        rfq.save()
        return Response({'status': 'archived'}, status=status.HTTP_200_OK)

class RFQEventListView(generics.ListAPIView):
    serializer_class = RFQEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'client_admin':
            # Client admin sees all RFQ events from their organization
            return RFQEvent.objects.filter(
                models.Q(rfq_import__created_by__organization=user.organization) |
                models.Q(rfq_management__rfq_import__created_by__organization=user.organization)
            ).select_related('rfq_import', 'rfq_management', 'rfq_import__created_by', 'rfq_management__rfq_import__created_by')
        
        elif user.role == 'end_user':
            # End user sees only their own RFQ events
            return RFQEvent.objects.filter(
                models.Q(rfq_import__created_by=user) |
                models.Q(rfq_management__rfq_import__created_by=user)
            ).select_related('rfq_import', 'rfq_management', 'rfq_import__created_by', 'rfq_management__rfq_import__created_by')
        
        else:
            # Other roles see no events
            return RFQEvent.objects.none()

class RFQEventDetailView(generics.RetrieveAPIView):
    serializer_class = RFQEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'client_admin':
            return RFQEvent.objects.filter(
                models.Q(rfq_import__created_by__organization=user.organization) |
                models.Q(rfq_management__rfq_import__created_by__organization=user.organization)
            ).select_related('rfq_import', 'rfq_management', 'rfq_import__created_by', 'rfq_management__rfq_import__created_by')
        
        elif user.role == 'end_user':
            return RFQEvent.objects.filter(
                models.Q(rfq_import__created_by=user) |
                models.Q(rfq_management__rfq_import__created_by=user)
            ).select_related('rfq_import', 'rfq_management', 'rfq_import__created_by', 'rfq_management__rfq_import__created_by')
        
        else:
            return RFQEvent.objects.none()

class RFQExportView(APIView):
    permission_classes = [IsAuthenticated,isclientadmin]

    def get(self,request,*args,**kwargs):
        rfqs = RFQManagement.objects.filter(rfq_status = 'closed')
        serializer = RFQExportSerializer(rfqs, many=True)
        return Response(serializer.data)
    
###################################################################################
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

class SupplierResponseFormView(View):
    def get(self, request, token):
        try:
            token_obj = SupplierResponseToken.objects.get(token=token)
        except SupplierResponseToken.DoesNotExist:
            return HttpResponse("Invalid or expired token", status=400)

        return render(request, 'supplier_response_form.html', {
            'token': token
        })

    def post(self, request, token):
        try:
            token_obj = SupplierResponseToken.objects.get(token=token)
        except SupplierResponseToken.DoesNotExist:
            return HttpResponse("Invalid or expired token", status=400)

        supplier = token_obj.supplier
        rfq = token_obj.rfq_import

        if SupplierResponse.objects.filter(rfq_import=rfq, supplier=supplier).exists():
            return HttpResponse("You have already submitted your response.", status=400)

        quoted_price = request.POST.get('quoted_price')
        lead_time = request.POST.get('lead_time')
        comments = request.POST.get('comments')

        SupplierResponse.objects.create(
            rfq_import=rfq,
            supplier=supplier,
            quoted_price=quoted_price,
            lead_time=lead_time,
            comments=comments
        )

        # Update RFQEvent supplier count
        event = RFQEvent.objects.get(rfq_import=rfq)
        event.supplier_responses = SupplierResponse.objects.filter(rfq_import=rfq).count()
        event.save()

        token_obj.is_used = True
        token_obj.save()

        return HttpResponse("Your response has been submitted successfully!")

# --- NEW: SupplierResponse Serializer ---
class SupplierResponseSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)
    supplier_code = serializers.CharField(source='supplier.supplier_code', read_only=True)
    class Meta:
        model = SupplierResponse
        fields = ['id', 'rfq_import', 'supplier', 'supplier_name', 'supplier_code', 'quoted_price', 'lead_time', 'comments', 'created_at']

# --- NEW: View all supplier responses for a specific RFQImportData ---
class SupplierResponseListByRFQView(generics.ListAPIView):
    serializer_class = SupplierResponseSerializer
    permission_classes = [IsAuthenticated, isclientadmin]

    def get_queryset(self):
        rfq_import_id = self.kwargs['rfq_import_id']
        # Only allow client admins to view responses for RFQs in their org
        rfq = get_object_or_404(RFQImportData, id=rfq_import_id, created_by__organization=self.request.user.organization)
        return SupplierResponse.objects.filter(rfq_import=rfq)

# --- NEW: Award a supplier for an RFQImportData ---

from core.utils.email_utils import send_award_email_to_supplier


class AwardSupplierView(APIView):
    permission_classes = [IsAuthenticated, isclientadmin]

    class InputSerializer(serializers.Serializer):
        rfq_import_id = serializers.IntegerField()
        supplier_id = serializers.IntegerField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rfq_import_id = serializer.validated_data['rfq_import_id']
        supplier_id = serializer.validated_data['supplier_id']

        rfq_import = get_object_or_404(RFQImportData, id=rfq_import_id, created_by__organization=request.user.organization)
        supplier = get_object_or_404(Supplier, id=supplier_id)

        # Find or create the RFQManagement for this supplier and RFQImportData
        rfq_management = RFQManagement.objects.filter(rfq_import=rfq_import, supplier_code=supplier.supplier_code).first()
        if not rfq_management:
            return Response({'error': 'No RFQManagement found for this supplier and RFQ.'}, status=404)

        # Set awarded_supplier and status
        rfq_management.awarded_supplier = supplier
        rfq_management.status = 'awarded'
        rfq_management.save()

        # Update the RFQEvent status to 'awarded'
        try:
            event = RFQEvent.objects.get(rfq_import=rfq_import)
            event.status = 'awarded'
            event.save()
        except RFQEvent.DoesNotExist:
            pass

        # --- Send award email to supplier ---
        send_award_email_with_order(rfq_import, supplier, rfq_management)

        return Response({'status': 'Supplier awarded and RFQ marked as awarded.'}, status=200)
# --- NEW: RFQ with Supplier Responses View ---
class RFQWithResponsesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, isclientadmin]
    
    class RFQWithResponsesSerializer(serializers.ModelSerializer):
        supplier_responses = serializers.SerializerMethodField()
        
        class Meta:
            model = RFQImportData
            fields = ['id', 'title', 'client_pr_number', 'description', 'need_by_date', 'supplier_responses']
        
        def get_supplier_responses(self, obj):
            responses = SupplierResponse.objects.filter(rfq_import=obj)
            return [{
                'id': resp.id,
                'supplier_id': resp.supplier.id,
                'supplier_name': resp.supplier.supplier_name,
                'supplier_code': resp.supplier.supplier_code,
                'quoted_price': str(resp.quoted_price),
                'lead_time': resp.lead_time,
                'comments': resp.comments,
                'created_at': resp.created_at
            } for resp in responses]
    
    serializer_class = RFQWithResponsesSerializer
    
    def get_queryset(self):
        # Get RFQs from client admin's organization that have supplier responses
        return RFQImportData.objects.filter(
            created_by__organization=self.request.user.organization,
            supplierresponse__isnull=False
        ).distinct()