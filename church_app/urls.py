"""
URL configuration for church_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import logging
from urllib.parse import urlparse

from django.contrib import admin
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from django.views.csrf import csrf_failure as default_csrf_failure
from django.http import JsonResponse
from django.db import connection
from django.contrib.sitemaps.views import sitemap
from church.sitemaps import StaticViewSitemap, NewsItemSitemap, WordOfTruthSitemap, ChildrensBreadSitemap, ManTalkSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'news': NewsItemSitemap,
    'word_of_truth': WordOfTruthSitemap,
    'childrens_bread': ChildrensBreadSitemap,
    'mantalk': ManTalkSitemap,
}

logger = logging.getLogger(__name__)


def _login_redirect_host(request):
    """
    Host to use for post-login redirect so the browser stays on the same
    origin and sends the session cookie. Prefer X-Forwarded-Host (client-facing)
    when present and allowed; else Referer host; else request.get_host().
    """
    allowed = getattr(settings, 'ALLOWED_HOSTS', []) or []
    forwarded = request.META.get('HTTP_X_FORWARDED_HOST', '').strip()
    if forwarded and ',' in forwarded:
        forwarded = forwarded.split(',')[0].strip()
    if forwarded and any(forwarded == h or forwarded.endswith('.' + h) for h in allowed):
        return forwarded
    referer = request.META.get('HTTP_REFERER') or ''
    if referer:
        try:
            parsed = urlparse(referer)
            if parsed.netloc and any(parsed.netloc == h or parsed.netloc.endswith('.' + h) for h in allowed):
                return parsed.netloc
        except Exception:
            pass
    return request.get_host()


def staff_login_view(request):
    """
    Custom staff login that bypasses Django admin login. Use this when admin
    login loops behind a proxy (e.g. https://bb-international.org).
    Same User model and session; after login you are sent to /admin/.
    """
    next_url = request.GET.get('next') or request.POST.get('next') or '/admin/'
    # Ensure next is same-host and safe
    if not next_url.startswith('/'):
        next_url = '/admin/'

    if request.user.is_authenticated and request.user.is_staff:
        host = _login_redirect_host(request)
        scheme = 'https' if request.is_secure() else 'http'
        url = f'{scheme}://{host}{next_url}'
        return redirect(url)

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        logger.info(f"STAFF_LOGIN: Attempting login for username='{username}'")
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            logger.info(f"STAFF_LOGIN: authenticate() result: {user}")
            
            if user is None:
                # Debug why
                from django.contrib.auth.models import User
                try:
                    u = User.objects.get(username=username)
                    is_pword_correct = u.check_password(password)
                    logger.warning(f"STAFF_LOGIN: User found. check_password={is_pword_correct}, is_active={u.is_active}, is_staff={u.is_staff}")
                except User.DoesNotExist:
                     logger.warning(f"STAFF_LOGIN: User '{username}' does not exist in DB.")

            if user is not None and user.is_staff:
                login(request, user)
                request.session.save()  # persist before redirect so cookie is set
                host = _login_redirect_host(request)
                
                # Robust HTTPS forcing: if on prod domain or Cloud Run, ALWAYS use https
                # regardless of DEBUG setting or protocol headers (which can be stripped)
                if 'bb-international.org' in host or '.run.app' in host:
                    scheme = 'https'
                else:
                    scheme = 'https' if request.is_secure() else 'http'
                
                    
                url = f'{scheme}://{host}{next_url}'
                logger.info("STAFF_LOGIN: redirect after login to %s (host=%s)", url, host)
                return redirect(url)
            if user is not None and not user.is_staff:
                return render(request, 'church/staff_login.html', {
                    'error': 'This account does not have staff access.',
                    'next_url': next_url,
                })
        return render(request, 'church/staff_login.html', {
            'error': 'Invalid username or password.',
            'next_url': next_url,
        })

    return render(request, 'church/staff_login.html', {'next_url': next_url})


def csrf_failure_view(request, reason=''):
    """Log CSRF failure (Referer/Origin) then show default 403 page. Helps debug admin login loop."""
    logger.warning(
        "CSRF_FAILURE: reason=%s Referer=%s Origin=%s Host=%s trusted_origins=%s",
        reason,
        request.META.get('HTTP_REFERER', ''),
        request.META.get('HTTP_ORIGIN', ''),
        request.get_host(),
        getattr(settings, 'CSRF_TRUSTED_ORIGINS', []),
    )
    return default_csrf_failure(request, reason)


def health_check_view(request):
    """Health check for load balancers and orchestration (e.g. Cloud Run, K8s)."""
    try:
        connection.ensure_connection()
        return JsonResponse({'status': 'healthy', 'database': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'database': str(e)}, status=503)


# Customize admin site
admin.site.site_header = "Breaking Barriers International"
admin.site.site_title = "Breaking Barriers International"
admin.site.index_title = "Administration"

urlpatterns = [
    path('health/', health_check_view),
    path('staff-login/', staff_login_view),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('church.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/images/logo.png', permanent=False)),
    path('offline/', TemplateView.as_view(template_name='church/offline.html'), name='offline'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]
try:
    import debug_toolbar
    if getattr(settings, 'DEBUG', False):
        urlpatterns.insert(0, path('__debug__/', include('debug_toolbar.urls')))
except ImportError:
    pass

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # In development, serve static files from STATICFILES_DIRS
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
