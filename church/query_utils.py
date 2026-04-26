"""
Optimized query helpers and cached singletons for church app.
Reduces database queries and caches frequently used singleton models.
"""
from django.core.cache import cache

from .models import (
    NewsItem,
    Testimonial,
    GalleryImage,
    MensMinistry,
    Partner,
    Verse,
    InfoCard,
    FAQ,
    SidebarPromo,
    HeroSettings,
    CTACard,
    AboutPage,
    WordOfTruth,
    ManTalk,
    ChildrensBread,
    NewsLine,
    WordOfTruth,
    ManTalk,
    ChildrensBread,
    NewsLine,
    MN,
    BoardMember,
)

# Cache timeouts (seconds)
SINGLETON_CACHE_TIMEOUT = 3600  # 1 hour
LIST_CACHE_TIMEOUT = 300       # 5 minutes


def get_cached_singleton(model_class, cache_key, timeout=SINGLETON_CACHE_TIMEOUT):
    """Get singleton model (pk=1) with caching."""
    obj = cache.get(cache_key)
    if obj is None:
        obj, _ = model_class.objects.get_or_create(pk=1)
        cache.set(cache_key, obj, timeout)
    return obj


def get_cached_hero_settings():
    """Hero section settings (cached)."""
    return get_cached_singleton(HeroSettings, 'bbi_hero_settings')


def get_cached_cta_card():
    """CTA card (cached)."""
    return get_cached_singleton(CTACard, 'bbi_cta_card')


def get_cached_about_page():
    """About page content (cached)."""
    return get_cached_singleton(AboutPage, 'bbi_about_page')


def get_cached_maintenance_settings():
    """Maintenance settings (cached)."""
    return get_cached_singleton(MN, 'bbi_maintenance_settings')


def get_optimized_news_items(limit=6):
    """Latest published news items for list/home (cached)."""
    cache_key = f'bbi_news_items_{limit}'
    items = cache.get(cache_key)
    if items is None:
        items = list(NewsItem.objects.filter(is_published=True).order_by('-created_at')[:limit])
        cache.set(cache_key, items, LIST_CACHE_TIMEOUT)
    return items


def get_optimized_testimonials(limit=6):
    """Approved testimonials for home (cached)."""
    cache_key = f'bbi_testimonials_{limit}'
    items = cache.get(cache_key)
    if items is None:
        items = list(Testimonial.objects.filter(approved=True).order_by('-created_at')[:limit])
        cache.set(cache_key, items, LIST_CACHE_TIMEOUT)
    return items


def get_optimized_gallery_items(limit=6):
    """Latest gallery items for home (cached)."""
    cache_key = f'bbi_gallery_items_{limit}'
    items = cache.get(cache_key)
    if items is None:
        items = list(GalleryImage.objects.all().order_by('-uploaded_at')[:limit])
        cache.set(cache_key, items, LIST_CACHE_TIMEOUT)
    return items


def get_optimized_mens_ministry():
    """Latest active Men's Ministry (cached)."""
    cache_key = 'bbi_mens_ministry'
    item = cache.get(cache_key)
    if item is None:
        item = MensMinistry.objects.filter(is_active=True).order_by('-created_at').first()
        cache.set(cache_key, item, LIST_CACHE_TIMEOUT)
    return item


def get_optimized_partners():
    """Active partners for carousel (cached)."""
    cache_key = 'bbi_partners'
    items = cache.get(cache_key)
    if items is None:
        items = list(Partner.objects.filter(is_active=True).order_by('display_order', 'name'))
        cache.set(cache_key, items, LIST_CACHE_TIMEOUT)
    return items


def get_optimized_verse_of_the_day():
    """Latest active & featured verse (no cache)."""
    return Verse.objects.filter(
        is_active=True,
        is_featured=True
    ).order_by('-date_posted').first()


def get_cached_verse_of_the_day():
    """Latest active & featured verse (cached 5 min)."""
    cache_key = 'bbi_verse_of_the_day'
    verse = cache.get(cache_key)
    if verse is None:
        verse = get_optimized_verse_of_the_day()
        cache.set(cache_key, verse, LIST_CACHE_TIMEOUT)
    return verse


def get_optimized_info_cards():
    """Active info cards by type (childrens_bread, news, word_of_truth). Single query."""
    cards = list(
        InfoCard.objects.filter(is_active=True).order_by('card_type')
    )
    by_type = {c.card_type: c for c in cards}
    return {
        'childrens_bread': by_type.get('childrens_bread'),
        'news': by_type.get('news'),
        'word_of_truth': by_type.get('word_of_truth'),
    }


def get_optimized_faqs():
    """Active FAQs for sidebar (no cache - used in detail views)."""
    return FAQ.objects.filter(
        is_active=True
    ).order_by('display_order', 'question')


def get_cached_faqs():
    """Active FAQs for sidebar (cached 5 min)."""
    cache_key = 'bbi_faqs'
    faqs = cache.get(cache_key)
    if faqs is None:
        faqs = list(get_optimized_faqs())
        cache.set(cache_key, faqs, LIST_CACHE_TIMEOUT)
    return faqs


def get_optimized_sidebar_promos(limit=3):
    """Active sidebar promos (no cache)."""
    return SidebarPromo.objects.filter(
        is_active=True
    ).order_by('display_order', 'created_at')[:limit]


def get_cached_sidebar_promos(limit=3):
    """Active sidebar promos (cached 5 min)."""
    cache_key = f'bbi_sidebar_promos_{limit}'
    promos = cache.get(cache_key)
    if promos is None:
        promos = list(get_optimized_sidebar_promos(limit))
        cache.set(cache_key, promos, LIST_CACHE_TIMEOUT)
    return promos


def get_optimized_word_of_truth_list():
    """Published Word of Truth articles (list)."""
    return WordOfTruth.objects.filter(
        is_published=True
    ).order_by('-created_at')


def get_optimized_childrens_bread_preview(limit=5):
    """Latest Children's Bread articles for info card carousel preview (cached)."""
    cache_key = f'bbi_cb_preview_{limit}'
    items = cache.get(cache_key)
    if items is None:
        items = list(ChildrensBread.objects.filter(is_published=True).order_by('-created_at')[:limit])
        cache.set(cache_key, items, LIST_CACHE_TIMEOUT)
    return items


def get_optimized_news_line_preview(limit=5):
    """Latest News Line articles for info card carousel preview (cached)."""
    cache_key = f'bbi_nl_preview_{limit}'
    items = cache.get(cache_key)
    if items is None:
        items = list(NewsLine.objects.filter(is_published=True).order_by('-created_at')[:limit])
        cache.set(cache_key, items, LIST_CACHE_TIMEOUT)
    return items


def get_optimized_word_of_truth_preview(limit=5):
    """Latest Word of Truth articles for info card carousel preview (cached)."""
    cache_key = f'bbi_wot_preview_{limit}'
    items = cache.get(cache_key)
    if items is None:
        items = list(WordOfTruth.objects.filter(is_published=True).order_by('-created_at')[:limit])
        cache.set(cache_key, items, LIST_CACHE_TIMEOUT)
    return items


def get_optimized_man_talk_list(limit=3):
    """Published ManTalk articles (latest)."""
    return ManTalk.objects.filter(
        is_published=True
    ).order_by('-created_at')[:limit]


def get_optimized_board_members():
    """Active Board Members for Leadership page."""
    return BoardMember.objects.filter(
        is_active=True
    ).order_by('display_order', 'name')


def invalidate_home_caches():
    """Clear caches that affect the home page and article detail sidebars."""
    cache.delete_many([
        'bbi_hero_settings',
        'bbi_cta_card',
        'bbi_about_page',
        'bbi_faqs',
        'bbi_verse_of_the_day',
        'bbi_sidebar_promos_3',
        'bbi_maintenance_settings',
        'bbi_news_items_6',
        'bbi_testimonials_6',
        'bbi_gallery_items_6',
        'bbi_mens_ministry',
        'bbi_partners',
        'bbi_cb_preview_5',
        'bbi_nl_preview_5',
        'bbi_wot_preview_5',
    ])
