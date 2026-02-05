"""
Cache invalidation signals and thumbnail pre-generation.
Clear cached singletons when related models change.
Pre-generate thumbnails on image upload for better performance.
Generate WebP copies of thumbnails for modern browsers (use <picture> in templates).
"""
from io import BytesIO
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.core.files.base import ContentFile
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.signals import thumbnail_created

from .models import (
    NewsItem,
    WordOfTruth,
    ChildrensBread,
    NewsLine,
    InfoCard,
    FAQ,
    SidebarPromo,
    HeroSettings,
    CTACard,
    AboutPage,
    GalleryImage,
    Testimonial,
    Partner,
    Verse,
)
from .query_utils import invalidate_home_caches


@receiver(post_save, sender=HeroSettings)
@receiver(post_save, sender=CTACard)
@receiver(post_save, sender=AboutPage)
def invalidate_singleton_caches(sender, instance, **kwargs):
    """Invalidate cached singletons when Hero, CTA, or About is saved."""
    invalidate_home_caches()


@receiver(post_save, sender=NewsItem)
@receiver(post_delete, sender=NewsItem)
def invalidate_news_caches(sender, instance, **kwargs):
    """Invalidate home/sidebar caches when news changes."""
    invalidate_home_caches()
    # Also invalidate search cache when news changes
    # Note: Full pattern deletion requires django-redis, otherwise search cache expires naturally
    try:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern('bbi:search_*')
    except Exception:
        pass  # Cache backend doesn't support pattern deletion


@receiver(post_save, sender=WordOfTruth)
@receiver(post_delete, sender=WordOfTruth)
def invalidate_word_of_truth_caches(sender, instance, **kwargs):
    """Invalidate caches when Word of Truth articles change."""
    invalidate_home_caches()
    cache.delete(f'word_of_truth_{instance.slug}')
    # Also invalidate search cache
    try:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern('search_*')  # Prefix 'bbi:' is added automatically
    except Exception:
        pass  # Cache backend doesn't support pattern deletion - cache will expire naturally


@receiver(post_save, sender=ChildrensBread)
@receiver(post_delete, sender=ChildrensBread)
def invalidate_childrens_bread_caches(sender, instance, **kwargs):
    """Invalidate caches when Children's Bread articles change."""
    invalidate_home_caches()
    cache.delete(f'childrens_bread_{instance.slug}')


@receiver(post_save, sender=NewsLine)
@receiver(post_delete, sender=NewsLine)
def invalidate_news_line_caches(sender, instance, **kwargs):
    """Invalidate caches when News Line articles change."""
    invalidate_home_caches()
    cache.delete(f'news_line_{instance.slug}')


@receiver(post_save, sender=InfoCard)
@receiver(post_save, sender=FAQ)
@receiver(post_save, sender=SidebarPromo)
@receiver(post_save, sender=Verse)
def invalidate_sidebar_caches(sender, instance, **kwargs):
    """Invalidate home/sidebar caches when info cards, FAQs, promos, or verse change."""
    invalidate_home_caches()


# Thumbnail pre-generation signals
def generate_thumbnails_for_image(image_field, thumbnail_sizes=None):
    """
    Pre-generate thumbnails for an image field.
    
    Args:
        image_field: ImageField instance
        thumbnail_sizes: List of size tuples, or None to use defaults
    """
    if not image_field or not image_field.name:
        return
    
    if thumbnail_sizes is None:
        # Default sizes based on common usage
        thumbnail_sizes = [
            (100, 100),   # small
            (400, 400),   # medium
            (800, 600),   # large
            (1600, 900),  # info_card
        ]
    
    try:
        thumbnailer = get_thumbnailer(image_field)
        for size in thumbnail_sizes:
            try:
                thumbnailer.get_thumbnail({
                    'size': size,
                    'crop': 'smart',
                })
            except Exception:
                # Skip if thumbnail generation fails (e.g., invalid image)
                continue
    except Exception:
        # Fail silently - thumbnails will be generated on-demand
        pass


@receiver(post_save, sender=NewsItem)
def pregenerate_news_thumbnails(sender, instance, **kwargs):
    """Pre-generate thumbnails for NewsItem images (runs after cache invalidation)."""
    if instance.image and kwargs.get('created', False):
        # Only generate thumbnails on creation to avoid regenerating on every save
        generate_thumbnails_for_image(instance.image, [
            (400, 400),   # medium
            (800, 600),   # large (detail view)
        ])


@receiver(post_save, sender=GalleryImage)
def pregenerate_gallery_thumbnails(sender, instance, **kwargs):
    """Pre-generate thumbnails for GalleryImage."""
    if instance.image:
        generate_thumbnails_for_image(instance.image, [
            (100, 100),   # small (thumbnails)
            (400, 400),   # medium
            (800, 600),   # large
        ])


@receiver(post_save, sender=WordOfTruth)
def pregenerate_word_of_truth_thumbnails(sender, instance, **kwargs):
    """Pre-generate thumbnails for WordOfTruth images."""
    if instance.image:
        generate_thumbnails_for_image(instance.image, [
            (400, 400),   # medium
            (800, 600),   # large (detail view)
        ])


@receiver(post_save, sender=InfoCard)
def pregenerate_info_card_thumbnails(sender, instance, **kwargs):
    """Pre-generate thumbnails for InfoCard images."""
    if instance.image:
        generate_thumbnails_for_image(instance.image, [
            (400, 400),   # medium
            (1600, 900),  # info_card size
        ])


@receiver(post_save, sender=Testimonial)
def pregenerate_testimonial_thumbnails(sender, instance, **kwargs):
    """Pre-generate thumbnails for Testimonial photos."""
    if instance.photo:
        generate_thumbnails_for_image(instance.photo, [
            (100, 100),   # small
            (400, 400),   # medium (square)
        ])


@receiver(post_save, sender=Partner)
def pregenerate_partner_thumbnails(sender, instance, **kwargs):
    """Pre-generate thumbnails for Partner logos."""
    if instance.logo:
        generate_thumbnails_for_image(instance.logo, [
            (300, 200),   # partner logo size
        ])


# WebP image optimization: generate WebP copy for each thumbnail (use <picture> in templates)
WEBP_QUALITY = 85


@receiver(thumbnail_created)
def store_thumbnail_webp(sender, **kwargs):
    """
    When a thumbnail is created, also save a WebP version for smaller file size.
    Templates should use <picture><source srcset="{{ thumb.url }}.webp" type="image/webp"><img src="{{ thumb.url }}"></picture>
    """
    try:
        from PIL import Image
        thumb_file = sender
        if not getattr(thumb_file, 'name', None) or not getattr(thumb_file, 'storage', None):
            return
        # Read thumbnail content and re-encode as WebP
        thumb_file.open('rb')
        try:
            content = thumb_file.read()
        finally:
            thumb_file.close()
        if not content:
            return
        img = Image.open(BytesIO(content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
        buf = BytesIO()
        img.save(buf, 'WEBP', quality=WEBP_QUALITY)
        buf.seek(0)
        webp_name = thumb_file.name + '.webp'
        thumb_file.storage.save(webp_name, ContentFile(buf.getvalue()))
    except Exception:
        pass  # Fail silently; JPEG/PNG thumbnail is still served
