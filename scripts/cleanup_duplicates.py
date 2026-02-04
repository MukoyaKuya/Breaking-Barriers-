from church.models import GalleryImage
from django.db import models
import collections

def cleanup():
    items = GalleryImage.objects.all().order_by('id')
    seen = {}
    to_delete = []
    
    for item in items:
        # Create a unique identifier for the content
        # caption + image path + category
        identifier = f"{item.caption}|{item.image.name if item.image else ''}|{item.category}"
        
        if identifier in seen:
            to_delete.append(item.pk)
        else:
            seen[identifier] = item.pk
            
    if to_delete:
        print(f"Found {len(to_delete)} duplicate(s). Deleting...")
        GalleryImage.objects.filter(pk__in=to_delete).delete()
        print("Cleanup complete.")
    else:
        print("No duplicates found.")

if __name__ == "__main__":
    cleanup()
