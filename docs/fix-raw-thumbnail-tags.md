# How to Fix Raw Thumbnail Tags Showing on the Page

When pages show **literal template tags** like `{% thumbnail book.cover_image "600x900" box=book.image_cropping crop=True detail=True as cropped %}` or `{% thumbnail article.image "800x600" ... %}` instead of rendered images, use this guide.

---

## 1. Symptom

On Books (`/books/`), Word of Truth (`/word-of-truth/`), ManTalk (`/mantalk/`), or Children's Bread (`/childrens-bread/`) you see:

- Raw `{% thumbnail ... %}` text on the page
- No images or broken image placeholders
- Article titles, descriptions, or dates may appear as plain text

---

## 2. Root Cause

**Split `{% thumbnail %}` tag** — If the tag is broken across two lines (e.g. `... as cropped` on one line and `%}` on the next), Django does not recognize it as a template tag and outputs it as literal text.

### Why does the error keep recurring?

- **Formatters and editors** — Prettier, Black, Django HTML formatters, or editor "Format on Save" often wrap long lines. When they do, they can break `{% thumbnail ... %}` (putting `%}` on the next line) or `{{ variable }}` (putting `{{` or `}}` on a separate line). Django then treats the tag as literal text and shows it on the page.
- **How to avoid it:** Keep every `{% thumbnail ... %}` and every `{{ ... }}` on a **single line**. After editing templates, avoid reformatting those files, or disable format-on-save for `church/templates/**/*.html`. If you use a formatter, add an ignore/exception for Django template tags or exclude the templates folder.
- **Caching** — This project caches querysets and (on some views) full page output. Template changes take effect as soon as the file is saved; if you still see the old output, do a hard refresh (Ctrl+Shift+R) or clear the Django cache (see §6).

---

## 3. The Fix

### Put every `{% thumbnail %}` tag on one line

The **entire** tag must be on a **single line** (including the closing `%}`).

**Wrong (split across two lines):**
```django
{% thumbnail book.cover_image "600x900" box=book.image_cropping crop=True detail=True as cropped
%}
```

**Right:**
```django
{% thumbnail book.cover_image "600x900" box=book.image_cropping crop=True detail=True as cropped %}
```

### Correct syntax

**With cropping (uses saved crop box):**
```django
{% thumbnail book.cover_image "600x900" box=book.image_cropping crop=True detail=True as cropped %}
<img src="{{ cropped.url }}" alt="{{ book.title }}" ...>
```

**Without cropping (fallback when no crop is set):**
```django
{% thumbnail book.cover_image "600x900" crop=True detail=True as thumb %}
<img src="{{ thumb.url }}" alt="{{ book.title }}" ...>
```

---

## 4. Files to Check

| Page | File | Fix |
|------|------|-----|
| Books list | `church/templates/church/book_list.html` | Put both `{% thumbnail %}` tags on one line each |
| Book detail | `church/templates/church/book_detail.html` | Same |
| Word of Truth | `church/templates/church/word_of_truth.html` | Put thumbnail tag on one line |
| Word of Truth list | `church/templates/church/word_of_truth_list.html` | Same |
| Word of Truth detail | `church/templates/church/word_of_truth_detail.html` | Same |
| Word of Truth partial | `church/templates/church/partials/word_of_truth_items.html` | Same |
| ManTalk list | `church/templates/church/mantalk_list.html` | Same |
| ManTalk detail | `church/templates/church/mantalk_detail.html` | Same |
| Children's Bread list | `church/templates/church/childrens_bread_list.html` | Same |
| Children's Bread detail | `church/templates/church/childrens_bread_detail.html` | Same |
| Children's Bread partial | `church/templates/church/partials/childrens_bread_items.html` | Same |

### Quick grep to find split tags

```bash
rg "thumbnail.*as cropped$" church/templates/
```

If you see results, those tags are split (the closing `%}` is on the next line).

---

## 5. Checklist

- [ ] Every `{% thumbnail ... %}` tag is on a single line (including `%}`)
- [ ] Use `crop=True detail=True` (not `crop detail`)
- [ ] Each template has `{% load thumbnail %}` at the top
- [ ] Restart dev server or redeploy

---

## 6. Deploy & Cache (for cloud)

1. **Commit and push:**
   ```bash
   git add church/templates/church/*.html church/templates/church/partials/*.html
   git commit -m "Fix split thumbnail tags (Books, Word of Truth, articles)"
   git push origin main
   ```

2. **Redeploy** to Cloud Run (or your platform).

3. **Clear cache** — Wait 15–30 minutes, or clear Redis:
   ```bash
   python manage.py shell -c "from django.core.cache import cache; cache.clear(); print('Cache cleared')"
   ```

---

## 7. Verify

1. **Books**: `/books/` — Cover images display; no raw `{% thumbnail %}` text.
2. **Word of Truth**: `/word-of-truth/` — Article images display.
3. **ManTalk**: `/mantalk/` — Article cards show images.
4. **Children's Bread**: `/childrens-bread/` — Same.
5. Hard-refresh (Ctrl+Shift+R) to bypass browser cache.

---

## Related docs

- [fix-article-thumbnail-and-date-rendering.md](./fix-article-thumbnail-and-date-rendering.md) — Date filters and split `{{ }}` tags
- [fix-thumbnail-on-cloud-deployment.md](./fix-thumbnail-on-cloud-deployment.md) — Cloud Run deploy steps
