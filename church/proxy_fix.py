import logging
from django.conf import settings
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ProxyRefererFixMiddleware(MiddlewareMixin):
    """
    Fix Referer for login POSTs so CSRF passes behind proxies.
    Applies to /admin/login/ and /staff-login/ (custom form used when admin
    login is redirected).
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Check POST to admin login or staff login (custom form used behind proxy)
        if request.method != 'POST':
            return None
        path = request.path.rstrip('/')
        if path not in ('/admin/login', '/staff-login'):
            return None
            trusted_origins = settings.CSRF_TRUSTED_ORIGINS
            try:
                # Check if correct Host is trusted
                request_host = request.get_host()
                is_host_trusted = any(o.endswith(request_host) for o in trusted_origins)
                
                if is_host_trusted:
                    referer = request.META.get('HTTP_REFERER')
                    should_fix = False
                    
                    if not referer:
                        should_fix = True
                        logger.info(f"PROXY_REFERER_FIX: Missing Referer for host {request_host}")
                    else:
                        # Check if Referer matches a trusted origin
                        parsed_ref = urlparse(referer)
                        ref_origin = f"{parsed_ref.scheme}://{parsed_ref.netloc}"
                        if ref_origin not in trusted_origins:
                            should_fix = True
                            logger.info(f"PROXY_REFERER_FIX: Mismatched Referer {referer} for host {request_host}")

                    if should_fix:
                        # Reconstruct the expected Referer (current page)
                        new_referer = request.build_absolute_uri()
                        request.META['HTTP_REFERER'] = new_referer
                        logger.info(f"PROXY_REFERER_FIX: Set HTTP_REFERER to {new_referer}")
            except Exception as e:
                logger.error(f"PROXY_REFERER_FIX: Error checking/fixing referer: {e}")
        return None

def csrf_failure(request, reason=""):
    """
    Custom CSRF failure view to log diagnostics.
    """
    ua = request.META.get('HTTP_USER_AGENT', 'unknown')
    referer = request.META.get('HTTP_REFERER', 'missing')
    origin = request.META.get('HTTP_ORIGIN', 'missing')
    host = request.get_host()
    
    logger.error(
        f"CSRF_FAILURE: reason='{reason}' "
        f"Referer='{referer}' "
        f"Origin='{origin}' "
        f"Host='{host}' "
        f"trusted_origins={settings.CSRF_TRUSTED_ORIGINS} "
        f"UA='{ua}'"
    )
    
    # Return the standard 403 Forbidden page provided by Django
    return render(request, "403_csrf.html", {
        'title': '403 Forbidden',
        'main': 'CSRF verification failed',
        'reason': reason
    }, status=403)
