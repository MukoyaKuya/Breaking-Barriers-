import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from storages.backends.gcloud import GoogleCloudStorage

def test_gcs():
    bucket_name = 'bbinternational-media'
    print(f"Testing bucket: {bucket_name}")
    try:
        storage = GoogleCloudStorage(bucket_name=bucket_name)
        print("Storage initialized successfully.")
        
        # Test listing
        try:
            dirs, files = storage.listdir('sidebar_promos/')
            print(f"sidebar_promos/ listing success: {len(files)} files found.")
            print(f"First 5: {files[:5]}")
        except Exception as e:
            print(f"Listing sidebar_promos/ failed: {e}")
            
        # Test a specific file that the browser saw 404ing
        test_file = 'sidebar_promos/Finsal.png'
        print(f"Checking existence of {test_file}...")
        try:
            exists = storage.exists(test_file)
            print(f"Exists: {exists}")
        except Exception as e:
            print(f"Exists check failed: {e}")
            
    except Exception as e:
        print(f"Failed to initialize GCS storage: {e}")

if __name__ == "__main__":
    test_gcs()
