import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.apps import apps
from easy_thumbnails.files import get_thumbnailer

def regenerate_all_thumbnails():
    """Regenerate thumbnails for all models that use image cropping."""
    
    models_config = [
        ('church.SidebarPromo', 'image', (300, 400)),
        ('church.GalleryImage', 'image', (800, 600)),
        ('church.NewsItem', 'image', (800, 600)),
        ('church.HeroSettings', 'image', (1920, 1080)),
        ('church.Partner', 'logo', (300, 200)),
        ('church.InfoCard', 'image', (1600, 900)),
        ('church.Testimonial', 'photo', (400, 400)),
        ('church.CalendarEvent', 'image', (800, 600)),
    ]
    
    for model_name, image_field, size in models_config:
        try:
            model = apps.get_model(model_name)
            instances = model.objects.all()
            print(f"\nProcessing {model_name} ({instances.count()} instances)...")
            
            for instance in instances:
                image = getattr(instance, image_field)
                if not image or not image.name:
                    continue
                    
                print(f"  - {instance}: {image.name}")
                
                thumbnailer = get_thumbnailer(image)
                
                # Generate thumbnail WITHOUT box parameter
                options = {
                    'size': size,
                    'crop': True,
                    'detail': True
                }
                
                try:
                    thumb = thumbnailer.get_thumbnail(options)
                    print(f"    Generated: {thumb.url}")
                    
                    if thumb.storage.exists(thumb.name):
                        print(f"    Verified on GCS")
                    else:
                        print(f"    WARNING: Not on GCS")
                except Exception as e:
                    print(f"    Error: {e}")
                        
        except Exception as e:
            print(f"Error with {model_name}: {e}")

if __name__ == "__main__":
    regenerate_all_thumbnails()
    print("\nFinished!")
