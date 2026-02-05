
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from church.models import CalendarEvent, NewsItem
from easy_thumbnails.files import get_thumbnailer

def list_and_test():
    events = NewsItem.objects.exclude(image='')
    print(f"Found {events.count()} NewsItems with images.")
    
    for event in events:
        print(f"Event: {event.title}, Image: {event.image.name}")
        if not event.image:
             continue
        
        # Verify file existence via storage
        try:
            if not event.image.storage.exists(event.image.name):
                print("  -> File MISSING according to storage.")
                continue
            else:
                print("  -> File EXISTS.")
        except Exception as e:
            print(f"  -> Storage Check Error: {e}")
            continue

        # Try to thumbnail
        try:
             # Use the same options as views.py
             options = {
                'size': (800, 600),
                'box': '0,0,500,500', 
                'crop': True,
                'detail': True,
            }
             print(f"  -> Generating thumbnail with options: {options}")
             thumb = get_thumbnailer(event.image).get_thumbnail(options)
             print(f"  -> SUCCESS. URL: {thumb.url}")
             print(f"  -> Path: {thumb.path}")
             break # One is enough
        except Exception as e:
            print(f"  -> FAILED: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    list_and_test()
