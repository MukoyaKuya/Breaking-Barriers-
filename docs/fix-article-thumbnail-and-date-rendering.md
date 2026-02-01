# How to Fix Article Template Rendering (ManTalk / Children's Bread)

When article pages (ManTalk or Children's Bread) show **literal template tags and content** instead of rendered output—e.g. raw `{% thumbnail ... %}`, `{{ article.created_at|date:"M" }}`, article titles, and body text—use this guide.

---

## 1. Symptom

On ManTalk (`/mantalk/`) or Children's Bread (`/childrens-bread/`) you may see:

- Raw `{% thumbnail article.image "800x600" box=article.image_cropping crop=True detail=True as cropped %}`
- Raw `{{ article.created_at|date:"M" }}` and `{{ article.created_at|date:"d" }}`
- Article title (e.g. "The Role of Faith and Repentance in Spiritual Deliverance") as plain text
- Author name, summary, and "Read More" as unstyled text

---

## 2. Root Causes

1. **Split `{% thumbnail %}` tag**  
   If the tag is broken across two lines (e.g. `... as cropped` on one line and `%}` on the next), Django can treat it as plain text and output it literally.

2. **Split or fragile `{{ }}` tags**  
   Date filters like `{{ article.created_at|date:"M" }}` split across lines, or used in complex markup, can fail to render and appear as literal text.

3. **Relying on the `date` filter in the template**  
   Using `|date:"M"` and `|date:"d"` in list/card markup is brittle. Prefer model properties so the template only outputs a simple variable.

---

## 3. Fixes

### 3.1 Put every `{% thumbnail %}` on one line

The **entire** tag must be on a **single line** (including the closing `%}`).

**Wrong (split across two lines):**
```django
{% thumbnail article.image "800x600" box=article.image_cropping crop=True detail=True as cropped
%}
```

**Right:**
```django
{% thumbnail article.image "800x600" box=article.image_cropping crop=True detail=True as cropped %}
```

**Files to check:**

| File | What to fix |
|------|-------------|
| `church/templates/church/mantalk_list.html` | Both `{% thumbnail %}` tags (cropped and fallback) |
| `church/templates/church/mantalk_detail.html` | Both `{% thumbnail %}` tags |
| `church/templates/church/childrens_bread_list.html` | Both `{% thumbnail %}` tags |
| `church/templates/church/partials/childrens_bread_items.html` | Tags should already be on one line; confirm. |
| `church/templates/church/partials/mens_ministry.html` | Confirm thumbnail tag is on one line. |

Use the same rule for **detail** pages: e.g. `{% thumbnail article.image "800x533" ... %}` all on one line.

---

### 3.2 Use model date properties instead of `|date:"M"` and `|date:"d"`

ManTalk and ChildrensBread (and WordOfTruth) already define `created_at_month` and `created_at_day` on the model. Use those so the template does not depend on the date filter in list/card markup.

**Wrong (filter + easy to split):**
```django
<span>{{ article.created_at|date:"M" }}</span>
<span>{{ article.created_at|date:"d" }}</span>
```

**Right (one line each, use properties):**
```django
<span>{{ article.created_at_month }}</span>
<span>{{ article.created_at_day }}</span>
```

Keep each `{{ ... }}` on a **single line** (no line break inside the tag).

**Files to check:**

| File | Change |
|------|--------|
| `church/templates/church/childrens_bread_list.html` | Date badge: use `article.created_at_month` and `article.created_at_day`; keep each `{{ }}` on one line. |
| `church/templates/church/partials/childrens_bread_items.html` | Same for the date badge. |

ManTalk list already uses `article.created_at_month` and `article.created_at_day`; just ensure the `{{ }}` tags are not split across lines.

---

### 3.3 Keep all `{{ }}` and `{% %}` on single lines

- Do **not** put a line break between `{{` and the rest of the expression.
- Do **not** put a line break between `}}` and the previous part.
- Same for `{% ... %}`: the whole tag should be on one line.

**Wrong:**
```django
<span class="...">{{
    article.created_at_month }}</span>
```

**Right:**
```django
<span class="...">{{ article.created_at_month }}</span>
```

---

## 4. Checklist

- [ ] **mantalk_list.html**: Both `{% thumbnail ... %}` tags are on a single line each.
- [ ] **mantalk_detail.html**: Both `{% thumbnail ... %}` tags are on a single line each.
- [ ] **childrens_bread_list.html**: Both thumbnail tags on one line; date badge uses `created_at_month` and `created_at_day` on single lines.
- [ ] **partials/childrens_bread_items.html**: Thumbnail tags on one line; date badge uses `created_at_month` and `created_at_day` on single lines.
- [ ] No `{{` or `}}` or `{%` or `%}` split across two lines in these templates.
- [ ] Restart dev server or redeploy, then hard-refresh the article list and detail pages.

---

## 5. Verify

1. Open **ManTalk**: `/mantalk/` — cards show images and dates (e.g. "Jan", "15"); no raw tags.
2. Open a **ManTalk article** — hero image and full content render; no raw `{% thumbnail %}` or `{{ ... }}`.
3. Open **Children's Bread**: `/childrens-bread/` — same: images and dates render.
4. Open a **Children's Bread article** — hero image and content render.
5. Use "Load More" on Children's Bread and confirm new cards also render correctly.

If the live/cloud site still shows raw tags after fixing templates, redeploy and clear caches (see [fix-thumbnail-on-cloud-deployment.md](./fix-thumbnail-on-cloud-deployment.md)).

---

## 6. Related docs

- [fix-word-of-truth-template-rendering.md](./fix-word-of-truth-template-rendering.md) — Same pattern for Word of Truth.
- [fix-thumbnail-on-cloud-deployment.md](./fix-thumbnail-on-cloud-deployment.md) — Deploy and cache steps for cloud.
