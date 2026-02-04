from django.core.management.base import BaseCommand
from church.models import GalleryImage

class Command(BaseCommand):
    help = 'Aggressively clean up duplicate gallery images'

    def handle(self, *args, **options):
        items = list(GalleryImage.objects.all().order_by('id'))
        seen = set()
        count = 0
        for g in items:
            # Aggressive key: stripped and lowercase caption + category
            caption = str(g.caption).strip().lower()
            category = str(g.category).strip().lower()
            k = f"{caption}|{category}"
            
            if k in seen:
                g.delete()
                count += 1
            else:
                seen.add(k)
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} duplicate gallery images.'))
