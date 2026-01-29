# Quick Testing Guide

## Fastest Way to Verify Optimizations

### Option 1: Automated Test Script (Recommended)

Run the automated test suite:

```bash
python manage.py shell < test_optimizations.py
```

Or if Django is configured:

```bash
python test_optimizations.py
```

**Expected Output:**
- ✅ All 7 tests should pass
- Performance improvement > 50%
- Query count ≤ 10

---

### Option 2: Manual Quick Check (5 minutes)

#### 1. Check Cache is Working
```bash
python manage.py shell
```

```python
from django.core.cache import cache
cache.set('test', 'value', 30)
print(cache.get('test'))  # Should print 'value'
```

#### 2. Check Query Count
```python
from django.db import connection
from church.query_utils import get_optimized_news_items

connection.queries_log.clear()
news = list(get_optimized_news_items(6))
print(f"Queries: {len(connection.queries)}")  # Should be ≤ 5
```

#### 3. Check Pagination
- Visit: `http://localhost:8000/word-of-truth/`
- Look for pagination controls at bottom
- Should show "Showing 1–20 of X results"

#### 4. Check Caching Performance
- Load home page twice
- Second load should be much faster (< 500ms)
- Check browser Network tab for response times

---

### Option 3: Browser DevTools Check

1. **Open Browser DevTools** (F12)
2. **Go to Network tab**
3. **Load home page** (`http://localhost:8000/`)
4. **Check:**
   - Response time < 2s (first load)
   - Response time < 500ms (second load)
   - No 500 errors

5. **Check pagination:**
   - Visit `/word-of-truth/`
   - Should see pagination controls
   - Click "Next" - should work

---

## Common Issues & Solutions

### Issue: "Cache not working"
**Solution:**
- Check `REDIS_URL` is set (or app uses LocMemCache)
- Verify cache backend in settings: `print(cache.__class__.__name__)`

### Issue: "Too many queries"
**Solution:**
- Ensure migrations applied: `python manage.py migrate`
- Check indexes exist in database
- Verify `query_utils.py` is being used

### Issue: "Pagination not showing"
**Solution:**
- Ensure you have > 20 articles (for Word of Truth)
- Check template includes pagination partial
- Verify `page_obj` in context

### Issue: "Cache not invalidating"
**Solution:**
- Check signals are registered: `python manage.py shell` → `import church.signals`
- Verify `apps.py` has `ready()` method
- Check cache keys are cleared: `cache.get('bbi_hero_settings')`

---

## Performance Benchmarks

### What to Expect:

| Metric | Target | How to Check |
|--------|--------|--------------|
| Home page queries | ≤ 10 | Django shell + `connection.queries` |
| Cached page load | < 500ms | Browser Network tab |
| Uncached page load | < 2s | Browser Network tab |
| Pagination | Works | Visit list pages |
| Cache hit rate | > 80% | Monitor cache stats |

---

## Detailed Testing

For comprehensive testing, see **TEST_PLAN.md** for:
- Full test suite (8 test suites)
- Performance benchmarks
- Edge case testing
- Integration testing

---

**Quick Test Time:** ~5 minutes  
**Full Test Time:** ~30-60 minutes
