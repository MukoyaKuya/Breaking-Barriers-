
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from easy_thumbnails.files import get_thumbnailer
from church.models import CalendarEvent
from django.conf import settings
# Test with default namer to isolate issue
settings.THUMBNAIL_NAMER = 'easy_thumbnails.namers.default'


def run_test():
    filename = 'calendar_events/554046056_1264358689061610_2566163542975989460_n.jpg'
    
    # Check if file exists in media root
    from django.conf import settings
    full_path = os.path.join(settings.MEDIA_ROOT, filename)
    print(f"Checking existence of: {full_path}")
    if os.path.exists(full_path):
        print("File EXISTS.")
    else:
        print("File NOT FOUND. Creating a dummy file for testing...")
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        # Create a simple red block image
        from PIL import Image
        img = Image.new('RGB', (1000, 1000), color = 'red')
        img.save(full_path)
        print("Dummy file created.")

    # Simulate the thumbnail generation
    # Create a mock object with 'name' attribute
    class MockImage:
        def __init__(self, name):
            self.name = name
            self.storage = settings.STORAGES['default']['BACKEND']
            # We need to instantiate the storage class
            from django.core.files.storage import FileSystemStorage
            self.storage = FileSystemStorage()
            self.url = '/media/' + name

    mock_image = MockImage(filename)
    
    # Options used in views.py
    # 'box': event.image_cropping usually looks like "0,0,800,600"
    options = {
        'size': (800, 600),
        'box': '0,0,500,500', 
        'crop': True,
        'detail': True,
    }

    # Verify storage open
    try:
        f = mock_image.storage.open(filename)
        print(f"Storage open success. Size: {f.size}")
        f.close()
    except Exception as e:
        print(f"Storage open FAILED: {e}")

    # Verify PIL open
    from PIL import Image
    try:
        with mock_image.storage.open(filename) as f:
            img = Image.open(f)
            img.verify()
            print(f"PIL verify success. Format: {img.format}")
    except Exception as e:
        print(f"PIL open/verify FAILED: {e}")

    try:
        print("Attempting to generate thumbnail...")
        # get_thumbnailer needs relative_name if the object isn't a FieldFile
        thumbnailer = get_thumbnailer(mock_image, relative_name=filename)
        thumb = thumbnailer.get_thumbnail(options)
        print(f"Thumbnail URL: {thumb.url}")
        print(f"Thumbnail Name: {thumb.name}")
        
        # Verify if the thumbnail file actually exists
        # In this custom setup, name might contain / but OS is windows
        # thumb.name is relative to MEDIA_ROOT
        
        # Normalize thumb.name for robust check
        norm_thumb_name = thumb.name.replace('/', os.sep)
        thumb_path = os.path.join(settings.MEDIA_ROOT, norm_thumb_name)
        
        print(f"Checking existence of: {thumb_path}")
        if os.path.exists(thumb_path):
             print(f"SUCCESS: Thumbnail created at {thumb_path}")
        else:
             print(f"FAILURE: Thumbnail URL generated but file missing at {thumb_path}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
