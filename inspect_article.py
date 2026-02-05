import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from church.models import WordOfTruth

def inspect_article():
    slug = 'expecting-victory-in-the-midst-of-persecution'
    try:
        article = WordOfTruth.objects.get(slug=slug)
        print(f"Title: {article.title}")
        print(f"Summary: {article.summary[:50]}...")
        print(f"Image: {article.image}")
        print(f"Image exists in DB? {bool(article.image)}")
        if article.image:
            print(f"Image URL: {article.image.url}")
        print(f"Body length: {len(article.body) if article.body else 0}")
    except WordOfTruth.DoesNotExist:
        print("Article not found!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_article()
