import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
django.setup()

from django.template.loader import render_to_string
from church.models import WordOfTruth
from django.test import RequestFactory

def test_render():
    article = WordOfTruth.objects.filter(is_published=True).first()
    if not article:
        print("No published WordOfTruth found.")
        return

    factory = RequestFactory()
    request = factory.get(article.get_absolute_url())
    
    context = {
        'word_of_truth': article,
        'faqs': [],
        'sidebar_promos': [],
        'cta_card': None,
        'verse_of_the_day': None,
        'request': request, # Important for meta tags
    }
    
    try:
        html = render_to_string('church/word_of_truth_detail.html', context)
        print("Successfully rendered!")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_render()
