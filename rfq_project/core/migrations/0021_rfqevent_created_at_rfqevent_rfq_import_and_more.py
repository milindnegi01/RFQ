# Generated by Django 4.2.21 on 2025-06-21 09:51

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_rfqevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfqevent',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rfqevent',
            name='rfq_import',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='core.rfqimportdata'),
        ),
        migrations.AddField(
            model_name='rfqevent',
            name='rfq_management',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='core.rfqmanagement'),
        ),
        migrations.AlterField(
            model_name='rfqevent',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('opened', 'Opened'), ('closed', 'Closed'), ('awarded', 'Awarded'), ('cancelled', 'Cancelled'), ('archived', 'Archived')], default='draft', max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='rfqevent',
            unique_together={('rfq_import', 'rfq_management')},
        ),
        migrations.RemoveField(
            model_name='rfqevent',
            name='rfq',
        ),
    ]
