import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.apps import apps
from easy_thumbnails.files import get_thumbnailer
from django.conf import settings

def force_regenerate_sidebar_promos():
    """Force regenerate sidebar promo thumbnails by explicitly generating new ones."""
    SidebarPromo = apps.get_model('church.SidebarPromo')
    
    promos = SidebarPromo.objects.all()
    print(f"Found {promos.count()} sidebar promos")
    print(f"Storage backend: {settings.DEFAULT_FILE_STORAGE}")
    
    for promo in promos:
        if not promo.image or not promo.image.name:
            print(f"Skipping {promo}: no image")
            continue
            
        print(f"\n{'='*50}")
        print(f"Processing: {promo.caption}")
        print(f"Image path: {promo.image.name}")
        
        try:
            thumbnailer = get_thumbnailer(promo.image)
            
            # Options WITHOUT box parameter
            options = {
                'size': (300, 400),
                'crop': True,
                'detail': True
            }
            
            # Force generate (even if exists)
            thumb = thumbnailer.get_thumbnail(options, generate=True)
            
            print(f"Thumbnail generated:")
            print(f"  URL: {thumb.url}")
            print(f"  Name: {thumb.name}")
            print(f"  Storage: {thumb.storage}")
            
            # Verify it exists
            exists = thumb.storage.exists(thumb.name)
            print(f"  Exists on storage: {exists}")
            
            if not exists:
                # Try to save explicitly
                print("  Attempting explicit save...")
                from django.core.files.base import ContentFile
                content = thumb.read()
                thumb.storage.save(thumb.name, ContentFile(content))
                print(f"  Saved {len(content)} bytes")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    force_regenerate_sidebar_promos()
    print("\nDone!")
