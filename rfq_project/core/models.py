from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('master_admin', 'Master Admin'),
        ('client_admin', 'Client Admin'),
        ('end_user', 'End User'),
        ('supplier', 'Supplier')
    ]
    role=models.CharField(max_length=20, choices=ROLE_CHOICES)
    organization= models.CharField(max_length=255, blank=True,null=True) # fro the client and supplier

    client_admin = models.ForeignKey('self', 
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=True,
                                   related_name='end_users',
                                   limit_choices_to={'role': 'client_admin'})
    def __str__(self):
        return f"{self.username}({self.get_role_display()})"
    def save(self, *args, **kwargs):
        # If this is an end user and has an organization but no client_admin
        if self.role == 'end_user' and self.organization and not self.client_admin:
            # Try to find a client admin with the same organization
            client_admin = CustomUser.objects.filter(
                role='client_admin',
                organization=self.organization
            ).first()
            if client_admin:
                self.client_admin = client_admin
        super().save(*args, **kwargs)

class ClientAdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='client_admin_profile')
    client_id = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    client_org_address = models.TextField()
    organization_name = models.CharField(max_length=255 , default='')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"


class EndUserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='end_user_profile', null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, default='')
    client_admin = models.ForeignKey(ClientAdminProfile, on_delete=models.CASCADE, related_name='end_users', null=True, blank=True)
    username = models.CharField(max_length=255)  # Now required
    email = models.EmailField(null=True, blank=True)  # Keep email optional
    password = models.CharField(max_length=255,help_text="Hashed password from CustomUser")  # Now required

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username if self.user else self.username})"
class Supplier(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name="supplier_profile")
    supplier_code = models.CharField(max_length=50, unique=True)
    supplier_name = models.CharField(max_length=255)
    supplier_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)
    incoterms = models.CharField(max_length=50)
    payment_terms = models.CharField(max_length=100)
    primary_contact_name = models.CharField(max_length=255)
    email_address = models.EmailField()
    contact_number = models.CharField(max_length=20)
    gst = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.supplier_name} ({self.supplier_code})"
# Create your models here.

from django.db import migrations

def set_default_credentials(apps, schema_editor):
    EndUserProfile = apps.get_model('core', 'EndUserProfile')
    for profile in EndUserProfile.objects.all():
        if not profile.username:
            profile.username = f"user_{profile.id}"
        if not profile.password:
            profile.password = "changeme123"  # Default password that should be changed
        profile.save()

class Migration(migrations.Migration):
    dependencies = [
        ('core', 'previous_migration'),  # This will be automatically filled
    ]

    operations = [
        migrations.RunPython(set_default_credentials),
    ]
##commodity list models
class Commodity(models.Model):
    commodity_code = models.CharField(max_length=50, unique = True)
    commodity_name = models.CharField(max_length=225)

    def __str__(self):
        return f"{self.commodity_name}({self.commodity_code})"
    
##end - user
class RFQImportData(models.Model):
    created_by = models.ForeignKey(CustomUser , on_delete=models.CASCADE)
    client_pr_number = models.CharField(max_length=100)
    client_requestor_name = models.CharField(max_length=100)
    client_requestor_id = models.CharField(max_length=100)
    client_code = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    shipping_address = models.TextField(max_length=100)
    Currency = models.CharField(max_length=100)
    serial_no = models.CharField(max_length=100)
    description = models.TextField()
    need_by_date = models.DateField()
    supplier_part_number = models.CharField(max_length=100)
    drawing_number = models.CharField(max_length=100, blank=True, null=True)
    commodity_code = models.CharField(max_length=50)
    uom = models.CharField(max_length=50)  # Unit of Measure
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    supplier_name = models.CharField(max_length=100)
    manufacturer_name = models.CharField(max_length=100)
    manufacturer_part_number = models.CharField(max_length=100)  

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title 

class RFQManagement(models.Model):
    rfq_import = models.ForeignKey('RFQImportData', on_delete=models.CASCADE, related_name='rfq_management', null=True, blank=True)
    client_pr_number = models.CharField(max_length=100)
    client_requestor_name = models.CharField(max_length=100)
    client_requestor_id = models.CharField(max_length=100)
    client_item_code = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    shipping_address = models.TextField()
    currency = models.CharField(max_length=20)
    rfq_type = models.CharField(max_length=50)
    assignee = models.CharField(max_length=100)
    serial_number = models.IntegerField()
    description = models.TextField()
    need_by_date = models.DateField()
    supplier_part_number = models.CharField(max_length=100)
    commodity_code = models.CharField(max_length=100)
    uom = models.CharField(max_length=20)
    manufacturer_name = models.CharField(max_length=100)
    manufacturer_part_number = models.CharField(max_length=100)
    benchmark_price = models.FloatField()
    rfq_status = models.CharField(max_length=100)
    supplier_code = models.CharField(max_length=100)
    supplier_name = models.CharField(max_length=100)
    unit_price = models.FloatField()
    lead_time = models.CharField(max_length=50)
    inco_terms = models.CharField(max_length=50)
    payment_terms = models.CharField(max_length=100)
    freight = models.CharField(max_length=50)
    alternative_part_number = models.CharField(max_length=100, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    chat_box_comments = models.TextField(blank=True, null=True)
    rfq_received_date = models.DateField(blank=True, null=True)
    rfq_opened_date = models.DateField(blank=True, null=True)
    rfq_closed_date = models.DateField(blank=True, null=True)
    rfq_award_date = models.DateField(blank=True, null=True)
    awarded_price = models.FloatField(blank=True, null=True)
    rfq_archived_date = models.DateField(blank=True, null=True)
    rfq_cancelled_date = models.DateField(blank=True, null=True)
    reason_for_cancel = models.TextField(blank=True, null=True)
    reason_for_archive = models.TextField(blank=True, null=True)
    bidding_declined = models.CharField(max_length=50, blank=True, null=True)
    rfq_reopened_date_1 = models.DateField(blank=True, null=True)
    rfq_closed_date_1 = models.DateField(blank=True, null=True)
    rfq_reopened_date_2 = models.DateField(blank=True, null=True)
    rfq_closed_date_2 = models.DateField(blank=True, null=True)
    rfq_reopened_date_3 = models.DateField(blank=True, null=True)
    rfq_closed_date_3 = models.DateField(blank=True, null=True)
    savings = models.FloatField(blank=True, null=True)
    savings_percent = models.FloatField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client_pr_number



