import os
import django
from django.conf import settings
import sys

sys.path.append(os.getcwd())

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(os.getcwd(), 'db.sqlite3'),
            }
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

def reset_password():
    try:
        u = User.objects.get(username='Roy')
        u.set_password('Roy@2025')
        u.save()
        print(f"BINGO: Password for '{u.username}' reset to 'Roy@2025'")
    except User.DoesNotExist:
        print("ERROR: User 'Roy' not found locally.")

if __name__ == '__main__':
    reset_password()
