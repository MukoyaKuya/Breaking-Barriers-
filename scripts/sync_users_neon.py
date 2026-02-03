import os
import django
from django.conf import settings
import dj_database_url
import sys
import json

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
        SECRET_KEY='django-insecure-dummy-key-for-script',
    )
    django.setup()

from django.contrib.auth.models import User

def load_users():
    print("--- Syncing Users to Neon ---")
    
    with open('local_users_dump.json', 'r') as f:
        data = json.load(f)
    
    for item in data:
        if item['model'] == 'auth.user':
            fields = item['fields']
            username = fields['username']
            print(f"Syncing user: {username}")
            
            user, created = User.objects.update_or_create(
                username=username,
                defaults={
                    'password': fields['password'],
                    'is_superuser': fields['is_superuser'],
                    'first_name': fields['first_name'],
                    'last_name': fields['last_name'],
                    'email': fields['email'],
                    'is_staff': fields['is_staff'],
                    'is_active': fields['is_active'],
                    'date_joined': fields['date_joined'],
                }
            )
            
            if created:
                print(f"  -> CREATED")
            else:
                print(f"  -> UPDATED")

if __name__ == '__main__':
    load_users()
