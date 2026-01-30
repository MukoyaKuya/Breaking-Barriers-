
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from easy_thumbnails.models import Source, Thumbnail

def clear_thumbnails():
    print("Clearing easy_thumbnails database entries...")
    t_count, _ = Thumbnail.objects.all().delete()
    s_count, _ = Source.objects.all().delete()
    print(f"Deleted {t_count} thumbnails and {s_count} source references.")
    print("This forces regeneration of thumbnails on next request.")

if __name__ == "__main__":
    clear_thumbnails()
