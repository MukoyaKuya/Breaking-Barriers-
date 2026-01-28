import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.core.files.storage import default_storage

def list_gcs_files():
    print(f"Storage: {default_storage.__class__.__name__}")
    
    dirs = ['info_cards', 'sidebar_promos', 'news', 'gallery']
    for d in dirs:
        print(f"\nListing directory: {d}")
        try:
            dirs_list, files = default_storage.listdir(d)
            print(f"  Files found ({len(files)}): {files[:10]}{'...' if len(files) > 10 else ''}")
        except Exception as e:
            print(f"  Error listing {d}: {e}")

if __name__ == "__main__":
    list_gcs_files()
