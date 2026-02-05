import os
import django
import sys
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load Env vars from env.yaml manually since we are running standalone
import yaml
try:
    with open(BASE_DIR / 'env.yaml', 'r') as f:
        env = yaml.safe_load(f)
        for k, v in env.items():
            os.environ[k] = str(v)
except FileNotFoundError:
    print("env.yaml not found!")
    sys.exit(1)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from church.models import NewsItem, Book, Partner
from easy_thumbnails.files import get_thumbnailer

def debug_thumbnails():
    print("--- Debugging Production Thumbnails ---")
    print(f"Database: {os.environ.get('DATABASE_URL').split('@')[1]}")
    print(f"Bucket: {os.environ.get('GS_BUCKET_NAME')}")
    
    # Check NewsItem
    item = NewsItem.objects.filter(image__isnull=False).exclude(image='').first()
    if item:
        print(f"\nTesting NewsItem: {item.title}")
        print(f"Image Field: {item.image.name}")
        try:
            # Check existence
            if not item.image.storage.exists(item.image.name):
                print("ERROR: Source file does not exist in Storage!")
            else:
                print("SUCCESS: Source file exists.")
                
                # Try generating
                print("Attempting thumbnail generation...")
                options = {'size': (800, 600), 'crop': True}
                thumb = get_thumbnailer(item.image).get_thumbnail(options)
                print(f"Thumbnail URL: {thumb.url}")
        except Exception as e:
            print(f"EXCEPTION: {e}")
    else:
        print("\nNo NewsItem with image found.")

if __name__ == '__main__':
    debug_thumbnails()
