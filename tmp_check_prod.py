import os
import django
import json

# Setup environment for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_OsJiLV86Bkdn@ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

django.setup()

from church.models import NewsItem, NewsLine, Verse, AboutPage, MissionStatement, BoardMember

def check_prod_counts():
    print(f"--- PRODUCTION DATA AUDIT ---")
    print(f"NewsItems: {NewsItem.objects.count()}")
    print(f"NewsLineItems: {NewsLine.objects.count()}")
    print(f"Verses: {Verse.objects.count()}")
    print(f"BoardMembers: {BoardMember.objects.count()}")
    print(f"AboutPages: {AboutPage.objects.count()}")
    print(f"MissionStatements: {MissionStatement.objects.count()}")

if __name__ == "__main__":
    check_prod_counts()
