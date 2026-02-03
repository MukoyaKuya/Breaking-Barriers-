import os
import django
from django.conf import settings
import dj_database_url
import sys

sys.path.append(os.getcwd())

# Configure for Neon DB
NEON_URL = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require'

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': dj_database_url.parse(NEON_URL)
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'easy_thumbnails',
            'image_cropping',
            'ckeditor',
            'ckeditor_uploader',
            'church', 
        ],
        STATIC_URL='/static/',
        CKEDITOR_UPLOAD_PATH='uploads/',
    )
    django.setup()

from django.contrib.auth.models import User

def check_structure():
    try:
        u = User.objects.get(username='Roy')
        print(f"User: {u.username}")
        print(f"Hash: {u.password}")
        print(f"Is Active: {u.is_active}")
        print(f"Is Staff: {u.is_staff}")
        print(f"Is Superuser: {u.is_superuser}")
    except User.DoesNotExist:
        print("User 'Roy' not found in Neon.")

if __name__ == '__main__':
    check_structure()
