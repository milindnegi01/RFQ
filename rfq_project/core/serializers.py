from rest_framework import serializers
from .models import CustomUser,ClientAdminProfile,EndUserProfile

class ClientAdminProfileSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ClientAdminProfile
        fields = ['client_id','first_name','last_name','contact_number','client_org_address']

class ClientAdminCreateSerializer(serializers.ModelSerializer):
    client_admin_profile = ClientAdminProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['username','email','password','role','organization','client_admin_profile']
        extra_kwargs = {
            'password':{'write_only':True},
            'role':{'read_only':True},
            }
    def create(self, validated_data):
        profile_data = validated_data.pop('client_admin_profile')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.role = 'client_admin'
        user.save()
        ClientAdminProfile.objects.create(user=user,**profile_data)
        return user
        
            
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
        }
    def create(self, validated_data):   
        profile_data = validated_data.pop('end_user_profile',None)
        password = validated_data.pop('password',None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.role = 'end_user'
        user.save()
        if profile_data:
            EndUserProfile.objects.create(user=user,**profile_data)
        return user




