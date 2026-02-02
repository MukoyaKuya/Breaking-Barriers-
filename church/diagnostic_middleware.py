import logging
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponseRedirect

logger = logging.getLogger(__name__)


def _referer_origin_matches_trusted(referer, trusted_origins):
    """Return True if referer's scheme+host matches any trusted origin."""
    if not referer or not trusted_origins:
        return False
    try:
        parsed = urlparse(referer)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        return origin in trusted_origins
    except Exception:
        return False


class ProxyRefererFixMiddleware:
    """
    When behind a proxy that strips or rewrites Referer, Django's CSRF check can
    fail on admin login. For POST to /admin/login/, set HTTP_REFERER to the
    current request URL when Referer is missing or doesn't match trusted origins
    (and current host is trusted). Must run before CsrfViewMiddleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method != 'POST' or request.path.rstrip('/') != '/admin/login':
            return self.get_response(request)

        trusted = getattr(settings, 'CSRF_TRUSTED_ORIGINS', []) or []
        current_origin = f"{'https' if request.is_secure() else 'http'}://{request.get_host()}"
        referer = request.META.get('HTTP_REFERER') or ''

        if current_origin not in trusted:
            return self.get_response(request)

        if not referer or not _referer_origin_matches_trusted(referer, trusted):
            request.META['HTTP_REFERER'] = request.build_absolute_uri(request.path)
            logger.info("PROXY_REFERER_FIX: Set HTTP_REFERER for admin login POST (missing or wrong origin)")
        return self.get_response(request)


class StaffLoginRedirectMiddleware:
    """
    Redirect /admin/login/ to /staff-login/?next=/admin/ so staff use the
    custom login that works behind proxies (avoids admin login loop).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path.rstrip('/') == '/admin/login'
            and not request.user.is_authenticated
        ):
            next_url = request.GET.get('next') or '/admin/'
            if not next_url.startswith('/'):
                next_url = '/admin/'
            staff_login_url = f'/staff-login/?next={next_url}'
            return HttpResponseRedirect(request.build_absolute_uri(staff_login_url))
        return self.get_response(request)


class HeaderLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sanitize X-Forwarded-Host if it contains commas (multiple proxies)
        if 'HTTP_X_FORWARDED_HOST' in request.META:
            host = request.META['HTTP_X_FORWARDED_HOST']
            if ',' in host:
                # Take the first host (client-facing)
                clean_host = host.split(',')[0].strip()
                logger.info(f"DIAGNOSTIC: Sanitizing Host header from '{host}' to '{clean_host}'")
                request.META['HTTP_X_FORWARDED_HOST'] = clean_host
            # Keep HTTP_HOST in sync so cookies and redirects use the public host (fixes admin login loop)
            request.META['HTTP_HOST'] = request.META['HTTP_X_FORWARDED_HOST'].strip()
        else:
            # No X-Forwarded-Host: for login paths, use Referer host so cookie/redirect use public host
            path = request.path.rstrip('/')
            if path in ('/admin/login', '/staff-login'):
                referer = request.META.get('HTTP_REFERER') or ''
                if referer:
                    try:
                        parsed = urlparse(referer)
                        netloc = (parsed.netloc or '').strip()
                        allowed = getattr(settings, 'ALLOWED_HOSTS', []) or []
                        if netloc and any(netloc == h or netloc.endswith('.' + h) for h in allowed):
                            request.META['HTTP_HOST'] = netloc
                            logger.info("DIAGNOSTIC: Set HTTP_HOST from Referer for login path (host=%s)", netloc)
                    except Exception:
                        pass

        if request.path.startswith('/admin/'):
            # Log headers for admin requests
            headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_') or k in ['REMOTE_ADDR', 'CONTENT_TYPE', 'CONTENT_LENGTH']}
            logger.info(f"DIAGNOSTIC: Path={request.path}, Method={request.method}")
            logger.info(f"DIAGNOSTIC Headers: {headers}")
            logger.info(f"DIAGNOSTIC Cookies: {request.COOKIES.keys()}")
            
        response = self.get_response(request)
        
        if request.path.startswith('/admin/'):
            logger.info(f"DIAGNOSTIC Response: Status={response.status_code}")
            if 'Location' in response:
                logger.info(f"DIAGNOSTIC Location: {response['Location']}")
            if 'Set-Cookie' in response:
                logger.info(f"DIAGNOSTIC Set-Cookie: Found")
                
        return response
