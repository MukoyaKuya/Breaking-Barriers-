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
            'church',
             'image_cropping',
            'easy_thumbnails',
        ],
        STATIC_URL='/static/',
    )
    django.setup()

from church.models import InfoCard

def inspect_infocards():
    print("--- Inspecting InfoCards in Neon ---")
    cards = InfoCard.objects.all()
    for card in cards:
        print(f"ID: {card.id}")
        print(f"  Title: {card.title}")
        print(f"  Type: {card.card_type}")
        print(f"  Active: {card.is_active}")
        print(f"  Slug: {card.slug}")
        print("-" * 20)

    if not cards:
        print("NO INFO CARDS FOUND.")

if __name__ == '__main__':
    inspect_infocards()
