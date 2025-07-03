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

# ... existing code ...
from django.core.mail import send_mail
from django.conf import settings

def send_award_email_to_supplier(rfq_import, supplier):
    subject = f"Congratulations! You have been awarded RFQ: {rfq_import.title}"
    message = (
        f"Dear {supplier.supplier_name},\n\n"
        f"Congratulations! You have been selected as the awarded supplier for the RFQ '{rfq_import.title}'.\n"
        f"Details:\n"
        f"PR Number: {rfq_import.client_pr_number}\n"
        f"Description: {rfq_import.description}\n"
        f"Need By Date: {rfq_import.need_by_date}\n\n"
        f"Please log in to your portal for more details.\n\n"
        f"Best regards,\n"
        f"{rfq_import.created_by.organization}"
    )
    recipient_list = [supplier.email_address]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list) 

from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def send_award_email_with_order(rfq_import, supplier, rfq_management):
    subject = f"Purchase Order for Awarded RFQ: {rfq_import.title}"
    # Render order as HTML
    order_html = render_to_string('order_template.html', {
        'rfq': rfq_import,
        'supplier': supplier,
        'rfq_management': rfq_management,
    })
    email = EmailMessage(
        subject,
        order_html,
        settings.DEFAULT_FROM_EMAIL,
        [supplier.email_address],
    )
    email.content_subtype = "html"  # Send as HTML email
    email.send()