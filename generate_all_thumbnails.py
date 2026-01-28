import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.apps import apps
from easy_thumbnails.files import get_thumbnailer
from image_cropping.fields import ImageRatioField

def generate_thumbnails():
    print("Starting exact-match thumbnail generation...")
    
    models_to_process = [
        'church.NewsItem',
        'church.GalleryImage',
        'church.InfoCard',
        'church.HeroSettings',
        'church.Partner',
        'church.SidebarPromo',
        'church.Testimonial',
        'church.CalendarEvent'
    ]
    
    for model_name in models_to_process:
        try:
            model = apps.get_model(model_name)
            instances = model.objects.all()
            print(f"Processing {model_name} ({instances.count()} instances)...")
            
            ratio_fields = [f for f in model._meta.fields if isinstance(f, ImageRatioField)]
            
            for instance in instances:
                for ratio_field in ratio_fields:
                    image_field_name = ratio_field.image_field
                    image_file = getattr(instance, image_field_name)
                    
                    if not image_file or not image_file.name:
                        continue
                        
                    thumbnailer = get_thumbnailer(image_file)
                    
                    size_str = ratio_field.size if hasattr(ratio_field, 'size') else '800x600'
                    width, height = map(int, size_str.split('x'))
                    
                    crop_box = getattr(instance, ratio_field.name)
                    
                    # MATCH TEMPLATE OPTIONS EXACTLY: {% thumbnail image.image "800x600" box=image.image_cropping crop detail as cropped %}
                    options = {
                        'size': (width, height),
                        'box': crop_box,
                        'crop': True,
                        'detail': True
                    }
                    
                    print(f"  Item: {instance} | Image: {image_file.name}")
                    try:
                        thumb = thumbnailer.get_thumbnail(options)
                        print(f"    URL: {thumb.url}")
                        
                        # Verify verification
                        if thumb.storage.exists(thumb.name):
                            print(f"    Verified on GCS.")
                        else:
                            print(f"    ERROR: Still not on GCS.")
                    except Exception as e:
                        print(f"    Error: {e}")
                        
        except Exception as e:
            print(f"Error processing model {model_name}: {e}")

if __name__ == "__main__":
    generate_thumbnails()
    print("Finished.")
