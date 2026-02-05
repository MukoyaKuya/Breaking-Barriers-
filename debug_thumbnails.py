import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.apps import apps
from easy_thumbnails.files import get_thumbnailer
from image_cropping.fields import ImageRatioField

def debug_thumbnails():
    GalleryImage = apps.get_model('church.GalleryImage')
    
    # Target specific broken images
    targets = [
        'Matthew 18:20 "For where two or three gather in my name, there am I with them"',
        '"We shall continue to spread the word"'
    ]
    
    print("--- Detailed Thumbnail Debugging ---")
    
    for target in targets:
        try:
            items = GalleryImage.objects.filter(caption__icontains=target[:50])
            if not items.exists():
                print(f"NOT FOUND: {target}")
                continue
            
            for item in items:
                print(f"\nItem: {item.caption}")
                print(f"Source Image: {item.image.name}")
                print(f"Crop Box: {item.image_cropping}")
                
                thumbnailer = get_thumbnailer(item.image)
                
                # EXACT options from template: 
                # {% thumbnail image.image "800x600" box=image.image_cropping crop detail as cropped %}
                options = {
                    'size': (800, 600),
                    'box': item.image_cropping,
                    'crop': True,
                    'detail': True
                }
                
                thumb = thumbnailer.get_thumbnail(options)
                print(f"Generated URL: {thumb.url}")
                print(f"Generated Name: {thumb.name}")
                
                if thumb.storage.exists(thumb.name):
                    print("Status: EXISTS on GCS")
                else:
                    print("Status: MISSING on GCS")
                    
        except Exception as e:
            print(f"Error debugging {target}: {e}")

if __name__ == "__main__":
    debug_thumbnails()
