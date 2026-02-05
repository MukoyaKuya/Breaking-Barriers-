import os
import django
from django.conf import settings
import sys

sys.path.append(os.getcwd())

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(os.getcwd(), 'db.sqlite3'),
            }
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

def check_local():
    print("--- [LOCAL] Data Counts ---")
    
    # List of models to check
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
        except LookupError:
            print(f"{model_name}: NOT FOUND")
        except Exception as e:
            print(f"{model_name}: ERROR {e}")

if __name__ == '__main__':
    check_local()
