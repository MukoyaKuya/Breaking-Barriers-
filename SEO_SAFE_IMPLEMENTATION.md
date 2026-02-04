# SEO Safe Implementation Guide

This document outlines the current "Golden State" of the application and provides instructions for implementing SEO optimizations without risking database integrity or content loss.

## 1. The "Golden State" (Safe Point)

If any issues occur, you can revert the production traffic to these specific revisions to restore the "perfect" state immediately:

| Region | Service Name | Safe Revision | Status |
| :--- | :--- | :--- | :--- |
| **europe-west1** | `bbi-international` | `bbi-international-00071-96x` | Linked to Firebase |
| **europe-north2**| `bbi-international` | `bbi-international-00097-5vt` | Primary Service |

**Production Database (Neon):**
`ep-damp-water-aht3z7in-pooler.c-3.us-east-1.aws.neon.tech` (Damp Water Pooler)

---

## 2. Safe SEO Implementation Strategy

To optimize for SEO without affecting the database, follow these specific rules:

### A. Template-Only Metadata
Add meta tags to `base.html` and specific detail templates. This is "Safe" because it only changes the HTML output, not the data.

**What to add:**
- **OpenGraph Tags**: `<meta property="og:title" ...>`
- **Twitter Cards**: `<meta name="twitter:card" ...>`
- **Canonical Tags**: `<link rel="canonical" ...>`
- **JSON-LD Schema**: `<script type="application/ld+json">` snippets inside `{% block extra_head %}`.

### B. Robots.txt & Google Verification
- Serve these via `urls.py` using `TemplateView`.
- **Do not** create models for these; maintain them as static files or templates.

### C. Sitemap Generation
If using `django.contrib.sitemaps`:
1.  **Environment Variables**: Ensure `SITE_ID=1` is in your environment.
2.  **No Migrations**: Do not change any fields in `models.py`. Only add `get_absolute_url()` methods (which are logic-only and don't require database changes).

---

## 3. Safe Deployment Checklist

> [!CAUTION]
> Most database "overwrites" happen because of the `env.yaml` file.

1.  **Verify `env.yaml`**: Before every deployment, ensure the `DATABASE_URL` in your local `env.yaml` matches the **Neon** address, NOT a local or Cloud SQL address.
2.  **Deployment Command**:
    ```bash
    gcloud run deploy bbi-international --region [REGION] --source . --env-vars-file env.yaml
    ```
3.  **Traffic Split**: If a deployment looks wrong, immediately use the `gcloud run services update-traffic` command to point back to the **Revision 71** (west) or **Revision 97** (north) listed above.

---

## 4. Reversion Command (Emergency)

If the site content disappears or changes, run these immediately:

```bash
# Revert Europe West (Main)
gcloud run services update-traffic bbi-international --to-revisions bbi-international-00071-96x=100 --region europe-west1

# Revert Europe North
gcloud run services update-traffic bbi-international --to-revisions bbi-international-00097-5vt=100 --region europe-north2
```
