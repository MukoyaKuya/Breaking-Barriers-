import os
import django
from django.conf import settings
import dj_database_url
import sys

sys.path.append(os.getcwd())

# Configure for Neon DB
NEON_URL = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require'

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': dj_database_url.parse(NEON_URL)
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'church',
             'image_cropping',
            'easy_thumbnails',
        ],
        STATIC_URL='/static/',
    )
    django.setup()

from django.apps import apps

def check_neon():
    print("--- [NEON] Data Counts ---")
    
    models_to_check = [
        'church.Partner',
        'church.InfoCard',
        'church.NewsItem',
        'church.GalleryImage',
        'church.Testimonial',
        'church.CalendarEvent',
        'church.Verse',
        'church.WordOfTruth',
        'church.ManTalk',
        'church.ChildrensBread',
        'church.Book',
        'church.FAQ',
        'church.SidebarPromo',
        'church.NewsLine',
         # Singletons
        'church.HeroSettings',
        'church.AboutPage',
        'church.CTACard',
        'church.MensMinistry',
    ]

    for model_name in models_to_check:
        try:
            model = apps.get_model(model_name)
            count = model.objects.count()
            print(f"{model_name.split('.')[1]}: {count}")
            
            # For singletons, print a little detail to see if content differs
            if count == 1 and model_name in ['church.HeroSettings', 'church.AboutPage']:
                 obj = model.objects.first()
                 print(f"   -> ID: {obj.pk}")

        except LookupError:
            print(f"{model_name}: NOT FOUND")
        except Exception as e:
            print(f"{model_name}: ERROR {e}")

if __name__ == '__main__':
    check_neon()
