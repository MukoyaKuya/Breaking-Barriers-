import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

django.setup()

def get_stats():
    results = []
    with connection.cursor() as cursor:
        # Get Table Sizes
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
        size_rows = cursor.fetchall()
        
        results.append("--- TABLE SIZES ---")
        for row in size_rows:
            results.append(f"{row[0]}: {row[1]}")
            
        results.append("\n--- ROW COUNTS (Top 10) ---")
        for row in size_rows[:10]:
            table_name = row[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            results.append(f"{table_name}: {count} rows")
            
    output_path = r"c:\Users\Little Human\Desktop\BBInternational\Breaking-Barriers\neon_stats_output.txt"
    with open(output_path, "w") as f:
        f.write("\n".join(results))
    print(f"Results written to {output_path}")

if __name__ == "__main__":
    get_stats()
