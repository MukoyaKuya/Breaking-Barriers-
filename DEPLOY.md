# Deploy to Cloud Run (BBI International)

Your app is live at: **https://bbi-international-1073897174388.europe-north2.run.app/**

## Deploy new changes

### Option A: Deploy from your machine with gcloud

1. **Commit and push your code** (if not already):
   ```bash
   git add .
   git commit -m "Analytics: page visits by IP, YouTube thumbnails, PageView middleware"
   git push origin main
   ```

2. **Build and push the container image** (replace `YOUR_GCP_PROJECT_ID` with your Google Cloud project ID):
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/bbi-international
   ```
   Or if you use Artifact Registry:
   ```bash
   gcloud builds submit --tag europe-north2-docker.pkg.dev/YOUR_GCP_PROJECT_ID/YOUR_REPO/bbi-international
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy bbi-international \
     --image gcr.io/YOUR_GCP_PROJECT_ID/bbi-international \
     --region europe-north2 \
     --platform managed
   ```
   (Use the same image URL as in step 2 if you use Artifact Registry.)

4. **Migrations**: The container start script (`scripts/start.sh`) runs `python manage.py migrate --noinput` on every startup, so the new migration `0032_pageview_ip_address` will run automatically when the new revision is live.

### Option B: GitHub / Cloud Build trigger

If you have a Cloud Build trigger that builds on push:

1. Commit and push to the branch that triggers the build (e.g. `main`):
   ```bash
   git add .
   git commit -m "Analytics: page visits by IP, YouTube thumbnails, PageView middleware"
   git push origin main
   ```
2. The trigger will build the image and deploy to Cloud Run. Migrations run on container start as above.

### After deploy

- Open **https://bbi-international-1073897174388.europe-north2.run.app/** to confirm the site loads.
- New traffic will get IPs stored; **Unique visitors** on the analytics page will start counting after the new revision is live (existing rows have no IP).
- To see analytics: log in as staff and go to `/analytics/` (or use the Analytics link in the admin).
