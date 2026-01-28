import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.apps import apps
from django.core.files.storage import default_storage

def fix_sidebar_promo_images():
    """Fix sidebar promo image paths to match what exists on GCS."""
    SidebarPromo = apps.get_model('church.SidebarPromo')
    
    print("Checking sidebar promo images...")
    print(f"Storage backend: {default_storage.__class__.__name__}")
    
    promos = SidebarPromo.objects.all()
    print(f"Found {promos.count()} promos")
    
    # List what files actually exist in sidebar_promos/
    print("\nListing files on GCS:")
    try:
        from storages.backends.gcloud import GoogleCloudStorage
        storage = GoogleCloudStorage()
        # List files in the sidebar_promos directory
        _, files = storage.listdir('sidebar_promos')
        print(f"Files found: {files}")
    except Exception as e:
        print(f"Error listing: {e}")
        files = []
    
    for promo in promos:
        print(f"\n{'='*50}")
        print(f"Promo: {promo.caption}")
        if promo.image:
            print(f"DB references: {promo.image.name}")
            
            # Check if this file exists
            exists = default_storage.exists(promo.image.name)
            print(f"File exists: {exists}")
            
            if not exists:
                print("FIXING: File doesn't exist, looking for alternatives...")
                # Try to find a similar file
                base_name = promo.image.name.split('/')[-1].split('_')[0]  # Get first part before underscore
                print(f"Looking for files starting with: {base_name}")
                
                for f in files:
                    if f.startswith(base_name) and not '_q85' in f:
                        print(f"  Found match: {f}")
                        # Update the image path
                        new_path = f"sidebar_promos/{f}"
                        print(f"  Updating to: {new_path}")
                        promo.image.name = new_path
                        promo.save()
                        print(f"  SAVED!")
                        break
        else:
            print(f"No image set")

if __name__ == "__main__":
    fix_sidebar_promo_images()
    print("\nDone!")
