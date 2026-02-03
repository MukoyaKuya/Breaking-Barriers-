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
            'church', 
        ],
        STATIC_URL='/static/',
    )
    django.setup()

from django.contrib.auth.models import User

def check_users():
    print("--- [NEON] Users ---")
    users = User.objects.all()
    for u in users:
        print(f"User: {u.username} (Superuser: {u.is_superuser}, Active: {u.is_active})")
    
    if not users:
        print("NO USERS FOUND!")

if __name__ == '__main__':
    check_users()
