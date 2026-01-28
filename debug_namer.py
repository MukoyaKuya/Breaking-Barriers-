import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.apps import apps
from easy_thumbnails.files import get_thumbnailer
from django.conf import settings

# Enable debug mode for thumbnails
print(f"THUMBNAIL_NAMER setting: {settings.THUMBNAIL_NAMER}")
print(f"THUMBNAIL_PROCESSORS: {settings.THUMBNAIL_PROCESSORS}")

def debug_single_thumbnail():
    """Debug thumbnail generation for a single image."""
    GalleryImage = apps.get_model('church.GalleryImage')
    
    # Get the problematic image
    img = GalleryImage.objects.filter(caption__icontains="We shall continue").first()
    
    if not img:
        print("Image not found")
        return
        
    print(f"\n{'='*60}")
    print(f"Image: {img.caption}")
    print(f"File: {img.image.name}")
    print(f"Crop box (from model): {img.image_cropping}")
    print(f"Crop box type: {type(img.image_cropping)}")
    
    thumbnailer = get_thumbnailer(img.image)
    
    options = {
        'size': (800, 600),
        'box': img.image_cropping,
        'crop': True,
        'detail': True
    }
    
    print(f"\nOptions passed to get_thumbnail:")
    for k, v in options.items():
        print(f"  {k}: {v} (type: {type(v)})")
    
    # Generate thumbnail
    try:
        thumb = thumbnailer.get_thumbnail(options)
        print(f"\nGenerated thumbnail:")
        print(f"  URL: {thumb.url}")
        print(f"  Name: {thumb.name}")
        
        # Check existence
        if thumb.storage.exists(thumb.name):
            print(f"  Status: EXISTS on GCS")
        else:
            print(f"  Status: MISSING on GCS")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_single_thumbnail()
