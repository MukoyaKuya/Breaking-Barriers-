import os
import django
from django.core.management import call_command
from django.apps import apps
import json
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

django.setup()

def dump_all_safe():
    all_models = apps.get_models()
    combined_data = []
    
    # List of models that passed the debug_dump.py test
    safe_labels = [
        'auth.group', 'auth.user', 'sites.site',
        'easy_thumbnails.source', 'easy_thumbnails.thumbnail', 'easy_thumbnails.thumbnaildimensions',
        'church.verse', 'church.newsitem', 'church.newsline', 'church.partnerinquiry',
        'church.contactmessage', 'church.testimonial', 'church.galleryimage',
        'church.herosettings', 'church.aboutpage', 'church.infocard',
        'church.wordoftruth', 'church.mantalk', 'church.book',
        'church.childrensbread', 'church.ctacard', 'church.mensministry',
        'church.partner', 'church.newslettersubscriber', 'church.schoolministryenrollment',
        'church.sidebarpromo', 'church.faq', 'church.mn'
    ]
    
    for label in safe_labels:
        print(f"Dumping {label}...", end=" ", flush=True)
        try:
            buf = io.StringIO()
            call_command('dumpdata', label, stdout=buf)
            data = json.loads(buf.getvalue())
            combined_data.extend(data)
            print(f"OK ({len(data)} records)")
        except Exception as e:
            print(f"FAILED: {e}")
            
    output_path = "neon_backup_safe.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(combined_data)} records to {output_path}")

if __name__ == "__main__":
    dump_all_safe()
