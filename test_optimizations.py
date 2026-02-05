#!/usr/bin/env python
"""
Quick automated test script to verify optimizations are working.
Run with: python manage.py shell < test_optimizations.py
Or: python test_optimizations.py (if Django is configured)
"""
import os
import sys
import django

# Setup Django
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_app.settings')
    django.setup()

from django.test import Client
from django.core.cache import cache
from django.db import connection
from church.query_utils import (
    get_cached_hero_settings,
    get_cached_cta_card,
    get_optimized_news_items,
)
import time

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_cache_backend():
    """Test 1: Verify cache backend is configured"""
    print_section("Test 1: Cache Backend Configuration")
    
    cache_class = cache.__class__.__name__
    print(f"Cache backend: {cache_class}")
    
    # Test cache operations
    cache.set('test_key', 'test_value', 30)
    result = cache.get('test_key')
    
    if result == 'test_value':
        print("✅ Cache operations working correctly")
        return True
    else:
        print("❌ Cache operations failed")
        return False

def test_query_optimization():
    """Test 2: Verify query optimization"""
    print_section("Test 2: Database Query Optimization")
    
    # Clear query log
    connection.queries_log.clear()
    
    # Execute optimized queries
    news = list(get_optimized_news_items(limit=6))
    hero = get_cached_hero_settings()
    cta = get_cached_cta_card()
    
    query_count = len(connection.queries)
    print(f"Queries executed: {query_count}")
    
    if query_count <= 10:
        print(f"✅ Query count acceptable ({query_count} queries)")
        return True
    else:
        print(f"⚠️  Query count higher than expected ({query_count} queries)")
        return False

def test_singleton_caching():
    """Test 3: Verify singleton caching"""
    print_section("Test 3: Singleton Model Caching")
    
    # Clear cache
    cache.clear()
    
    # First access (should query database)
    connection.queries_log.clear()
    hero1 = get_cached_hero_settings()
    queries_first = len(connection.queries)
    
    # Second access (should use cache)
    connection.queries_log.clear()
    hero2 = get_cached_hero_settings()
    queries_second = len(connection.queries)
    
    print(f"Queries on first access: {queries_first}")
    print(f"Queries on second access: {queries_second}")
    
    # Check cache key exists
    cached_hero = cache.get('bbi_hero_settings')
    
    if queries_second == 0 and cached_hero is not None:
        print("✅ Singleton caching working correctly")
        return True
    else:
        print("❌ Singleton caching not working")
        return False

def test_page_load_performance():
    """Test 4: Measure page load performance"""
    print_section("Test 4: Page Load Performance")
    
    client = Client()
    
    # Clear cache
    cache.clear()
    
    # First load (uncached)
    start = time.time()
    response1 = client.get('/')
    uncached_time = time.time() - start
    
    # Second load (cached)
    start = time.time()
    response2 = client.get('/')
    cached_time = time.time() - start
    
    print(f"Uncached load time: {uncached_time:.3f}s")
    print(f"Cached load time: {cached_time:.3f}s")
    
    if cached_time < uncached_time:
        improvement = (1 - cached_time/uncached_time) * 100
        print(f"Performance improvement: {improvement:.1f}%")
        
        if improvement > 50:
            print("✅ Significant performance improvement with caching")
            return True
        else:
            print("⚠️  Caching improvement less than expected")
            return False
    else:
        print("❌ Caching not improving performance")
        return False

def test_database_indexes():
    """Test 5: Verify database indexes exist"""
    print_section("Test 5: Database Indexes")
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check for PostgreSQL
        if 'postgresql' in connection.vendor:
            cursor.execute("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND tablename LIKE 'church_%'
                AND indexname LIKE '%_idx'
                ORDER BY indexname;
            """)
            indexes = [row[0] for row in cursor.fetchall()]
        # Check for SQLite
        elif 'sqlite' in connection.vendor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'church_%';")
            indexes = [row[0] for row in cursor.fetchall()]
        else:
            print("⚠️  Database vendor not PostgreSQL or SQLite - skipping index check")
            return True
        
        print(f"Found {len(indexes)} indexes")
        
        # Check for key indexes
        key_indexes = [
            'church_news_is_publ',  # NewsItem
            'church_word_is_publ',  # WordOfTruth
            'church_info_card_ty',  # InfoCard
        ]
        
        found_key_indexes = [idx for idx in indexes if any(key in idx for key in key_indexes)]
        
        if len(found_key_indexes) >= 2:
            print(f"✅ Key indexes found: {len(found_key_indexes)}")
            return True
        else:
            print(f"⚠️  Expected more indexes, found: {len(found_key_indexes)}")
            return False

def test_pagination():
    """Test 6: Verify pagination is working"""
    print_section("Test 6: Pagination")
    
    client = Client()
    
    # Test Word of Truth pagination
    response = client.get('/word-of-truth/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for pagination controls
        has_pagination = 'pagination' in content.lower() or 'page=' in content or 'Next' in content
        
        if has_pagination:
            print("✅ Pagination controls found in Word of Truth page")
            return True
        else:
            print("⚠️  Pagination controls not found")
            return False
    else:
        print(f"❌ Page returned status {response.status_code}")
        return False

def test_cache_invalidation():
    """Test 7: Verify cache invalidation signals"""
    print_section("Test 7: Cache Invalidation")
    
    from church.models import NewsItem
    
    # Set cache
    cache.set('bbi_hero_settings', 'test_value', 3600)
    
    # Create a news item (should trigger signal)
    news, created = NewsItem.objects.get_or_create(
        slug='test-cache-invalidation',
        defaults={
            'title': 'Test Cache Invalidation',
            'summary': 'Test',
            'body': 'Test',
            'is_published': False,
        }
    )
    
    # Check if cache was cleared
    cached_value = cache.get('bbi_hero_settings')
    
    if cached_value is None:
        print("✅ Cache invalidated when NewsItem saved")
        # Cleanup
        if created:
            news.delete()
        return True
    else:
        print("⚠️  Cache not invalidated (may be expected if signal not firing)")
        # Cleanup
        if created:
            news.delete()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  BBInternational Optimization Test Suite")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Cache Backend", test_cache_backend()))
    results.append(("Query Optimization", test_query_optimization()))
    results.append(("Singleton Caching", test_singleton_caching()))
    results.append(("Page Load Performance", test_page_load_performance()))
    results.append(("Database Indexes", test_database_indexes()))
    results.append(("Pagination", test_pagination()))
    results.append(("Cache Invalidation", test_cache_invalidation()))
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Optimizations are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
