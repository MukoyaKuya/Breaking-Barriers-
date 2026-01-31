
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.test import RequestFactory
from church.views import donate_view
from church.models import ContactMessage, PartnerInquiry

def test_forms():
    factory = RequestFactory()

    # Test Contact Form Submission
    print("Testing Contact Form Submission...")
    contact_data = {
        'contact-submit': '',
        'contact-name': 'Test User',
        'contact-email': 'test@example.com',
        'contact-phone': '0712345678',
        'contact-subject': 'Test Subject',
        'contact-message': 'This is a test contact message.'
    }
    request = factory.post('/donate/', contact_data)
    
    # We need to add session and messages middleware support manually for the factory
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.messages.middleware import MessageMiddleware
    
    SessionMiddleware(lambda x: None).process_request(request)
    MessageMiddleware(lambda x: None).process_request(request)
    
    response = donate_view(request)
    
    if response.status_code == 302:
        print("Contact form redirected successfully (likely success).")
        latest_contact = ContactMessage.objects.last()
        if latest_contact and latest_contact.name == 'Test User':
            print(f"Contact saved: {latest_contact.name} - {latest_contact.message}")
        else:
            print("Error: Contact message not saved.")
    else:
        print(f"Contact form submission failed with status {response.status_code}")

    # Test Partner Form Submission
    print("\nTesting Partner Form Submission...")
    partner_data = {
        'partner-submit': '',
        'partner-first_name': 'Partner',
        'partner-last_name': 'User',
        'partner-company_name': 'Test Corp',
        'partner-email': 'partner@example.com',
        'partner-phone': '0787654321',
        'partner-message': 'We want to partner with you.'
    }
    request = factory.post('/donate/', partner_data)
    SessionMiddleware(lambda x: None).process_request(request)
    MessageMiddleware(lambda x: None).process_request(request)

    response = donate_view(request)

    if response.status_code == 302:
        print("Partner form redirected successfully (likely success).")
        latest_partner = PartnerInquiry.objects.last()
        if latest_partner and latest_partner.first_name == 'Partner':
            print(f"Partner inquiry saved: {latest_partner.first_name} {latest_partner.last_name} - {latest_partner.company_name}")
        else:
            print("Error: Partner inquiry not saved.")
    else:
        print(f"Partner form submission failed with status {response.status_code}")

if __name__ == "__main__":
    test_forms()
