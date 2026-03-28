import os
import django
from django.db import connection
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

django.setup()

def get_analysis():
    results = []
    with connection.cursor() as cursor:
        results.append("--- NEON COST ANALYSIS REPORT ---")
        
        # 1. PageView Total
        cursor.execute("SELECT COUNT(*) FROM church_pageview")
        total_pvs = cursor.fetchone()[0]
        results.append(f"Total PageViews: {total_pvs}")

        # 2. Hits per day (Last 14 days)
        results.append("\n--- HITS PER DAY (Last 14 Days) ---")
        cursor.execute("""
            SELECT DATE(viewed_at) as date, COUNT(*) 
            FROM church_pageview 
            WHERE viewed_at > NOW() - INTERVAL '14 days'
            GROUP BY date 
            ORDER BY date DESC
        """)
        for row in cursor.fetchall():
            results.append(f"{row[0]}: {row[1]}")

        # 3. Top 30 IP Addresses
        results.append("\n--- TOP 30 IP ADDRESSES (Potential Bots) ---")
        cursor.execute("""
            SELECT ip_address, COUNT(*) as count 
            FROM church_pageview 
            GROUP BY ip_address 
            ORDER BY count DESC 
            LIMIT 30
        """)
        for row in cursor.fetchall():
            results.append(f"{row[0]}: {row[1]}")

        # 4. Top 30 Paths
        results.append("\n--- TOP 30 PATHS ---")
        cursor.execute("""
            SELECT path, COUNT(*) as count 
            FROM church_pageview 
            GROUP BY path 
            ORDER BY count DESC 
            LIMIT 30
        """)
        for row in cursor.fetchall():
            results.append(f"{row[0]}: {row[1]}")

        # 5. Session Analysis
        results.append("\n--- SESSION TABLE ANALYSIS ---")
        cursor.execute("SELECT COUNT(*) FROM django_session")
        total_sessions = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM django_session WHERE expire_date < NOW()")
        expired_sessions = cursor.fetchone()[0]
        results.append(f"Total Sessions in DB: {total_sessions}")
        results.append(f"Expired Sessions (Uncleaned): {expired_sessions}")
        
    output_path = r"c:\Users\Little Human\Desktop\BBInternational\Breaking-Barriers\neon_log_analysis.txt"
    with open(output_path, "w") as f:
        f.write("\n".join(results))
    print(f"Analysis saved to {output_path}")

if __name__ == "__main__":
    get_analysis()
