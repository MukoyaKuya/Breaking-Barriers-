import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    user = User.objects.get(username='Roy')
    print(f"User FOUND: {user.username}")
    print(f"Is Superuser: {user.is_superuser}")
    print(f"Is Staff: {user.is_staff}")
    print(f"Is Active: {user.is_active}")
except User.DoesNotExist:
    print("User Roy NOT FOUND")
except Exception as e:
    print(f"Error: {e}")
