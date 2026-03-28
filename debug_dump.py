import os
import django
from django.core.management import call_command
from django.apps import apps
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

django.setup()

def debug_dump():
    all_models = apps.get_models()
    results = []
    for model in all_models:
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        label = f"{app_label}.{model_name}"
        
        if label in ['auth.permission', 'contenttypes', 'admin.logentry', 'church.pageview', 'sessions.session']:
            continue
            
        print(f"Testing dump of {label}...", end=" ", flush=True)
        try:
            buf = io.StringIO()
            call_command('dumpdata', label, stdout=buf)
            results.append(f"{label}: OK")
            print("OK")
        except Exception as e:
            results.append(f"{label}: FAILED - {e}")
            print(f"FAILED: {e}")
            
    with open("debug_dump_results.txt", "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    debug_dump()
