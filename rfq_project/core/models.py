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

    def __str__(self):
        return f"{self.username}({self.get_role_display()})"

class ClientAdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='client_admin_profile')
    client_id = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    client_org_address = models.TextField()


class EndUserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='end_user_profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"

# Create your models here.
