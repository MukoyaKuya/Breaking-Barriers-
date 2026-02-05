import os
import django

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')

# Configure Django
from django.conf import settings

# Force database connection to local proxy without SSL
if os.environ.get('DB_OVERRIDE') == 'True':
    import dj_database_url
    settings.DATABASES = {
        'default': dj_database_url.config(
            default='postgres://postgres:BBI_Secure_Pass_2026!@127.0.0.1:5432/bbi_prod',
            ssl_require=False
        )
    }

django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
username = 'Roy'
password = 'Roy@2025'
email = 'roy@example.com'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"SUCCESS: Superuser '{username}' created.")
else:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"SUCCESS: Superuser '{username}' updated.")
