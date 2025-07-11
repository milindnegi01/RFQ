# Generated by Django 4.2.21 on 2025-06-04 09:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_enduserprofile_password_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='client_admin',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'client_admin'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='end_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='enduserprofile',
            name='password',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='enduserprofile',
            name='username',
            field=models.CharField(max_length=255),
        ),
    ]
