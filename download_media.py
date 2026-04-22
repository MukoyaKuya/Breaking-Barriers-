import os
import django
from dotenv import load_dotenv
from pathlib import Path
from google.cloud import storage

# Setup Django environment
BASE_DIR = Path('.')
load_dotenv(BASE_DIR / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.conf import settings

def download_media():
    bucket_name = os.environ.get('GS_BUCKET_NAME')
    if not bucket_name:
        print("Error: GS_BUCKET_NAME environment variable not set.")
        return

    print(f"Connecting to Google Cloud Storage bucket: {bucket_name}")
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
    except Exception as e:
        print(f"Failed to initialize GCS client: {e}")
        print("You might need to run: gcloud auth application-default login")
        return

    media_root = settings.MEDIA_ROOT
    print(f"Local media directory: {media_root}")

    # List all blobs in the bucket
    blobs = bucket.list_blobs()
    downloaded_count = 0
    skipped_count = 0

    for blob in blobs:
        # Ignore empty directories
        if blob.name.endswith('/'):
            continue

        local_path = os.path.join(media_root, blob.name)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        if not os.path.exists(local_path):
            print(f"Downloading: {blob.name}")
            try:
                blob.download_to_filename(local_path)
                downloaded_count += 1
            except Exception as e:
                print(f"  Error downloading {blob.name}: {e}")
        else:
            # Optionally check if sizes match, but for now just skip if exists logs output will be too noisy
            skipped_count += 1

    print("\n--- Download Summary ---")
    print(f"Downloaded: {downloaded_count} files")
    print(f"Skipped (already exists): {skipped_count} files")

if __name__ == "__main__":
    download_media()
