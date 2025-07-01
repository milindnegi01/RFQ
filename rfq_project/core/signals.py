from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import RFQManagement, RFQEvent, RFQImportData

@receiver(post_save, sender=RFQImportData)
def create_rfq_import_event(sender, instance, created, **kwargs):
    """Create event when RFQImportData is created (draft status)"""
    if created:
        RFQEvent.objects.create(
            rfq_import=instance,
            status='draft'
        )

@receiver(post_save, sender=RFQManagement)
def create_or_update_rfq_management_event(sender, instance, created, **kwargs):
    """Create or update event when RFQManagement is created/updated"""
    if created:
        # If this RFQManagement is created from an RFQImportData
        if instance.rfq_import:
            # Update the existing draft event to opened
            try:
                existing_event = RFQEvent.objects.get(rfq_import=instance.rfq_import)
                print(f"Found existing event for rfq_import id={instance.rfq_import.id}")
                existing_event.rfq_management = instance
                existing_event.status = 'opened'
                existing_event.save()
                print(f"Updated event status to 'opened'")
            except RFQEvent.DoesNotExist:
                # Create new event if none exists
                print("No existing event found, creating new one")
                RFQEvent.objects.create(
                    rfq_management=instance,
                    status='opened'
                )
        else:
            # Create new event for standalone RFQManagement
            print("No rfq_import, creating new event for RFQManagement")
            RFQEvent.objects.create(
                rfq_management=instance,
                status='opened'
            )
    else:
        # Update status based on RFQManagement status
        try:
            if instance.rfq_import:
                event = RFQEvent.objects.get(rfq_import=instance.rfq_import)
            else:
                event = RFQEvent.objects.get(rfq_management=instance)
            
            # Update status based on RFQManagement status
            if instance.status == 'awarded':
                event.status = 'awarded'
            elif instance.status == 'closed':
                event.status = 'closed'
            elif instance.status == 'cancelled':
                event.status = 'cancelled'
            elif instance.status == 'archived':
                event.status = 'archived'
            else:
                event.status = 'opened'
            
            event.save()
        except RFQEvent.DoesNotExist:
            # Create event if it doesn't exist
            RFQEvent.objects.create(
                rfq_management=instance,
                status=instance.status
            )

@receiver(m2m_changed, sender=RFQManagement.selected_suppliers.through)
def update_supplier_responses(sender, instance, action, **kwargs):
    """Update supplier responses count when selected_suppliers changes"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        try:
            if instance.rfq_import:
                event = RFQEvent.objects.get(rfq_import=instance.rfq_import)
            else:
                event = RFQEvent.objects.get(rfq_management=instance)
            
            event.update_supplier_responses()
        except RFQEvent.DoesNotExist:
            pass
