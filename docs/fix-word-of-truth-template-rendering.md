# How to Fix Word of Truth Template Rendering

When Django template tags (e.g. `{{ word_of_truth.created_at|date:"M" }}`, `{% thumbnail ... %}`, `{{ word_of_truth.title }}`) appear as **literal text** on the Word of Truth page instead of being processed, use this process.

---

## 1. Root cause

- **Split template tags**: If a `{% %}` or `{{ }}` tag is broken across multiple lines (e.g. `{{` on one line and `}}` on the next), Django can treat it as plain text.
- **Relying on the `date` filter in fragile markup**: Using `|date:"M"` and `|date:"d"` inside split or complex markup can fail to render. Moving date formatting into the model avoids that.

---

## 2. Fix in the model

Add **date helper properties** on `WordOfTruth` so the template doesn’t need the `date` filter.

**File:** `church/models.py`  
**Class:** `WordOfTruth`

Add after the `save()` method (and before `class ChildrensBread`):

```python
@property
def created_at_month(self):
    """Month abbreviation (e.g. Jan) for badge display."""
    return self.created_at.strftime('%b') if self.created_at else ''

@property
def created_at_day(self):
    """Day number (e.g. 01) for badge display."""
    return self.created_at.strftime('%d') if self.created_at else ''
```

No migration is required (these are Python-only properties).

---

## 3. Fix in the main list template

**File:** `church/templates/church/word_of_truth_list.html`

1. **Thumbnail tag – one line**  
   Ensure the whole `{% thumbnail ... %}` tag is on a single line.  
   - **Wrong:** `{% thumbnail ... as` on one line, `cropped %}` on the next.  
   - **Right:** `{% thumbnail word_of_truth.image "800x600" box=word_of_truth.image_cropping crop detail as cropped %}` all on one line.

2. **Date badge – use model properties**  
   Replace:
   - `{{ word_of_truth.created_at|date:"M" }}` → `{{ word_of_truth.created_at_month }}`
   - `{{ word_of_truth.created_at|date:"d" }}` → `{{ word_of_truth.created_at_day }}`  
   Keep each `{{ ... }}` on a **single line** (no line break inside the tag).

3. **Title and other variables**  
   Keep every `{{ variable }}` and `{% tag %}` on one line. For example:
   - `{{ word_of_truth.title }}` should not be split as `{{ word_of_truth.title` and `}}` on separate lines.

4. **Optional: simplify HTML**  
   You can put the date-badge `<div>` and its class on one line so the `{{ }}` tags stay clearly on single lines.

---

## 4. Fix in the partial (Load More)

**File:** `church/templates/church/partials/word_of_truth_items.html`

Use the same date properties so initial load and “Load More” behave the same:

- Replace `{{ word_of_truth.created_at|date:"M" }}` with `{{ word_of_truth.created_at_month }}`.
- Replace `{{ word_of_truth.created_at|date:"d" }}` with `{{ word_of_truth.created_at_day }}`.

Keep each `{{ }}` on a single line.

---

## 5. Checklist

- [ ] `WordOfTruth` in `church/models.py` has `created_at_month` and `created_at_day` properties.
- [ ] `word_of_truth_list.html`: all `{% thumbnail ... %}` and `{{ ... }}` are on single lines; date badge uses `created_at_month` and `created_at_day`.
- [ ] `partials/word_of_truth_items.html`: date badge uses `created_at_month` and `created_at_day`; no split tags.
- [ ] Restart dev server (or redeploy) and hard-refresh the Word of Truth page.

---

## 6. Verify

1. Open `/word-of-truth/` (or your full URL).
2. You should see: real month (e.g. Jan), day number, article titles, and images—no raw `{{ ... }}` or `{% thumbnail ... %}` in the HTML.
3. Click “Load More” and confirm new cards also show correct dates and titles.

If the live site still shows raw tags, clear any server-side or CDN cache and redeploy so the updated templates and code are served.
