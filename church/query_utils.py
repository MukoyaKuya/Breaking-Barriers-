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


def get_optimized_news_items(limit=6):
    """Latest published news items for list/home."""
    return NewsItem.objects.filter(
        is_published=True
    ).order_by('-created_at')[:limit]


def get_optimized_testimonials(limit=6):
    """Approved testimonials for home."""
    return Testimonial.objects.filter(
        approved=True
    ).order_by('-created_at')[:limit]


def get_optimized_gallery_items(limit=6):
    """Latest gallery items for home."""
    return GalleryImage.objects.all().order_by('-uploaded_at')[:limit]


def get_optimized_mens_ministry():
    """Latest active Men's Ministry (single)."""
    return MensMinistry.objects.filter(
        is_active=True
    ).order_by('-created_at').first()


def get_optimized_partners():
    """Active partners for carousel."""
    return Partner.objects.filter(
        is_active=True
    ).order_by('display_order', 'name')


def get_optimized_verse_of_the_day():
    """Latest active & featured verse."""
    return Verse.objects.filter(
        is_active=True,
        is_featured=True
    ).order_by('-date_posted').first()


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
    """Active FAQs for sidebar."""
    return FAQ.objects.filter(
        is_active=True
    ).order_by('display_order', 'question')


def get_optimized_sidebar_promos(limit=3):
    """Active sidebar promos."""
    return SidebarPromo.objects.filter(
        is_active=True
    ).order_by('display_order', 'created_at')[:limit]


def get_optimized_word_of_truth_list():
    """Published Word of Truth articles (list)."""
    return WordOfTruth.objects.filter(
        is_published=True
    ).order_by('-created_at')


def get_optimized_childrens_bread_preview(limit=5):
    """Latest Children's Bread articles for info card carousel preview."""
    return list(
        ChildrensBread.objects.filter(is_published=True).order_by('-created_at')[:limit]
    )


def get_optimized_news_line_preview(limit=5):
    """Latest News Line articles for info card carousel preview."""
    return list(
        NewsLine.objects.filter(is_published=True).order_by('-created_at')[:limit]
    )


def get_optimized_word_of_truth_preview(limit=5):
    """Latest Word of Truth articles for info card carousel preview."""
    return list(
        WordOfTruth.objects.filter(is_published=True).order_by('-created_at')[:limit]
    )


def get_optimized_man_talk_list(limit=3):
    """Published ManTalk articles (latest)."""
    return ManTalk.objects.filter(
        is_published=True
    ).order_by('-created_at')[:limit]


def invalidate_home_caches():
    """Clear caches that affect the home page."""
    cache.delete_many([
        'bbi_hero_settings',
        'bbi_cta_card',
        'bbi_about_page',
    ])
