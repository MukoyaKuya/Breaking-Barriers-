import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.apps import apps
from easy_thumbnails.files import get_thumbnailer
from django.core.files.storage import default_storage

def fix_gallery_thumbnails():
    """Delete and regenerate thumbnails for specific problematic gallery images."""
    GalleryImage = apps.get_model('church.GalleryImage')
    
    # Get all gallery images
    images = GalleryImage.objects.all()
    
    print(f"Processing {images.count()} gallery images...")
    
    for img in images:
        if not img.image or not img.image.name:
            continue
            
        print(f"\n{'='*60}")
        print(f"Image: {img.caption}")
        print(f"File: {img.image.name}")
        print(f"Crop box: {img.image_cropping}")
        
        # Delete existing thumbnails for this image
        thumbnailer = get_thumbnailer(img.image)
        
        # Get list of all thumbnails for this image
        try:
            # Try to delete all existing thumbnails
            thumbnailer.delete_thumbnails()
            print("Deleted existing thumbnails")
        except Exception as e:
            print(f"Could not delete thumbnails: {e}")
        
        # Now regenerate with exact template options
        options = {
            'size': (800, 600),
            'box': img.image_cropping,
            'crop': True,
            'detail': True
        }
        
        try:
            # Force generation
            thumb = thumbnailer.get_thumbnail(options)
            print(f"Generated: {thumb.url}")
            print(f"Filename: {thumb.name}")
            
            # Verify it exists
            if thumb.storage.exists(thumb.name):
                print("✓ Verified on GCS")
                
                # Also try to read it to ensure it's accessible
                try:
                    with thumb.storage.open(thumb.name, 'rb') as f:
                        size = len(f.read())
                        print(f"✓ File is readable ({size} bytes)")
                except Exception as e:
                    print(f"✗ File exists but not readable: {e}")
            else:
                print("✗ NOT found on GCS")
        except Exception as e:
            print(f"✗ Error generating thumbnail: {e}")
    
    print(f"\n{'='*60}")
    print("Finished processing all gallery images")

if __name__ == "__main__":
    fix_gallery_thumbnails()
