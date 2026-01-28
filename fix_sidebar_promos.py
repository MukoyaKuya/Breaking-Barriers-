import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.apps import apps
from easy_thumbnails.files import get_thumbnailer

def regenerate_sidebar_promos():
    """Force regenerate sidebar promo thumbnails without box parameter."""
    SidebarPromo = apps.get_model('church.SidebarPromo')
    
    promos = SidebarPromo.objects.all()
    print(f"Found {promos.count()} sidebar promos")
    
    for promo in promos:
        if not promo.image or not promo.image.name:
            print(f"  Skipping {promo}: no image")
            continue
            
        print(f"\n  Processing: {promo.caption}")
        print(f"  Image: {promo.image.name}")
        
        thumbnailer = get_thumbnailer(promo.image)
        
        # Generate 300x400 thumbnail WITHOUT box parameter
        options = {
            'size': (300, 400),
            'crop': True,
            'detail': True
        }
        
        try:
            thumb = thumbnailer.get_thumbnail(options)
            print(f"  Generated URL: {thumb.url}")
            print(f"  Thumbnail name: {thumb.name}")
            
            if thumb.storage.exists(thumb.name):
                print(f"  ✓ Verified on GCS")
            else:
                print(f"  ✗ NOT on GCS!")
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    regenerate_sidebar_promos()
    print("\nDone!")
