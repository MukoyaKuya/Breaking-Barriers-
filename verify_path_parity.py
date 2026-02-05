import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.apps import apps
from django.db import models

def verify_and_fix_paths():
    print("Checking database for GCS-unsafe paths (backslashes)...")
    
    modified_count = 0
    # Iterate through all models in the 'church' app
    church_app = apps.get_app_config('church')
    for model in church_app.get_models():
        # Find FileFields or ImageFields
        file_fields = [f.name for f in model._meta.fields if isinstance(f, (models.FileField, models.ImageField))]
        
        if not file_fields:
            continue
            
        print(f"\nModel: {model.__name__} (Checking fields: {', '.join(file_fields)})")
        
        for obj in model.objects.all():
            changed = False
            for field_name in file_fields:
                file_field = getattr(obj, field_name)
                if file_field and file_field.name:
                    original_name = file_field.name
                    if '\\' in original_name:
                        safe_name = original_name.replace('\\', '/')
                        print(f"  [FIX] {obj.pk}: '{original_name}' -> '{safe_name}'")
                        file_field.name = safe_name
                        changed = True
            
            if changed:
                obj.save(update_fields=file_fields)
                modified_count += 1

    print(f"\nFinished. Fixed {modified_count} records.")

if __name__ == "__main__":
    verify_and_fix_paths()
