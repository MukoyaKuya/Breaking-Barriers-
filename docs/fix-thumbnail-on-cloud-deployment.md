# How to Fix the Word of Truth Thumbnail Issue on Cloud Deployment

When Word of Truth pages on your **cloud deployment** (e.g. Cloud Run) show raw template tags like `{% thumbnail ... %}` or broken/missing images instead of properly cropped thumbnails, follow this guide.

---

## 1. Symptom

On the live site (e.g. **https://bbi-international-1073897174388.europe-north2.run.app/word-of-truth/**):

- Raw text such as `{% thumbnail word_of_truth.image "800x533" box=word_of_truth.image_cropping crop detail as cropped %}` appears on the page
- Article titles (e.g. "Standing Strong Through Persecution") show up as literal text next to or instead of the hero image
- Images fail to load or appear as broken thumbnails

---

## 2. Root Cause

The `{% thumbnail %}` tag from **easy-thumbnails** + **django-image-cropping** uses incorrect syntax:

- **Wrong:** `crop detail` (without `=True`) — can be misparsed by the template tag parser
- **Right:** `crop=True detail=True` — explicit boolean options required by the `crop_corners` processor

The `detail` option tells the cropping processor to use the stored crop box; omitting or misparsing it breaks thumbnail generation.

---

## 3. Fix in Templates

Ensure all thumbnail tags use `crop=True detail=True` instead of `crop detail`.

### Files to Check

| File | Fix |
|------|-----|
| `church/templates/church/word_of_truth_detail.html` | Both `{% thumbnail ... %}` tags (with and without `box`) |
| `church/templates/church/word_of_truth.html` | Cropped thumbnail tag |
| `church/templates/church/word_of_truth_list.html` | Both thumbnail tags |
| `church/templates/church/partials/word_of_truth_items.html` | Both thumbnail tags |

### Correct Syntax

**With cropping (uses saved crop box):**
```django
{% thumbnail word_of_truth.image "800x533" box=word_of_truth.image_cropping crop=True detail=True as cropped %}
<img src="{{ cropped.url }}" alt="{{ word_of_truth.title }}" ...>
```

**Without cropping (fallback when no crop is set):**
```django
{% thumbnail word_of_truth.image "800x533" crop=True detail=True as thumb %}
<img src="{{ thumb.url }}" alt="{{ word_of_truth.title }}" ...>
```

---

## 4. Deploy the Fix to Cloud Run

### Option A: Manual deploy with gcloud

1. **Commit and push the template changes:**
   ```bash
   git add church/templates/church/word_of_truth*.html church/templates/church/partials/word_of_truth_items.html
   git commit -m "Fix thumbnail tag syntax for Word of Truth (crop=True detail=True)"
   git push origin main
   ```

2. **Build and push the container:**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/bbi-international
   ```
   Or with Artifact Registry:
   ```bash
   gcloud builds submit --tag europe-north2-docker.pkg.dev/YOUR_GCP_PROJECT_ID/YOUR_REPO/bbi-international
   ```

3. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy bbi-international \
     --image gcr.io/YOUR_GCP_PROJECT_ID/bbi-international \
     --region europe-north2 \
     --platform managed
   ```

### Option B: GitHub / Cloud Build trigger

1. Commit and push to the branch that triggers the build (e.g. `main`):
   ```bash
   git add church/templates/church/word_of_truth*.html church/templates/church/partials/word_of_truth_items.html
   git commit -m "Fix thumbnail tag syntax for Word of Truth (crop=True detail=True)"
   git push origin main
   ```
2. Wait for the trigger to build and deploy; migrations run automatically on container start.

---

## 5. Clear Cache After Deploy

The app uses **Redis** (when `REDIS_URL` is set) and **view-level caching** for Word of Truth pages. Old cached HTML may still show the broken templates until caches expire or are cleared.

### Option A: Wait for natural expiry

- View cache: ~15 minutes for Word of Truth pages
- After a new revision is live, wait 15–30 minutes and hard-refresh the page

### Option B: Clear Redis cache (if you have access)

If `REDIS_URL` is set and you can run management commands against production:

```bash
# Connect to Cloud Run (or your deployment) and run:
python manage.py shell
```

Then in the shell:

```python
from django.core.cache import cache
cache.clear()
exit()
```

Or use a one-liner:

```bash
# From local machine with Cloud Run proxy, or inside the container
python manage.py shell -c "from django.core.cache import cache; cache.clear(); print('Cache cleared')"
```

### Option C: Redeploy / force new revision

Sometimes a fresh deploy forces new instances and clears in-memory caches. Re-running the deploy step can help if Redis isn’t configured or accessible.

---

## 6. Verify on Cloud

1. Open the Word of Truth list:  
   `https://your-cloud-run-url.run.app/word-of-truth/`
2. Open a Word of Truth detail page (e.g. "Standing Strong Through Persecution")
3. Confirm:
   - Hero image displays correctly (cropped when `image_cropping` is set)
   - No raw `{% thumbnail ... %}` text in the HTML
   - Article titles appear in the proper headings, not as stray text
4. Hard-refresh (Ctrl+Shift+R or Cmd+Shift+R) to avoid browser cache.

---

## 7. If You Use a CDN

If media or pages are served through Cloudflare, Cloud CDN, or similar:

1. Purge the CDN cache for the affected paths (e.g. `/word-of-truth/`, `/word-of-truth/*/`).
2. Or use cache-busting: a new deployment revision often changes asset URLs, which helps bypass CDN cache.

---

## 8. Checklist

- [ ] All Word of Truth templates use `crop=True detail=True` in `{% thumbnail %}` tags
- [ ] Changes committed and pushed
- [ ] New image built and deployed to Cloud Run
- [ ] Waited 15+ minutes or cleared Redis cache
- [ ] Word of Truth pages verified on the live URL
- [ ] CDN cache purged (if applicable)

---

## Related Docs

- [fix-word-of-truth-template-rendering.md](./fix-word-of-truth-template-rendering.md) — General template rendering fixes (dates, split tags)
- [DEPLOY.md](../DEPLOY.md) — Cloud Run deployment steps
