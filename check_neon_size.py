import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

django.setup()

def get_table_sizes():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                relname AS table_name, 
                pg_size_pretty(pg_total_relation_size(C.oid)) AS total_size,
                pg_total_relation_size(C.oid) as raw_size
            FROM pg_class C
            LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
            WHERE nspname NOT IN ('pg_catalog', 'information_schema')
              AND relkind = 'r'
            ORDER BY raw_size DESC;
        """)
        rows = cursor.fetchall()
        for row in rows:
            print(f"{row[0]}: {row[1]}")

if __name__ == "__main__":
    get_table_sizes()
