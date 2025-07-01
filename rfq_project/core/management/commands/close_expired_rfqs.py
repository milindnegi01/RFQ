from django.core.management.base import BaseCommand
from core.models import RFQManagement
from django.utils import timezone

class Command(BaseCommand):
    help = 'Closes all opened RFQs whose need_by_date has passed'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        rfqs = RFQManagement.objects.filter(status='opened', need_by_date__lt=today)
        count = rfqs.update(status='closed')
        self.stdout.write(self.style.SUCCESS(f'Closed {count} expired RFQs.')) 