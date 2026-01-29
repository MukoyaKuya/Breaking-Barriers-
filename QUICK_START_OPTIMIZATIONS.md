# Quick Start: Critical Optimizations Implementation Guide

This guide provides step-by-step instructions for implementing the most critical optimizations immediately.

## Prerequisites

```bash
# Install required packages
pip install django-redis redis
```

## Step 1: Add Redis Caching (30 minutes)

### 1.1 Update requirements.txt
```bash
echo "django-redis==5.4.0" >> requirements.txt
echo "redis==5.0.1" >> requirements.txt
```

### 1.2 Update settings.py

Add to `church_app/settings.py`:

```python
# Add after database configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'bbi',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Add cache middleware (at the beginning and end of MIDDLEWARE list)
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # Add first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... rest of middleware ...
    'django.middleware.cache.FetchFromCacheMiddleware',  # Add last
]

# Cache settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'bbi'
```

### 1.3 Update docker-compose.yml

Add Redis service:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  app:
    # ... existing config ...
    environment:
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - redis

volumes:
  redis_data:
```

---

## Step 2: Optimize Database Queries (1 hour)

### 2.1 Create query optimization utilities

Create `church/query_utils.py`:

```python
from django.core.cache import cache
from .models import NewsItem, Testimonial, GalleryImage, InfoCard, FAQ, SidebarPromo, Verse, CTACard, HeroSettings

def get_optimized_news_items(limit=6):
    """Get news items with optimized queries"""
    return NewsItem.objects.filter(
        is_published=True
    ).only(
        'id', 'title', 'slug', 'summary', 'image', 'created_at', 'event_date'
    ).order_by('-created_at')[:limit]

def get_optimized_testimonials(limit=6):
    """Get testimonials with optimized queries"""
    return Testimonial.objects.filter(
        approved=True
    ).only(
        'id', 'member_name', 'text', 'photo', 'video_url', 'created_at'
    ).order_by('-created_at')[:limit]

def get_optimized_gallery_items(limit=6):
    """Get gallery items with optimized queries"""
    return GalleryImage.objects.all().only(
        'id', 'caption', 'image', 'video_url', 'category', 'uploaded_at', 'duration_label'
    ).order_by('-uploaded_at')[:limit]

def get_cached_singleton(model_class, cache_key, timeout=3600):
    """Get singleton model with caching"""
    obj = cache.get(cache_key)
    if obj is None:
        obj, _ = model_class.objects.get_or_create(pk=1)
        cache.set(cache_key, obj, timeout)
    return obj

def get_cached_hero_settings():
    """Get hero settings with caching"""
    return get_cached_singleton(HeroSettings, 'hero_settings', 3600)

def get_cached_cta_card():
    """Get CTA card with caching"""
    return get_cached_singleton(CTACard, 'cta_card', 3600)
```

### 2.2 Update views.py

Replace queries in `home_view`:

```python
from .query_utils import (
    get_optimized_news_items,
    get_optimized_testimonials,
    get_optimized_gallery_items,
    get_cached_hero_settings,
    get_cached_cta_card,
)

def home_view(request):
    """Home page view with optimized queries"""
    # Use optimized query functions
    news_items = get_optimized_news_items(limit=6)
    total_count = NewsItem.objects.filter(is_published=True).count()
    has_more_news = total_count > 6
    
    testimonials = get_optimized_testimonials(limit=6)
    gallery_items = get_optimized_gallery_items(limit=6)
    
    # Use cached singletons
    hero_settings = get_cached_hero_settings()
    cta_card = get_cached_cta_card()
    
    # Optimize other queries
    mens_ministry = MensMinistry.objects.filter(
        is_active=True
    ).only('id', 'title', 'video_url', 'description').order_by('-created_at').first()
    
    partners = Partner.objects.filter(
        is_active=True
    ).only('id', 'name', 'logo', 'website_url', 'display_order').order_by('display_order', 'name')
    
    verse_of_the_day = Verse.objects.filter(
        is_active=True, is_featured=True
    ).only('id', 'content', 'reference').first()
    
    # Info cards - optimize
    childrens_bread_card = InfoCard.objects.filter(
        card_type='childrens_bread', is_active=True
    ).only('id', 'title', 'slug', 'image', 'headline', 'summary').first()
    
    news_card = InfoCard.objects.filter(
        card_type='news', is_active=True
    ).only('id', 'title', 'slug', 'image', 'headline', 'summary').first()
    
    word_of_truth_card = InfoCard.objects.filter(
        card_type='word_of_truth', is_active=True
    ).only('id', 'title', 'slug', 'image', 'headline', 'summary').first()
    
    # FAQs and sidebar promos
    faqs = FAQ.objects.filter(is_active=True).only(
        'id', 'question', 'answer', 'display_order'
    ).order_by('display_order', 'question')
    
    sidebar_promos = SidebarPromo.objects.filter(
        is_active=True
    ).only('id', 'image', 'video_url', 'caption', 'link_url', 'display_order')[:3]
    
    context = {
        'news_items': news_items,
        'has_more_news': has_more_news,
        'testimonials': testimonials,
        'gallery_items': gallery_items,
        'mens_ministry': mens_ministry,
        'partners': partners,
        'hero_settings': hero_settings,
        'verse_of_the_day': verse_of_the_day,
        'childrens_bread_card': childrens_bread_card,
        'news_card': news_card,
        'word_of_truth_card': word_of_truth_card,
        'cta_card': cta_card,
        'faqs': faqs,
        'sidebar_promos': sidebar_promos,
    }
    return render(request, 'church/home.html', context)
```

---

## Step 3: Add Database Indexes (30 minutes)

### 3.1 Update models.py

Add indexes to models. Example for NewsItem:

```python
class NewsItem(models.Model):
    # ... existing fields ...
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'News Item'
        verbose_name_plural = 'News Items'
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
        ]
```

Add similar indexes to:
- `CalendarEvent`: `['event_date', 'is_published']`, `['event_type']`
- `WordOfTruth`: `['is_published', '-created_at']`, `['slug']`
- `GalleryImage`: `['category', '-uploaded_at']`
- `InfoCard`: `['card_type', 'is_active']`, `['slug']`
- `FAQ`: `['is_active', 'display_order']`
- `SidebarPromo`: `['is_active', 'display_order']`

### 3.2 Create and run migration

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Step 4: Add View-Level Caching (30 minutes)

### 4.1 Update views.py

Add cache decorators:

```python
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

@cache_page(60 * 15)  # Cache for 15 minutes
@vary_on_headers('Cookie')  # Different cache for logged-in users
def home_view(request):
    # ... existing code ...

@cache_page(60 * 30)  # Cache for 30 minutes
def about_view(request):
    # ... existing code ...

@cache_page(60 * 10)  # Cache for 10 minutes
def word_of_truth_view(request):
    # ... existing code ...
```

---

## Step 5: Optimize Gunicorn Configuration (15 minutes)

### 5.1 Update scripts/start.sh

```bash
#!/bin/bash

# Substitute the environment variables in the nginx config
envsubst '$PORT $GS_BUCKET_NAME' < /app/nginx.conf.template > /app/nginx.conf

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Calculate optimal worker count: (2 x CPU cores) + 1
# Default to 5 workers if CPU count unavailable
WORKERS=${GUNICORN_WORKERS:-5}
THREADS=${GUNICORN_THREADS:-4}

# Start Gunicorn in the background on port 8000
echo "Starting Gunicorn with $WORKERS workers and $THREADS threads..."
gunicorn \
    --bind 127.0.0.1:8000 \
    --workers $WORKERS \
    --threads $THREADS \
    --worker-class gthread \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    church_app.wsgi:application &

# Start Nginx in the foreground
echo "Starting Nginx on port $PORT..."
nginx -c /app/nginx.conf -g "daemon off;"
```

### 5.2 Update docker-compose.yml

```yaml
services:
  app:
    # ... existing config ...
    environment:
      - GUNICORN_WORKERS=5
      - GUNICORN_THREADS=4
```

---

## Step 6: Add Cache Invalidation (30 minutes)

### 6.1 Create signals.py

Create `church/signals.py`:

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import NewsItem, WordOfTruth, InfoCard, FAQ, SidebarPromo

def invalidate_home_cache():
    """Invalidate home page cache"""
    cache.delete('home_page_cache')

@receiver(post_save, sender=NewsItem)
@receiver(post_delete, sender=NewsItem)
def invalidate_news_caches(sender, instance, **kwargs):
    """Invalidate news-related caches"""
    cache.delete_many([
        'news_items_6',
        'news_items_12',
    ])
    invalidate_home_cache()

@receiver(post_save, sender=WordOfTruth)
@receiver(post_delete, sender=WordOfTruth)
def invalidate_word_of_truth_caches(sender, instance, **kwargs):
    """Invalidate Word of Truth caches"""
    cache.delete('word_of_truth_list')
    invalidate_home_cache()

@receiver(post_save, sender=InfoCard)
@receiver(post_save, sender=FAQ)
@receiver(post_save, sender=SidebarPromo)
def invalidate_sidebar_caches(sender, instance, **kwargs):
    """Invalidate sidebar-related caches"""
    invalidate_home_cache()
```

### 6.2 Update apps.py

Update `church/apps.py`:

```python
from django.apps import AppConfig

class ChurchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'church'

    def ready(self):
        import church.signals  # Import signals
```

---

## Testing the Optimizations

### Test Redis Connection

```python
# In Django shell: python manage.py shell
from django.core.cache import cache
cache.set('test', 'value', 30)
print(cache.get('test'))  # Should print 'value'
```

### Test Query Count

```python
# In Django shell
from django.db import connection
from django.test.utils import override_settings
from church.views import home_view
from django.test import RequestFactory

factory = RequestFactory()
request = factory.get('/')

# Reset query count
connection.queries_log.clear()

# Make request
response = home_view(request)

# Check query count
print(f"Query count: {len(connection.queries)}")
# Should be significantly lower than before (target: < 10)
```

### Monitor Performance

```bash
# Install django-debug-toolbar for development
pip install django-debug-toolbar

# Add to settings.py (DEBUG=True only)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

---

## Expected Results

After implementing these quick-start optimizations:

1. **Database queries**: Reduced from 15-25 to 5-10 per page
2. **Page load time**: Reduced by 60-80% for cached pages
3. **Concurrent users**: Can handle 3-5x more concurrent requests
4. **Server resources**: Lower CPU and memory usage

---

## Next Steps

1. Monitor performance metrics
2. Implement remaining optimizations from the main plan
3. Add pagination to list views
4. Implement CDN for media files
5. Add full-text search

---

## Implemented: Image, Search, Dev Tools, Monitoring, Infra

The following are already implemented in the codebase:

- **Image optimization (WebP):** Thumbnails get a WebP copy via `thumbnail_created` signal; templates use `<picture>` with `source type="image/webp"` and `<img>` fallback. See `church/signals.py` and thumbnail-using templates.
- **Search autocomplete:** `GET /search/autocomplete/?q=...` returns JSON suggestions (news + Word of Truth). Header search (desktop and mobile) uses debounced autocomplete with Alpine.js.
- **Django Debug Toolbar:** Optional when `DEBUG=True`; add `django-debug-toolbar` to `requirements.txt` and install. Toolbar is only loaded if the package is installed.
- **Production monitoring:** `/health/` checks DB and returns 200/503. Production logging writes to `logs/django.log`. See **MONITORING.md**.
- **Load balancing / read replicas:** Set `REPLICA_DATABASE_URL` alongside `DATABASE_URL` to send reads to replica. See **INFRA.md** and `church_app/db_router.py`.

---

**Note**: Test all changes in a development environment before deploying to production!
