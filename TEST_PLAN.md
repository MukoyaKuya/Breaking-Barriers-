# Test Plan for BBInternational Platform Optimizations

## Overview

This test plan verifies that all implemented optimizations are working correctly and delivering the expected performance improvements.

**Test Environment Requirements:**
- Django development server running
- Redis running (optional - app works with LocMemCache fallback)
- Database with sample data (at least 50+ articles, 100+ gallery items)
- Browser developer tools (Network tab, Performance tab)

---

## Test Suite 1: Database Query Optimization

### Test 1.1: Verify Query Count Reduction
**Objective:** Confirm database queries per page are reduced from 15-25 to 5-10.

**Steps:**
1. Enable Django Debug Toolbar or query logging:
   ```python
   # In settings.py (DEBUG=True)
   LOGGING = {
       'version': 1,
       'handlers': {
           'console': {
               'class': 'logging.StreamHandler',
           },
       },
       'loggers': {
           'django.db.backends': {
               'level': 'DEBUG',
               'handlers': ['console'],
           },
       },
   }
   ```

2. Clear cache: `python manage.py shell` → `from django.core.cache import cache; cache.clear()`

3. Load home page: `http://localhost:8000/`

4. Check query count in logs or Django Debug Toolbar

**Expected Result:**
- Query count: **5-10 queries** (down from 15-25)
- No N+1 query patterns visible
- Singleton models (HeroSettings, CTACard) loaded efficiently

**Pass Criteria:** Query count ≤ 10 queries per page load

---

### Test 1.2: Verify Database Indexes
**Objective:** Confirm indexes are created and improving query performance.

**Steps:**
1. Connect to database:
   ```bash
   # PostgreSQL
   psql -d your_database_name
   
   # Or SQLite
   sqlite3 db.sqlite3
   ```

2. Check indexes exist:
   ```sql
   -- PostgreSQL
   SELECT indexname, tablename 
   FROM pg_indexes 
   WHERE schemaname = 'public' 
   AND tablename LIKE 'church_%';
   
   -- SQLite
   .indexes church_newsitem
   ```

3. Verify key indexes:
   - `church_news_is_publ_f002c3_idx` on NewsItem (is_published, created_at)
   - `church_word_is_publ_682c08_idx` on WordOfTruth (is_published, created_at)
   - `church_info_card_ty_9e82bf_idx` on InfoCard (card_type, is_active)

**Expected Result:**
- All indexes from migrations `0028` and `0029` exist
- Index names match expected patterns

**Pass Criteria:** All expected indexes present in database

---

### Test 1.3: Verify Optimized Query Functions
**Objective:** Confirm `query_utils.py` functions return correct data efficiently.

**Steps:**
1. Open Django shell: `python manage.py shell`

2. Test query functions:
   ```python
   from church.query_utils import *
   from django.db import connection
   
   # Reset query log
   connection.queries_log.clear()
   
   # Test functions
   news = get_optimized_news_items(limit=6)
   testimonials = get_optimized_testimonials(limit=6)
   hero = get_cached_hero_settings()
   cta = get_cached_cta_card()
   
   # Check query count
   print(f"Queries executed: {len(connection.queries)}")
   ```

**Expected Result:**
- Functions return correct querysets
- Query count is minimal
- Cached singletons return same object on subsequent calls

**Pass Criteria:** All functions work correctly, query count is low

---

## Test Suite 2: Caching Functionality

### Test 2.1: Verify Redis Cache Backend
**Objective:** Confirm Redis caching is working (if Redis is configured).

**Steps:**
1. Set `REDIS_URL` environment variable: `export REDIS_URL=redis://localhost:6379/1`

2. Test cache connection:
   ```python
   python manage.py shell
   from django.core.cache import cache
   
   # Test cache
   cache.set('test_key', 'test_value', 30)
   result = cache.get('test_key')
   print(f"Cache test: {result}")  # Should print 'test_value'
   ```

3. Check Redis directly (if accessible):
   ```bash
   redis-cli
   KEYS bbi:*
   ```

**Expected Result:**
- Cache set/get operations work
- Keys prefixed with `bbi:` appear in Redis
- Cache timeout works correctly

**Pass Criteria:** Cache operations succeed, keys visible in Redis

---

### Test 2.2: Verify LocMemCache Fallback
**Objective:** Confirm app works without Redis using in-memory cache.

**Steps:**
1. Unset `REDIS_URL` environment variable

2. Restart Django server

3. Test cache:
   ```python
   python manage.py shell
   from django.core.cache import cache
   print(cache.__class__.__name__)  # Should be 'LocMemCache'
   ```

4. Load home page - should work without errors

**Expected Result:**
- App uses LocMemCache when Redis unavailable
- No errors in logs
- Pages load successfully

**Pass Criteria:** App functions correctly with LocMemCache

---

### Test 2.3: Verify Singleton Caching
**Objective:** Confirm HeroSettings, CTACard, AboutPage are cached.

**Steps:**
1. Clear cache: `python manage.py shell` → `from django.core.cache import cache; cache.clear()`

2. Load home page (first request)

3. Check cache keys:
   ```python
   python manage.py shell
   from django.core.cache import cache
   
   # Check if singletons are cached
   hero = cache.get('bbi_hero_settings')
   cta = cache.get('bbi_cta_card')
   about = cache.get('bbi_about_page')
   
   print(f"Hero cached: {hero is not None}")
   print(f"CTA cached: {cta is not None}")
   print(f"About cached: {about is not None}")
   ```

4. Load home page again (second request)

5. Verify database queries - should be fewer on second request

**Expected Result:**
- Singleton objects cached after first access
- Cache keys exist: `bbi_hero_settings`, `bbi_cta_card`, `bbi_about_page`
- Second page load has fewer database queries

**Pass Criteria:** Singletons cached, query count reduced on subsequent loads

---

### Test 2.4: Verify View-Level Caching
**Objective:** Confirm `@cache_page` decorators are working.

**Steps:**
1. Clear cache

2. Load home page: `http://localhost:8000/`
   - Note response time in browser Network tab

3. Load home page again immediately
   - Note response time (should be much faster)

4. Check cache headers in browser DevTools:
   - Response headers should indicate caching

5. Test cache timeout:
   - Wait 15+ minutes (or temporarily set timeout to 60 seconds for testing)
   - Load page again - should regenerate cache

**Expected Result:**
- First load: Normal response time (200-500ms)
- Second load: Very fast (< 100ms) - served from cache
- Cache expires after timeout period

**Pass Criteria:** Page loads faster on second request, cache expires correctly

---

## Test Suite 3: Cache Invalidation

### Test 3.1: Verify News Item Cache Invalidation
**Objective:** Confirm cache clears when NewsItem is saved/deleted.

**Steps:**
1. Load home page (populates cache)

2. Verify cache exists:
   ```python
   python manage.py shell
   from django.core.cache import cache
   hero = cache.get('bbi_hero_settings')
   print(f"Cache exists: {hero is not None}")
   ```

3. Create/update a NewsItem in Django admin:
   - Go to admin → News Items
   - Create new or edit existing item
   - Save

4. Check cache again:
   ```python
   python manage.py shell
   from django.core.cache import cache
   hero = cache.get('bbi_hero_settings')
   print(f"Cache cleared: {hero is None}")
   ```

5. Load home page - should show updated content

**Expected Result:**
- Cache cleared when NewsItem saved
- Home page shows fresh content
- Cache repopulated on next load

**Pass Criteria:** Cache invalidates correctly, fresh content appears

---

### Test 3.2: Verify Signal Registration
**Objective:** Confirm cache invalidation signals are registered.

**Steps:**
1. Check signals are loaded:
   ```python
   python manage.py shell
   from django.db.models.signals import post_save
   from church.models import NewsItem
   
   # Check if signal is connected
   receivers = post_save.receivers
   print(f"Post-save receivers: {len(receivers)}")
   ```

2. Verify signal fires:
   ```python
   # In Django shell
   from church.models import NewsItem
   from django.core.cache import cache
   
   # Set a test cache key
   cache.set('test_invalidation', 'test', 3600)
   
   # Create a news item (triggers signal)
   news = NewsItem.objects.create(
       title='Test',
       slug='test-cache-invalidation',
       summary='Test',
       body='Test',
       is_published=False
   )
   
   # Check if cache was cleared
   hero = cache.get('bbi_hero_settings')
   print(f"Cache cleared: {hero is None}")
   ```

**Expected Result:**
- Signals are registered
- Cache clears when models are saved
- No errors in logs

**Pass Criteria:** Signals work correctly, cache invalidates

---

## Test Suite 4: Pagination

### Test 4.1: Verify Word of Truth Pagination
**Objective:** Confirm pagination works for Word of Truth articles.

**Prerequisites:** Create 25+ WordOfTruth articles in admin

**Steps:**
1. Load Word of Truth page: `http://localhost:8000/word-of-truth/`

2. Verify:
   - Only 20 articles displayed on first page
   - Pagination controls visible at bottom
   - Shows "Showing 1–20 of X results"

3. Click "Next" button

4. Verify:
   - Next 20 articles displayed
   - URL includes `?page=2`
   - Pagination shows correct page number

5. Test edge cases:
   - Go to page 999 (should show last page)
   - Go to page 0 or negative (should show first page)
   - Go to non-numeric page (should show first page)

**Expected Result:**
- 20 articles per page
- Pagination controls work correctly
- Edge cases handled gracefully
- URL parameters preserved

**Pass Criteria:** Pagination displays correctly, navigation works

---

### Test 4.2: Verify Gallery Pagination
**Objective:** Confirm pagination works for Gallery with HTMX.

**Prerequisites:** Create 30+ GalleryImage items

**Steps:**
1. Load gallery page: `http://localhost:8000/gallery/`

2. Verify:
   - Only 24 items displayed
   - Pagination controls visible
   - Grid layout maintained

3. Click "Next" page

4. Verify:
   - HTMX loads next page (if HTMX enabled)
   - Or full page reload works
   - Category filter preserved in pagination URLs

5. Test with category filter:
   - Click a category filter
   - Verify pagination resets to page 1
   - Verify category parameter preserved in pagination URLs

**Expected Result:**
- 24 items per page
- Pagination works with HTMX
- Category filters work with pagination
- URL parameters preserved

**Pass Criteria:** Gallery pagination works, filters preserved

---

### Test 4.3: Verify Search Pagination
**Objective:** Confirm search results are paginated.

**Steps:**
1. Perform search: `http://localhost:8000/search/?q=test`

2. Verify:
   - Maximum 12 results per page
   - Pagination controls visible if > 12 results
   - Search query preserved in pagination URLs

3. Navigate to page 2

4. Verify:
   - Next 12 results displayed
   - Search query still in URL: `?q=test&page=2`

**Expected Result:**
- 12 results per page
- Search query preserved
- Pagination works correctly

**Pass Criteria:** Search pagination works, query preserved

---

## Test Suite 5: Performance Testing

### Test 5.1: Page Load Time (Cached)
**Objective:** Measure page load time with caching enabled.

**Tools:** Browser DevTools Network tab

**Steps:**
1. Clear cache and browser cache

2. Load home page (first request):
   - Record: Time to First Byte (TTFB)
   - Record: Total load time
   - Record: Database query count

3. Load home page again (cached):
   - Record: TTFB (should be < 100ms)
   - Record: Total load time (should be < 500ms)

**Expected Result:**
- First load: TTFB < 500ms, Total < 2s
- Cached load: TTFB < 100ms, Total < 500ms
- 80-90% improvement on cached loads

**Pass Criteria:** Cached pages load 80%+ faster

---

### Test 5.2: Database Query Performance
**Objective:** Measure query execution time with indexes.

**Steps:**
1. Enable query logging (see Test 1.1)

2. Load home page

3. Analyze query times in logs:
   ```python
   from django.db import connection
   for q in connection.queries:
       print(f"{q['time']}s - {q['sql'][:100]}")
   ```

4. Verify:
   - No queries taking > 100ms
   - Indexed queries are fast
   - Total query time < 200ms

**Expected Result:**
- All queries < 100ms
- Indexed fields query quickly
- Total query time < 200ms

**Pass Criteria:** All queries execute quickly with indexes

---

### Test 5.3: Concurrent Request Handling
**Objective:** Test application under concurrent load.

**Tools:** Apache Bench (ab) or similar

**Steps:**
1. Start Django server with optimized Gunicorn:
   ```bash
   gunicorn --workers 5 --threads 4 church_app.wsgi:application
   ```

2. Run load test:
   ```bash
   ab -n 1000 -c 50 http://localhost:8000/
   ```

3. Analyze results:
   - Requests per second
   - Average response time
   - Failed requests (should be 0)

**Expected Result:**
- Handles 50+ concurrent requests
- Average response time < 500ms
- No failed requests
- Requests per second > 50

**Pass Criteria:** Handles concurrent load without errors

---

## Test Suite 6: Edge Cases & Error Handling

### Test 6.1: Empty Database
**Objective:** Verify app handles empty database gracefully.

**Steps:**
1. Clear all data (or use fresh database)

2. Load all pages:
   - Home page
   - Word of Truth page
   - Gallery page
   - Search page

**Expected Result:**
- No errors or 500 pages
- Empty state messages displayed
- Pagination shows "0 results"

**Pass Criteria:** App handles empty state gracefully

---

### Test 6.2: Cache Failure Handling
**Objective:** Verify app works if cache fails.

**Steps:**
1. Configure invalid Redis URL: `REDIS_URL=redis://invalid:6379/1`

2. Start Django server

3. Load pages - should fall back to LocMemCache or work without cache

**Expected Result:**
- No crashes
- Pages load (may be slower)
- Errors logged but don't break app

**Pass Criteria:** App degrades gracefully on cache failure

---

### Test 6.3: Large Dataset Handling
**Objective:** Verify pagination handles large datasets.

**Prerequisites:** Create 1000+ articles (or use database with many records)

**Steps:**
1. Load Word of Truth page

2. Navigate through pages:
   - First page loads quickly
   - Last page loads quickly
   - Middle pages load quickly

3. Check memory usage (should be stable)

**Expected Result:**
- All pages load quickly regardless of total count
- Memory usage stable
- No performance degradation

**Pass Criteria:** Handles large datasets efficiently

---

## Test Suite 7: Integration Testing

### Test 7.1: Full User Journey
**Objective:** Test complete user flow with optimizations.

**Steps:**
1. **Home Page**
   - Load home page
   - Verify all sections load
   - Check query count
   - Verify cache is populated

2. **Browse Articles**
   - Click "Word of Truth"
   - Navigate through pagination
   - Click article detail
   - Verify sidebar loads

3. **Search**
   - Perform search
   - Navigate search results
   - Click result

4. **Gallery**
   - Browse gallery
   - Filter by category
   - Navigate pagination
   - View lightbox

**Expected Result:**
- All pages load quickly
- Navigation smooth
- No errors
- Cache working throughout

**Pass Criteria:** Complete user journey works smoothly

---

### Test 7.2: Admin Workflow
**Objective:** Verify admin can update content and cache invalidates.

**Steps:**
1. Login as admin

2. Load home page (note content)

3. Update HeroSettings in admin

4. Load home page again

5. Verify:
   - Cache cleared
   - New content appears
   - No stale data

**Expected Result:**
- Admin changes reflected immediately
- Cache invalidates correctly
- No stale content

**Pass Criteria:** Admin workflow works with cache invalidation

---

## Test Suite 8: Browser Compatibility

### Test 8.1: Cross-Browser Testing
**Objective:** Verify optimizations work across browsers.

**Browsers to Test:**
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (if on Mac)

**Steps:**
1. Load home page in each browser

2. Test pagination in each browser

3. Verify cache headers respected

**Expected Result:**
- Works in all modern browsers
- Pagination functions correctly
- No JavaScript errors

**Pass Criteria:** Works across all tested browsers

---

## Performance Benchmarks

### Target Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Database queries (home) | ≤ 10 | Django Debug Toolbar / Logging |
| Page load (cached) | < 500ms | Browser DevTools |
| Page load (uncached) | < 2s | Browser DevTools |
| Query execution time | < 100ms each | Database logs |
| Concurrent users | 1000+ | Load testing tool |
| Cache hit rate | > 80% | Cache statistics |

---

## Test Execution Checklist

### Pre-Testing Setup
- [ ] Django server running
- [ ] Redis running (optional)
- [ ] Database populated with test data
- [ ] Browser DevTools open
- [ ] Query logging enabled

### Quick Smoke Test (5 minutes)
- [ ] Home page loads
- [ ] Pagination appears on list pages
- [ ] Cache works (faster second load)
- [ ] No errors in console

### Full Test Suite (30-60 minutes)
- [ ] Test Suite 1: Database Optimization
- [ ] Test Suite 2: Caching Functionality
- [ ] Test Suite 3: Cache Invalidation
- [ ] Test Suite 4: Pagination
- [ ] Test Suite 5: Performance Testing
- [ ] Test Suite 6: Edge Cases
- [ ] Test Suite 7: Integration Testing
- [ ] Test Suite 8: Browser Compatibility

### Post-Testing
- [ ] Document any issues found
- [ ] Verify all pass criteria met
- [ ] Performance metrics recorded
- [ ] Test results documented

---

## Automated Testing Scripts

### Quick Performance Test
```python
# test_performance.py
from django.test import Client
from django.core.cache import cache
import time

client = Client()
cache.clear()

# First load (uncached)
start = time.time()
response = client.get('/')
uncached_time = time.time() - start

# Second load (cached)
start = time.time()
response = client.get('/')
cached_time = time.time() - start

print(f"Uncached: {uncached_time:.3f}s")
print(f"Cached: {cached_time:.3f}s")
print(f"Improvement: {(1 - cached_time/uncached_time)*100:.1f}%")
```

Run with: `python manage.py shell < test_performance.py`

---

## Reporting Issues

If tests fail, document:
1. **Test Case**: Which test failed
2. **Expected Result**: What should have happened
3. **Actual Result**: What actually happened
4. **Steps to Reproduce**: How to trigger the issue
5. **Environment**: Django version, Python version, Redis version
6. **Error Messages**: Full error traceback if applicable

---

**Test Plan Version**: 1.0  
**Last Updated**: January 29, 2026  
**Status**: Ready for Execution
