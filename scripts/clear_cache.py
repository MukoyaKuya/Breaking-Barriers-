import os
import django
import sys
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

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

from django.core.cache import cache

def clear_cache():
    print("--- Clearing Production Cache ---")
    print(f"Cache Backend: {cache}")
    try:
        cache.clear()
        print("SUCCESS: Cache cleared successfully.")
    except Exception as e:
        print(f"ERROR: Failed to clear cache: {e}")

if __name__ == '__main__':
    clear_cache()
