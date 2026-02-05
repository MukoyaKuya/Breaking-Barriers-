import os
import django
from django.conf import settings
import dj_database_url
import sys
import json

sys.path.append(os.getcwd())

# 1. Configure for Neon DB (Target)
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

from church.models import Partner, InfoCard, NewsItem, GalleryImage, Testimonial, WordOfTruth, ChildrensBread, NewsLine, Book, AboutPage

def merge_data():
    dump_file = 'local_church_dump.json'
    if not os.path.exists(dump_file):
        print(f"Error: {dump_file} not found.")
        return

    print("Loading local dump...")
    try:
        with open(dump_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        print("UTF-8 failed, trying cp1252...")
        with open(dump_file, 'r', encoding='cp1252') as f:
            data = json.load(f)

    print(f"Loaded {len(data)} objects. specific model processing starting...")

    stats = {'created': 0, 'skipped': 0, 'errors': 0}

    for item in data:
        model = item.get('model')
        fields = item.get('fields')

        try:
            if model == 'church.partner':
                # Deduplicate by Name
                obj, created = Partner.objects.get_or_create(
                    name=fields['name'],
                    defaults=fields
                )
                if created:
                    print(f"[Partner] Created: {fields['name']}")
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1

            elif model == 'church.infocard':
                # Deduplicate by Slug
                obj, created = InfoCard.objects.get_or_create(
                    slug=fields['slug'],
                    defaults=fields
                )
                if created:
                    print(f"[InfoCard] Created: {fields['title']}")
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1

            elif model == 'church.newsitem':
                # Deduplicate by Slug
                obj, created = NewsItem.objects.get_or_create(
                    slug=fields['slug'],
                    defaults=fields
                )
                if created:
                    print(f"[NewsItem] Created: {fields['title']}")
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1
            
            elif model == 'church.testimonial':
                 # Dupe by member_name
                obj, created = Testimonial.objects.get_or_create(
                    member_name=fields['member_name'],
                    defaults=fields
                )
                if created:
                    print(f"[Testimonial] Created: {fields['member_name']}")
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1

            elif model == 'church.galleryimage':
                # Dupe by caption + category
                obj, created = GalleryImage.objects.get_or_create(
                    caption=fields.get('caption', ''),
                    category=fields.get('category', 'Other'),
                    defaults=fields
                )
                if created:
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1

            elif model == 'church.wordoftruth':
                obj, created = WordOfTruth.objects.get_or_create(
                    slug=fields['slug'],
                    defaults=fields
                )
                if created:
                    print(f"[WordOfTruth] Created: {fields['title']}")
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1

            elif model == 'church.childrensbread':
                obj, created = ChildrensBread.objects.get_or_create(
                    slug=fields['slug'],
                    defaults=fields
                )
                if created:
                    print(f"[ChildrensBread] Created: {fields['title']}")
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1

            elif model == 'church.newsline':
                obj, created = NewsLine.objects.get_or_create(
                    slug=fields['slug'],
                    defaults=fields
                )
                if created:
                    print(f"[NewsLine] Created: {fields['title']}")
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1

            elif model == 'church.book':
                obj, created = Book.objects.get_or_create(
                    slug=fields['slug'],
                    defaults=fields
                )
                if created:
                    print(f"[Book] Created: {fields['title']}")
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1
            
            elif model == 'church.aboutpage':
                # Singleton logic
                obj, created = AboutPage.objects.get_or_create(pk=1)
                for field, value in fields.items():
                    if field != 'id' and field != 'pk':
                         setattr(obj, field, value)
                obj.save()
                stats['created'] += 1 # Update counts as created/actioned

            # Add other models as needed, or generic fallback if careful
            
        except Exception as e:
            print(f"Error importing {model}: {e}")
            stats['errors'] += 1

    print("-" * 30)
    print(f"Merge Complete. Stats: {stats}")

if __name__ == '__main__':
    merge_data()
