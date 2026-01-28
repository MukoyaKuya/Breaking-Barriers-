import os
import django
from django.conf import settings
from django.template.loader import render_to_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from church.models import GalleryImage

def verify_template_rendering():
    print("Testing Gallery Template Rendering...")
    images = GalleryImage.objects.all()[:1]
    if not images:
        print("No gallery images found to test.")
        return
        
    context = {'gallery_images': images}
    try:
        html = render_to_string('church/partials/gallery_items.html', context)
        print("\nRendered HTML Fragment (first few lines):")
        print(html[:500])
        
        if 'media/gallery/' in html and 'box-' in html:
            print("\n[SUCCESS] Thumbnail tag is working and generating normalized paths with cropping boxes.")
        elif 'media/gallery/' in html:
            print("\n[PARTIAL SUCCESS] Image path found, but 'box-' parameter missing (check if cropping is enabled for the item).")
        else:
            print("\n[FAILURE] No media path found in rendered HTML.")
            
    except Exception as e:
        print(f"Error rendering template: {e}")

if __name__ == "__main__":
    verify_template_rendering()
