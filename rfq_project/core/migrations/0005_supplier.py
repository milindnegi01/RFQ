# Generated by Django 4.2.21 on 2025-06-04 05:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_enduserprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supplier_code', models.CharField(max_length=50, unique=True)),
                ('supplier_name', models.CharField(max_length=255)),
                ('supplier_address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('country_code', models.CharField(max_length=10)),
                ('incoterms', models.CharField(max_length=50)),
                ('payment_terms', models.CharField(max_length=100)),
                ('primary_contact_name', models.CharField(max_length=255)),
                ('email_address', models.EmailField(max_length=254)),
                ('contact_number', models.CharField(max_length=20)),
                ('gst', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
