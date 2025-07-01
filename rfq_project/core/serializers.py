from rest_framework import serializers
from .models import CustomUser,ClientAdminProfile,EndUserProfile,Supplier,Commodity,RFQImportData,RFQManagement
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Print the username being used for authentication
        print(f"Attempting to authenticate user: {attrs.get('username')}")
        
        data = super().validate(attrs)
        
        # Print the authenticated user's details
        print(f"Successfully authenticated user: {self.user.username}")
        print(f"User role: {self.user.role}")
        
        # Add custom claims
        data['message'] = f"welcome {self.user.get_role_display()}"
        data['role'] = self.user.role
        data['username'] = self.user.username
        return data
# class ClientAdminProfileSerializer(serializers.ModelSerializer):
#     class Meta: 
#         model = ClientAdminProfile
#         fields = ['client_id','first_name','last_name','contact_number','client_org_address']

# class ClientAdminCreateSerializer(serializers.ModelSerializer):
#     client_admin_profile = ClientAdminProfileSerializer()

#     class Meta:
#         model = CustomUser
#         fields = ['username','email','password','role','organization','client_admin_profile']
#         extra_kwargs = {
#             'password':{'write_only':True},
#             'role':{'read_only':True},
#             }
#     def create(self, validated_data):
#         profile_data = validated_data.pop('client_admin_profile')
#         password = validated_data.pop('password')
#         user = CustomUser(**validated_data)
#         user.set_password(password)
#         user.role = 'client_admin'
#         user.save()
#         ClientAdminProfile.objects.create(user=user,**profile_data)
#         return user
        
            
class CustomUserSerializer(serializers.ModelSerializer):
    # client_admin_profile = ClientAdminProfileSerializer()
    class Meta:
        model = CustomUser
        fields = ['id','username','email','password','role','organization']
        extra_fields = {
            'password':{'write_only':True},
            'role':{'read_only':True},
            }
        extra_kwargs = {'password':{'write_only':True}}

class EndUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndUserProfile
        fields = ['first_name','last_name','contact_number']

class EndUserCreateSerializer(serializers.ModelSerializer):
    end_user_profile = EndUserProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id','username','email','password','role','organization','end_user_profile']
        extra_kwargs = {
            'password':{'write_only':True},
            'role':{'read_only':True},
            'organization':{'read_only':True}
        }
    def create(self, validated_data):   
        profile_data = validated_data.pop('end_user_profile')
        password = validated_data.pop('password')
        
        # Get the client admin's organization from the request
        client_admin = self.context['request'].user
        validated_data['organization'] = client_admin.organization
        
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.role = 'end_user'
        user.save()
        
        # Set the client admin relationship
        user.client_admin = client_admin
        user.save()
        
        if profile_data:
            EndUserProfile.objects.create(
                user=user,
                client_admin=client_admin.client_admin_profile,
                organization=client_admin.organization,  # Set organization here too
                password=user.password,
                **profile_data
            )
        return user
    
class SupplierSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Supplier
        fields = [
            'id', 'user_id', 'username',
            'supplier_code','supplier_name','supplier_address','city','country','country_code',
            'incoterms','payment_terms','primary_contact_name','email_address','contact_number','gst'
        ]


class SupplierCreateSerializer(serializers.ModelSerializer):
    supplier_profile = SupplierSerializer()

    class Meta:
        model = CustomUser
        fields = ['username','email','password','role','organization','supplier_profile']
        extra_kwargs = {
            'password':{'write_only':True},
            'role':{'read_only':True}
        }
    def create(self, validated_data):
        profile_data = validated_data.pop('supplier_profile')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.role = 'supplier'
        user.save()
        Supplier.objects.create(user=user, **profile_data)
        return user
    
##commodity serializer
class CommoditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ['id','commodity_code','commodity_name']

class RFQImportDataSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_organization = serializers.CharField(source='created_by.organization', read_only=True)
    
    class Meta:
        model = RFQImportData
        fields = '__all__'


class RFQManagementSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    awarded_supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), required=False, allow_null=True)
    rfq_import_id = serializers.IntegerField(write_only=True, required=False)
    
    # Make auto-filled fields read-only
    title = serializers.CharField(read_only=True)
    client_pr_number = serializers.CharField(read_only=True)
    client_requestor_name = serializers.CharField(read_only=True)
    client_requestor_id = serializers.CharField(read_only=True)
    shipping_address = serializers.CharField(read_only=True)
    currency = serializers.CharField(read_only=True)
    commodity_code = serializers.CharField(read_only=True)
    supplier_name = serializers.CharField(read_only=True)
    manufacturer_name = serializers.CharField(read_only=True)
    manufacturer_part_number = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    unit_price = serializers.FloatField(read_only=True)
    need_by_date = serializers.DateField(read_only=True)
    supplier_part_number = serializers.CharField(read_only=True)
    uom = serializers.CharField(read_only=True)
    serial_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = RFQManagement
        fields = '__all__'
        read_only_fields = ['status']

    def create(self, validated_data):
        # Always set status to 'opened' on creation
        validated_data['status'] = 'opened'
        rfq_import_id = validated_data.pop('rfq_import_id', None)
        
        if rfq_import_id:
            try:
                rfq_import = RFQImportData.objects.get(id=rfq_import_id)
                
                # Auto-fill all common fields from RFQImportData
                validated_data.update({
                    'rfq_import': rfq_import,
                    'title': rfq_import.title,
                    'client_pr_number': rfq_import.client_pr_number,
                    'client_requestor_name': rfq_import.client_requestor_name,
                    'client_requestor_id': rfq_import.client_requestor_id,
                    'shipping_address': rfq_import.shipping_address,
                    'currency': rfq_import.Currency,  # Note: Currency vs currency
                    'commodity_code': rfq_import.commodity_code,
                    'supplier_name': rfq_import.supplier_name,
                    'manufacturer_name': rfq_import.manufacturer_name,
                    'manufacturer_part_number': rfq_import.manufacturer_part_number,
                    'description': rfq_import.description,
                    'unit_price': float(rfq_import.unit_price),  # Convert Decimal to float
                    'need_by_date': rfq_import.need_by_date,
                    'supplier_part_number': rfq_import.supplier_part_number,
                    'uom': rfq_import.uom,
                    'serial_number': int(rfq_import.serial_no) if rfq_import.serial_no.isdigit() else 1,
                })
                
                print(f"Auto-filled RFQ Management with data from RFQ Import ID: {rfq_import_id}")
                print(f"Title: {validated_data.get('title')}")
                print(f"Client PR Number: {validated_data.get('client_pr_number')}")
                
            except RFQImportData.DoesNotExist:
                raise serializers.ValidationError(f"RFQ Import with ID {rfq_import_id} does not exist")

        return super().create(validated_data)

    def to_representation(self, instance):
        """Custom representation to show which fields are auto-filled"""
        data = super().to_representation(instance)
        
        # Add a flag to indicate if this RFQ was created from an import
        if instance.rfq_import:
            data['is_from_import'] = True
            data['source_rfq_import_id'] = instance.rfq_import.id
            data['source_rfq_import_title'] = instance.rfq_import.title
        else:
            data['is_from_import'] = False
            
        return data

from .models import RFQEvent

class RFQEventSerializer(serializers.ModelSerializer):
    rfq_title = serializers.CharField(read_only=True)
    client_pr_number = serializers.CharField(read_only=True)
    created_by_username = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    
    class Meta:
        model = RFQEvent
        fields = [
            'id', 
            'rfq_import', 
            'rfq_management', 
            'rfq_title',
            'client_pr_number',
            'status', 
            'supplier_responses', 
            'last_updated',
            'created_at',
            'created_by_username',
            'organization'
        ]
    
    def get_created_by_username(self, obj):
        if obj.rfq_import:
            return obj.rfq_import.created_by.username
        elif obj.rfq_management and obj.rfq_management.rfq_import:
            return obj.rfq_management.rfq_import.created_by.username
        return "Unknown"
    
    def get_organization(self, obj):
        if obj.rfq_import:
            return obj.rfq_import.created_by.organization
        elif obj.rfq_management and obj.rfq_management.rfq_import:
            return obj.rfq_management.rfq_import.created_by.organization
        return "Unknown"



class RFQExportSerializer(serializers.ModelSerializer):
    class Meta :
        model = RFQManagement
        fields = [
            'client_requestor_id',
            'client_code',
            'description',
            'need_by_date',
            'supplier_part_number',
            'commodity_code',
            'uom',
            'unit_price',
            'supplier_name',
            'manufacturer_name',
            'manufacturer_part_number'
        ]

from .models import RFQEvent
from .models import SupplierResponse

class SupplierResponseSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)
    supplier_code = serializers.CharField(source='supplier.supplier_code', read_only=True)
    class Meta:
        model = SupplierResponse
        fields = ['id', 'rfq_import', 'supplier', 'supplier_name', 'supplier_code', 'quoted_price', 'lead_time', 'comments', 'created_at']

