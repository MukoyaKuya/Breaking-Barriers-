import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "church_app.settings")
django.setup()

print(f"Database Vendor: {connection.vendor}")
print(f"Database Version: {connection.get_database_version()}")
print(f"Can return columns from insert: {connection.features.can_return_columns_from_insert}")

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        print(f"Actual Version from DB: {cursor.fetchone()[0]}")
except Exception as e:
    print(f"Error checking version: {e}")
