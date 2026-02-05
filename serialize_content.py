import os
import django
import json
import traceback
from django.core.management import call_command
from django.core import serializers
from django.conf import settings

# Configure settings to use Neon for this script execution only
# We do this by patching the environment before setup, or manually configuring if standalone.
# But we are using 'manage.py shell' context usually or reliance on DATABASE_URL in settings.py

NEON_DB_URL = "postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
os.environ['DATABASE_URL'] = NEON_DB_URL

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "church_app.settings")
django.setup()

def serialize_content():
    from django.contrib.auth.models import User
    import django.apps
    
    models_to_dump = [User]
    
    # Get all models from church app dynamically
    try:
        church_config = django.apps.apps.get_app_config('church')
        models_to_dump.extend(church_config.get_models())
    except Exception as e:
        print(f"Error getting church config: {e}")
        return

    all_objects = []
    
    print(f"Attempting to dump {len(models_to_dump)} models from Neon...")
    
    for model in models_to_dump:
        model_name = model._meta.object_name
        try:
            print(f"Fetching {model_name}...", end='', flush=True)
            # Use iterator to fetch efficiently, but for serialization we need a list or queryset
            qs = model.objects.all()
            count = qs.count()
            print(f" found {count}...", end='', flush=True)
            
            # Serialize individually or in chunks to catch errors per model?
            # Or just catch if the query fails (table missing)
            if count > 0:
                 # Evaluate to list to force DB hit inside try block
                 objs = list(qs)
                 all_objects.extend(objs)
                 print(" OK.")
            else:
                 print(" Empty.")
                 
        except Exception as e:
            print(f" FAILED: {e}")
            # Likely table missing or schema mismatch. Ignore and continue.
            
    print(f"Total objects to serialize: {len(all_objects)}")
    
    # Serialize to JSON string
    # We use Django's serializer
    try:
        json_data = serializers.serialize("json", all_objects, indent=2, use_natural_foreign_keys=True)
        
        output_file = 'neon_content.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        print(f"Successfully saved to {output_file}")
    except Exception as e:
        print(f"Serialization failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    serialize_content()
