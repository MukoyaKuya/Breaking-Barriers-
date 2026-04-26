import os
import django
import pymysql

pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.install_as_MySQLdb()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "church_app.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()[0]
    print(f"Database Version: {version}")
    
print(f"Django Version: {django.get_version()}")
print(f"Can return columns from insert: {connection.features.can_return_columns_from_insert}")
