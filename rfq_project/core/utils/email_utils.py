from django.core.mail import send_mail
from django.conf import settings
from core.models import SupplierResponseToken

def send_rfq_email_to_supplier(rfq_import, supplier):
    # Create or get a unique token for this supplier and RFQManagement
    token_obj, _ = SupplierResponseToken.objects.get_or_create(
        supplier=supplier,
        rfq_import=rfq_import
    )

    # Generate the response link
    response_url = f"http://127.0.0.1:8000/api/supplier/respond-form/{token_obj.token}/"

    subject = f"New RFQ Assigned: {rfq_import.title}"
    message = f"""
Dear {supplier.supplier_name},

You have been selected for a new RFQ.

Details:
- PR Number: {rfq_import.client_pr_number}
- Title: {rfq_import.title}
- Description: {rfq_import.description}
- Commodity Code: {rfq_import.commodity_code}
- Need by Date: {rfq_import.need_by_date}
- Manufacturer: {rfq_import.manufacturer_name}

Please respond at the earliest.

Respond here: {response_url}

Regards,
RFQ Management Team
    """

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [supplier.email_address])
