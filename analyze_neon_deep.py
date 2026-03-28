import os
import django
from django.db import connection
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

django.setup()

def deep_analysis():
    results = []
    with connection.cursor() as cursor:
        results.append("--- DEEP FORENSIC LOG ANALYSIS ---")
        
        # 1. Peak Frequency (Hits per minute during Mar 23 peak)
        results.append("\n--- PEAK FREQUENCY (Mar 23) ---")
        cursor.execute("""
            SELECT TO_CHAR(viewed_at, 'YYYY-MM-DD HH24:MI') as minute, COUNT(*) 
            FROM church_pageview 
            WHERE viewed_at >= '2026-03-23 10:00:00' AND viewed_at <= '2026-03-23 11:00:00'
            GROUP BY minute 
            ORDER BY minute ASC
        """)
        for row in cursor.fetchall():
            results.append(f"{row[0]}: {row[1]} hits")

        # 2. Path Variety for Attacking IPs
        results.append("\n--- TARGET PATHS FOR IP 57.141.6.3 ---")
        cursor.execute("""
            SELECT path, COUNT(*) as count 
            FROM church_pageview 
            WHERE ip_address = '57.141.6.3' 
            GROUP BY path 
            ORDER BY count DESC 
            LIMIT 20
        """)
        for row in cursor.fetchall():
            results.append(f"{row[0]}: {row[1]} hits")

        # 3. Last Activity
        results.append("\n--- MOST RECENT ACTIVITY (Last 50 entries) ---")
        cursor.execute("""
            SELECT viewed_at, ip_address, path 
            FROM church_pageview 
            ORDER BY viewed_at DESC 
            LIMIT 50
        """)
        for row in cursor.fetchall():
            results.append(f"{row[0]}: {row[1]} -> {row[2]}")

    output_path = r"c:\Users\Little Human\Desktop\BBInternational\Breaking-Barriers\neon_deep_analysis.txt"
    with open(output_path, "w") as f:
        f.write("\n".join(results))
    print(f"Deep analysis saved to {output_path}")

if __name__ == "__main__":
    deep_analysis()
