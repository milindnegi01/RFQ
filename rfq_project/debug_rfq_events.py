#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rfq_project.settings')
django.setup()

from core.models import RFQImportData, RFQEvent, RFQManagement, CustomUser

def debug_rfq_events():
    print("=== RFQ Events Debug ===\n")
    
    # Check existing RFQImportData
    print("1. RFQImportData records:")
    rfq_imports = RFQImportData.objects.all()
    for rfq in rfq_imports:
        print(f"   ID: {rfq.id}, Title: {rfq.title}, Created by: {rfq.created_by.username}")
    
    # Check existing RFQEvent records
    print("\n2. RFQEvent records:")
    events = RFQEvent.objects.all()
    for event in events:
        print(f"   ID: {event.id}, Status: {event.status}, RFQ Import: {event.rfq_import_id}, RFQ Management: {event.rfq_management_id}")
    
    # Check existing RFQManagement records
    print("\n3. RFQManagement records:")
    rfq_managements = RFQManagement.objects.all()
    for rfq_mgmt in rfq_managements:
        print(f"   ID: {rfq_mgmt.id}, Title: {rfq_mgmt.title}, Status: {rfq_mgmt.status}, RFQ Import: {rfq_mgmt.rfq_import_id}")
    
    # Find RFQImportData without events
    print("\n4. RFQImportData without events:")
    rfqs_without_events = []
    for rfq in rfq_imports:
        if not RFQEvent.objects.filter(rfq_import=rfq).exists():
            rfqs_without_events.append(rfq)
            print(f"   RFQ ID {rfq.id}: {rfq.title} - NO EVENT")
    
    # Find RFQManagement without events
    print("\n5. RFQManagement without events:")
    mgmt_without_events = []
    for rfq_mgmt in rfq_managements:
        if not RFQEvent.objects.filter(rfq_management=rfq_mgmt).exists():
            mgmt_without_events.append(rfq_mgmt)
            print(f"   Management ID {rfq_mgmt.id}: {rfq_mgmt.title} - NO EVENT")
    
    return rfqs_without_events, mgmt_without_events

def fix_rfq_events():
    print("\n=== Fixing RFQ Events ===\n")
    
    # Create events for RFQImportData without events
    print("1. Creating events for RFQImportData records:")
    for rfq in RFQImportData.objects.all():
        event, created = RFQEvent.objects.get_or_create(
            rfq_import=rfq,
            defaults={'status': 'draft'}
        )
        if created:
            print(f"   ✓ Created event for RFQ {rfq.id}: {rfq.title}")
        else:
            print(f"   - Event already exists for RFQ {rfq.id}: {rfq.title}")
    
    # Create/update events for RFQManagement records
    print("\n2. Creating/updating events for RFQManagement records:")
    for rfq_mgmt in RFQManagement.objects.all():
        if rfq_mgmt.rfq_import:
            # Update existing event or create new one
            event, created = RFQEvent.objects.get_or_create(
                rfq_import=rfq_mgmt.rfq_import,
                defaults={
                    'rfq_management': rfq_mgmt,
                    'status': rfq_mgmt.status
                }
            )
            if not created:
                # Update existing event
                event.rfq_management = rfq_mgmt
                event.status = rfq_mgmt.status
                event.save()
                print(f"   ✓ Updated event for RFQ Management {rfq_mgmt.id}")
            else:
                print(f"   ✓ Created event for RFQ Management {rfq_mgmt.id}")
        else:
            # Create standalone event
            event, created = RFQEvent.objects.get_or_create(
                rfq_management=rfq_mgmt,
                defaults={'status': rfq_mgmt.status}
            )
            if created:
                print(f"   ✓ Created standalone event for RFQ Management {rfq_mgmt.id}")
            else:
                print(f"   - Event already exists for RFQ Management {rfq_mgmt.id}")

def test_signal():
    print("\n=== Testing Signal ===\n")
    
    # Get an end user
    end_user = CustomUser.objects.filter(role='end_user').first()
    if not end_user:
        print("No end user found. Creating one...")
        end_user = CustomUser.objects.create(
            username='test_end_user',
            email='test@example.com',
            role='end_user',
            organization='TestOrg'
        )
    
    print(f"Testing signal with end user: {end_user.username}")
    
    # Create a test RFQImportData
    test_rfq = RFQImportData.objects.create(
        created_by=end_user,
        title="Test RFQ for Signal",
        client_pr_number="TEST001",
        client_requestor_name="Test User",
        client_requestor_id="USER001",
        client_code="CODE001",
        shipping_address="Test Address",
        Currency="USD",
        serial_no="1",
        description="Test Description",
        need_by_date="2024-12-31",
        supplier_part_number="PART001",
        commodity_code="COMM001",
        uom="PCS",
        unit_price=100.00,
        supplier_name="Test Supplier",
        manufacturer_name="Test Manufacturer",
        manufacturer_part_number="MAN001"
    )
    print(f"Created RFQImportData with ID: {test_rfq.id}")
    
    # Check if event was created
    event = RFQEvent.objects.filter(rfq_import=test_rfq).first()
    if event:
        print(f"✓ Signal working: Event created with ID {event.id}, Status: {event.status}")
    else:
        print("✗ Signal not working: No event created")
    
    return test_rfq

if __name__ == "__main__":
    # Debug current state
    rfqs_without_events, mgmt_without_events = debug_rfq_events()
    
    # Fix missing events
    fix_rfq_events()
    
    # Test signal
    test_rfq = test_signal()
    
    # Final check
    print("\n=== Final Check ===")
    debug_rfq_events()
    
    print(f"\nDebug complete! Test RFQ created with ID: {test_rfq.id}")
    print("You can now test the API endpoint: /api/rfq-events/") 