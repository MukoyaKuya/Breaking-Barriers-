import os
import django
import json
import io
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

django.setup()

def merge_calendar():
    print("Dumping church.calendarevent...")
    try:
        buf = io.StringIO()
        call_command('dumpdata', 'church.calendarevent', stdout=buf)
        events = json.loads(buf.getvalue())
        print(f"OK ({len(events)} events)")
        
        safe_path = "neon_backup_safe.json"
        full_path = "neon_backup_full_essential.json"
        
        with open(safe_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        data.extend(events)
        
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Success! Full essential backup saved to {full_path} ({len(data)} total records)")
    except Exception as e:
        print(f"FAILED to merge calendar: {e}")

if __name__ == "__main__":
    merge_calendar()
