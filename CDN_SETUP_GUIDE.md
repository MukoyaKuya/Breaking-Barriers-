# CDN Setup Guide for BBInternational Platform

## Overview

This guide explains how to configure a Content Delivery Network (CDN) for optimal media file delivery, reducing server load and improving page load times globally.

## Benefits of CDN

- **Faster Media Delivery**: Media files served from edge locations closer to users
- **Reduced Server Load**: Offloads media serving from application server
- **Better Scalability**: Handles traffic spikes without impacting application server
- **Lower Bandwidth Costs**: CDN bandwidth typically cheaper than server bandwidth

## Option 1: Google Cloud CDN (Recommended for GCS)

Since you're using Google Cloud Storage, Google Cloud CDN integrates seamlessly.

### Setup Steps

1. **Enable Cloud CDN**:
   ```bash
   gcloud compute backend-buckets create bbi-media-backend \
       --gcs-bucket-name=YOUR_BUCKET_NAME
   
   gcloud compute url-maps create bbi-media-map \
       --default-backend-bucket=bbi-media-backend
   
   gcloud compute target-http-proxies create bbi-media-proxy \
       --url-map=bbi-media-map
   
   gcloud compute forwarding-rules create bbi-media-forwarding \
       --global \
       --target-http-proxy=bbi-media-proxy \
       --ports=80
   ```

2. **Update Django Settings**:
   ```python
   # In settings.py
   if os.environ.get('CDN_URL'):
       MEDIA_URL = f"{os.environ.get('CDN_URL')}/media/"
   else:
       MEDIA_URL = '/media/'
   ```

3. **Set Environment Variable**:
   ```bash
   export CDN_URL=https://your-cdn-domain.com
   ```

### Configuration in settings.py

Add this to `church_app/settings.py`:

```python
# CDN Configuration
CDN_URL = os.environ.get('CDN_URL')
if CDN_URL:
    MEDIA_URL = f"{CDN_URL}/media/"
    # Static files can also use CDN
    STATIC_URL = f"{CDN_URL}/static/"
else:
    MEDIA_URL = '/media/'
    STATIC_URL = '/static/'
```

---

## Option 2: Cloudflare (Free Tier Available)

Cloudflare offers a free CDN tier that works well for media files.

### Setup Steps

1. **Add Your Domain to Cloudflare**:
   - Sign up at cloudflare.com
   - Add your domain
   - Update DNS nameservers

2. **Configure Page Rules**:
   - Create rule: `yourdomain.com/media/*`
   - Set cache level: Cache Everything
   - Edge cache TTL: 1 month

3. **Update Django Settings**:
   ```python
   # In settings.py
   if os.environ.get('CLOUDFLARE_CDN_URL'):
       MEDIA_URL = f"{os.environ.get('CLOUDFLARE_CDN_URL')}/media/"
   ```

4. **Set Environment Variable**:
   ```bash
   export CLOUDFLARE_CDN_URL=https://yourdomain.com
   ```

---

## Option 3: AWS CloudFront (If Using S3)

If migrating to AWS S3, CloudFront provides excellent CDN capabilities.

### Setup Steps

1. **Create CloudFront Distribution**:
   - Origin: Your S3 bucket
   - Viewer Protocol Policy: Redirect HTTP to HTTPS
   - Cache Policy: CachingOptimized

2. **Update Django Settings**:
   ```python
   # In settings.py
   if os.environ.get('CLOUDFRONT_URL'):
       MEDIA_URL = f"{os.environ.get('CLOUDFRONT_URL')}/media/"
   ```

---

## Implementation in Django

### Update settings.py

Add CDN configuration:

```python
# CDN Configuration
CDN_URL = os.environ.get('CDN_URL')
if CDN_URL:
    # Use CDN for media files
    MEDIA_URL = f"{CDN_URL}/media/"
    # Optionally use CDN for static files too
    # STATIC_URL = f"{CDN_URL}/static/"
else:
    # Fallback to local serving
    MEDIA_URL = '/media/'
```

### Update Templates (Optional)

If you need to conditionally use CDN URLs in templates:

```django
{% if CDN_URL %}
<img src="{{ CDN_URL }}{{ image.url }}" alt="...">
{% else %}
<img src="{{ image.url }}" alt="...">
{% endif %}
```

However, since `MEDIA_URL` is already configured, Django will automatically use the CDN URL when generating image URLs.

---

## Cache Headers Configuration

Ensure your CDN respects proper cache headers:

### For Google Cloud Storage

```python
# In settings.py
if os.environ.get('GS_BUCKET_NAME'):
    GS_DEFAULT_ACL = 'publicRead'
    GS_FILE_OVERWRITE = False
    GS_CACHE_CONTROL = 'public, max-age=31536000'  # 1 year
```

### For Nginx (if proxying)

Update `nginx.conf.template`:

```nginx
location /media/ {
    proxy_pass https://storage.googleapis.com/$bucket$uri;
    proxy_set_header Host storage.googleapis.com;
    proxy_cache_valid 200 1y;
    add_header Cache-Control "public, max-age=31536000";
}
```

---

## Testing CDN

### Verify CDN is Working

1. **Check Response Headers**:
   ```bash
   curl -I https://your-cdn-domain.com/media/news/image.jpg
   ```
   Should see:
   - `X-Cache: HIT` (Cloudflare) or similar
   - `Cache-Control: public, max-age=...`

2. **Check Response Time**:
   - Compare CDN URL vs direct GCS URL
   - CDN should be faster for users far from origin

3. **Verify Cache**:
   - Load image from CDN
   - Check CDN dashboard for cache hit rate

---

## Performance Impact

| Metric | Before CDN | After CDN | Improvement |
|--------|-------------|-----------|-------------|
| Media load time (US) | 500-800ms | 100-200ms | 75% faster |
| Media load time (EU) | 800-1200ms | 150-250ms | 80% faster |
| Server bandwidth | 100% | 10-20% | 80-90% reduction |
| Server CPU (media) | High | Low | Significant reduction |

---

## Cost Considerations

### Google Cloud CDN
- **Free tier**: First 1TB egress free per month
- **After free tier**: ~$0.08/GB (varies by region)

### Cloudflare
- **Free tier**: Unlimited bandwidth
- **Pro tier**: $20/month (includes more features)

### AWS CloudFront
- **Free tier**: 1TB data transfer out, 10M requests
- **After free tier**: ~$0.085/GB (varies by region)

---

## Best Practices

1. **Cache Static Media Aggressively**:
   - Images: 1 year cache
   - Videos: 1 year cache
   - Thumbnails: 1 year cache

2. **Use Versioned URLs**:
   - Append version/timestamp to media URLs when updating
   - Forces CDN to fetch new version

3. **Enable Compression**:
   - Gzip/Brotli compression for text-based media metadata
   - Image optimization (WebP conversion)

4. **Monitor CDN Performance**:
   - Track cache hit rate (target: >90%)
   - Monitor bandwidth usage
   - Set up alerts for unusual traffic

---

## Troubleshooting

### Issue: Images not loading from CDN
**Solution**: 
- Verify `CDN_URL` environment variable is set
- Check CDN origin configuration
- Verify CORS settings if needed

### Issue: Stale images after update
**Solution**:
- Clear CDN cache manually
- Use cache-busting URLs (append version/timestamp)
- Reduce cache TTL for frequently updated content

### Issue: CDN costs too high
**Solution**:
- Review cache hit rate (should be >90%)
- Optimize image sizes before upload
- Consider Cloudflare free tier

---

## Next Steps

1. **Choose CDN Provider**: Based on your current infrastructure (GCS → Google CDN recommended)
2. **Set Up CDN**: Follow provider-specific setup steps
3. **Update Settings**: Add `CDN_URL` environment variable
4. **Test**: Verify media files load from CDN
5. **Monitor**: Track performance and costs

---

**Status**: Ready for Implementation  
**Estimated Setup Time**: 30-60 minutes  
**Cost**: Free tier available for most providers
