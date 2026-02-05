import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.test import Client
from church.models import PartnerInquiry

print("Starting Donate Form Test...")

# Clean up previous tests
PartnerInquiry.objects.filter(email='test_script@example.com').delete()

c = Client()
data = {
    'partner-first_name': 'TestScript',
    'partner-last_name': 'Runner',
    'partner-email': 'test_script@example.com',
    'partner-phone': '+254712345678',
    'partner-company_name': 'TestCorp',
    'partner-message': 'Testing donation form submission.',
    'partner-submit': '' # Verification trigger
}

response = c.post('/donate/', data, HTTP_HOST='bb-international.org')

print(f"Response Status: {response.status_code}")
if response.status_code == 302:
    print(f"Redirect URL: {response.url}")

exists = PartnerInquiry.objects.filter(email='test_script@example.com').exists()
print(f"Record Saved: {exists}")

if exists:
    obj = PartnerInquiry.objects.get(email='test_script@example.com')
    print(f"ID: {obj.id}, Name: {obj.first_name}")
else:
    # If not saved, print form errors if context available (not easily accessing context from redirect response without follow=True/middleware setup)
    # But usually 200 + template means errors. 302 means success.
    if response.status_code == 200:
        print("Debugging 200 OK...")
        if response.context and 'partner_form' in response.context:
            print("Form Errors:", response.context['partner_form'].errors)
        else:
            print("No context available. Inspecting HTML content for error messages...")
            content = response.content.decode()
            if 'error' in content.lower():
                print("Found 'error' in HTML.")
                import re
                errors = re.findall(r'text-red-500.*?>(.*?)<', content)
                print("Found valid errors:", errors)
