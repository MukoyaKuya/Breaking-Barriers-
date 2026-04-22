import os
import django
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path('.')
load_dotenv(BASE_DIR / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.conf import settings

print("--- ENV CHECK ---")
print(f"GS_BUCKET_NAME: '{os.environ.get('GS_BUCKET_NAME')}'")
print(f"USE_LOCAL_STORAGE: '{os.environ.get('USE_LOCAL_STORAGE')}'")
print(f"DEBUG: {settings.DEBUG}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")

# Check conditional logic
use_local = os.environ.get('USE_LOCAL_STORAGE', 'False')
print(f"USE_LOCAL_STORAGE string: '{use_local}'")
print(f"Condition (use_local != 'True'): {use_local != 'True'}")
print(f"Final USE_GCS: {os.environ.get('GS_BUCKET_NAME') and use_local != 'True'}")
