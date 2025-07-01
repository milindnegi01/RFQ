from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ClientAdminProfile, EndUserProfile, Supplier,Commodity,RFQImportData,RFQEvent

class EndUserProfileInline(admin.StackedInline):
    model = EndUserProfile
    can_delete = False
    verbose_name_plural = 'End User Profile'
    fields = ('first_name','last_name','contact_number')

class ClientAdminProfileInline(admin.StackedInline):
    model = ClientAdminProfile
    can_delete = False
    verbose_name_plural = 'Client Admin Profile'
    fields = ('contact_number',)

class SupplierProfileInline(admin.StackedInline):
    model = Supplier
    can_delete = False
    verbose_name_plural = 'Supplier Profile'
    fields = ('supplier_code', 'supplier_name', 'supplier_address', 'city', 'state', 
              'country', 'country_code', 'incoterms', 'payment_terms', 'primary_contact_name',
              'email_address', 'contact_number', 'gst')

class CustomUserAdmin(UserAdmin):
    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        inlines = []
        if obj.role == 'client_admin':
            inlines.append(ClientAdminProfileInline(self.model, self.admin_site))
        elif obj.role == 'end_user':
            inlines.append(EndUserProfileInline(self.model, self.admin_site))
        elif obj.role == 'supplier':
            inlines.append(SupplierProfileInline(self.model, self.admin_site))
        return inlines
    
    # Fields to show in the list view
    list_display = ('username', 'email', 'get_contact_number', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'client_admin_profile__first_name', 
                    'client_admin_profile__last_name', 'client_admin_profile__contact_number',
                    'supplier_profile__supplier_name', 'supplier_profile__supplier_code')
    ordering = ('username',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'client_admin':
            return qs.filter(organization=request.user.organization)
        return qs

    # Fields to show in the add/edit form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'organization')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields to show in the add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'organization', 'role'),
        }),
    )

    def get_first_name(self, obj):
        if obj.role == 'end_user':
            return obj.end_user_profile.first_name if hasattr(obj,'end_user_profile') else ''
        elif obj.role == 'supplier':
            return obj.supplier_profile.primary_contact_name if hasattr(obj,'supplier_profile') else ''
        return obj.client_admin_profile.first_name if hasattr(obj, 'client_admin_profile') else ''
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        if obj.role == 'end_user':
            return obj.end_user_profile.first_name if hasattr(obj,'end_user_profile') else ''
        elif obj.role == 'supplier':
            return obj.supplier_profile.supplier_name if hasattr(obj,'supplier_profile') else ''
        return obj.client_admin_profile.last_name if hasattr(obj, 'client_admin_profile') else ''
    get_last_name.short_description = 'Last Name'

    def get_contact_number(self, obj):
        if obj.role == 'end_user':
            return obj.end_user_profile.contact_number if hasattr(obj,'end_user_profile') else ''
        elif obj.role == 'supplier':
            return obj.supplier_profile.contact_number if hasattr(obj,'supplier_profile') else ''
        return obj.client_admin_profile.contact_number if hasattr(obj, 'client_admin_profile') else ''
    get_contact_number.short_description = 'Contact Number'

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.role == 'end_user':
            # Add client_admin field to end users
            fieldsets = list(fieldsets)
            for i, (name, fieldset) in enumerate(fieldsets):
                if name == 'Personal info':
                    fields = list(fieldset['fields'])
                    fields.append('client_admin')
                    fieldsets[i] = (name, {'fields': fields})
        return fieldsets

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        # If this is a new user with role 'client_admin', create the profile
        if is_new: 
            if obj.role == 'client_admin':
                ClientAdminProfile.objects.get_or_create(
                    user=obj,
                    defaults={
                        'client_id': f"CA{obj.id}",  # Generate a client ID
                        'first_name': obj.first_name,
                        'last_name': obj.last_name,
                        'contact_number': '',  # Default empty
                        'client_org_address': obj.organization or ''  # Use organization as address
                    }
                )
            elif obj.role == 'end_user':
                # Create end user profile only if it doesn't exist
                if not hasattr(obj, 'end_user_profile'):
                    EndUserProfile.objects.create(
                        user=obj,
                        first_name=obj.first_name,
                        last_name=obj.last_name,
                        contact_number='',
                        organization=obj.organization,
                        username=obj.username,
                        email=obj.email,
                        password=obj.password
                    )
            elif obj.role == 'supplier':
                # Create supplier profile
                Supplier.objects.get_or_create(
                    user=obj,
                    defaults={
                        'supplier_code': f"SUP{obj.id}",
                        'supplier_name': obj.organization or '',
                        'supplier_address': '',
                        'city': '',
                        'state': '',
                        'country': '',
                        'country_code': '',
                        'incoterms': '',
                        'payment_terms': '',
                        'primary_contact_name': obj.first_name,
                        'email_address': obj.email,
                        'contact_number': '',
                        'gst': ''
                    }
                )
        else:
            # Handle updates for existing users
            if obj.role == 'end_user' and obj.organization:
                # Update client admin association
                client_admin = CustomUser.objects.filter(
                    role='client_admin',
                    organization=obj.organization
                ).first()
                if client_admin:
                    obj.client_admin = client_admin
                    obj.save()
                
                # Update end user profile if it exists
                if hasattr(obj, 'end_user_profile'):
                    obj.end_user_profile.organization = obj.organization
                    obj.end_user_profile.save()

        if obj.organization:
            client_admin = CustomUser.objects.filter(
                role='client_admin',
                organization=obj.organization
            ).first()
            if client_admin:
                obj.client_admin = client_admin
                obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'client_admin':
            # Show only end users belonging to this client admin
            return qs.filter(
                models.Q(organization=request.user.organization) |
                models.Q(client_admin=request.user)
            )
        return qs

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_code', 'supplier_name', 'city', 'country', 'primary_contact_name', 'email_address', 'contact_number')
    list_filter = ('country', 'city', 'state')
    search_fields = ('supplier_code', 'supplier_name', 'primary_contact_name', 'email_address', 'contact_number')
    ordering = ('supplier_code',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('supplier_code', 'supplier_name', 'supplier_address')
        }),
        ('Location', {
            'fields': ('city', 'state', 'country', 'country_code')
        }),
        ('Business Details', {
            'fields': ('incoterms', 'payment_terms', 'gst')
        }),
        ('Contact Information', {
            'fields': ('primary_contact_name', 'email_address', 'contact_number')
        }),
    )

class EndUserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'first_name', 'last_name', 'contact_number', 
                   'organization', 'get_client_admin')
    list_filter = ('organization', 'user__client_admin')
    search_fields = ('first_name', 'last_name', 'contact_number', 
                    'user__username', 'organization')
    ordering = ('organization', 'first_name')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__username'

    def get_organization(self, obj):
        return obj.user.organization
    get_organization.short_description = 'Organization'
    get_organization.admin_order_field = 'user__organization'

    def get_client_admin(self, obj):
        if obj.user.client_admin:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/core/customuser/{obj.user.client_admin.id}/change/',
                obj.user.client_admin.username
            )
        return '-'
    get_client_admin.short_description = 'Client Admin'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'client_admin':
            return qs.filter(user__organization=request.user.organization)
        return qs

class ClientAdminProfileAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'get_first_name', 'get_last_name', 'get_email', 'contact_number', 'client_org_address')
    list_filter = ('client_org_address',)
    search_fields = ('client_id', 'first_name', 'last_name', 'contact_number', 'client_org_address')
    ordering = ('client_id',)

    def get_first_name(self, obj):
        return obj.first_name
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'first_name'

    def get_last_name(self, obj):
        return obj.last_name
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'last_name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email Address'
    get_email.admin_order_field = 'user__email'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'client_admin':
            return qs.filter(user=request.user)
        return qs
    
class RFQImportDataAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_pr_number', 'client_requestor_name', 'client_code', 'need_by_date', 'created_at')
    list_filter = ('client_code', 'created_at', 'need_by_date')
    search_fields = ('title', 'client_pr_number', 'client_requestor_name', 'client_code', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'client_pr_number', 'client_requestor_name', 'client_requestor_id', 'client_code')
        }),
        ('Shipping Details', {
            'fields': ('shipping_address', 'need_by_date', 'Currency')
        }),
        ('Product Details', {
            'fields': ('serial_no', 'description', 'supplier_part_number', 'drawing_number', 
                      'commodity_code', 'uom', 'unit_price')
        }),
        ('Supplier Information', {
            'fields': ('supplier_name', 'manufacturer_name', 'manufacturer_part_number')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'client_admin':
            # Show RFQs for the client admin's organization
            return qs.filter(created_by__organization=request.user.organization)
        elif request.user.role == 'end_user':
            # Show only RFQs created by the end user
            return qs.filter(created_by=request.user)
        return qs

    def has_add_permission(self, request):
        # Only end users can create RFQs
        return request.user.role == 'end_user'

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        # Only the creator or client admin can modify
        return (obj.created_by == request.user or 
                (request.user.role == 'client_admin' and 
                 obj.created_by.organization == request.user.organization))

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        # Only the creator or client admin can delete
        return (obj.created_by == request.user or 
                (request.user.role == 'client_admin' and 
                 obj.created_by.organization == request.user.organization))
    
@admin.register(RFQEvent)
class RFQEventAdmin(admin.ModelAdmin):
    list_display = ['get_rfq_title', 'get_client_pr_number', 'status', 'supplier_responses', 'last_updated']
    list_filter = ['status', 'created_at', 'last_updated']
    search_fields = ['rfq_import__title', 'rfq_management__title', 'rfq_import__client_pr_number', 'rfq_management__client_pr_number']
    readonly_fields = ['created_at', 'last_updated']
    
    fieldsets = (
        ('RFQ Information', {
            'fields': ('rfq_import', 'rfq_management')
        }),
        ('Event Details', {
            'fields': ('status', 'supplier_responses')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated')
        }),
    )

    def get_rfq_title(self, obj):
        return obj.rfq_title
    get_rfq_title.short_description = 'RFQ Title'
    get_rfq_title.admin_order_field = 'rfq_import__title'

    def get_client_pr_number(self, obj):
        return obj.client_pr_number
    get_client_pr_number.short_description = 'Client PR Number'
    get_client_pr_number.admin_order_field = 'rfq_import__client_pr_number'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'client_admin':
            # Show RFQ events for the client admin's organization
            return qs.filter(
                models.Q(rfq_import__created_by__organization=request.user.organization) |
                models.Q(rfq_management__rfq_import__created_by__organization=request.user.organization)
            )
        elif request.user.role == 'end_user':
            # Show only RFQ events created by the end user
            return qs.filter(
                models.Q(rfq_import__created_by=request.user) |
                models.Q(rfq_management__rfq_import__created_by=request.user)
            )
        return qs

# Add this line at the end of the file with the other registrations
admin.site.register(RFQImportData, RFQImportDataAdmin)
# Register your models with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(EndUserProfile, EndUserProfileAdmin)
admin.site.register(ClientAdminProfile, ClientAdminProfileAdmin)
admin.site.register(Supplier, SupplierAdmin)
