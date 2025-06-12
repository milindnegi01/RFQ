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
    class Meta:
        model = Supplier
        fields = ['supplier_code','supplier_name','supplier_address','city','country','country_code','incoterms','payment_terms','primary_contact_name','email_address','contact_number','gst']


class SupplierCreateSerializer(serializers.ModelSerializer):
    supplier_profile = SupplierSerializer

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
    class Meta:
        model = RFQManagement
        fields = '__all__'


