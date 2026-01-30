"""Middleware for analytics (page view tracking)."""
from django.utils.deprecation import MiddlewareMixin


def get_client_ip(request):
    """Return the client IP for the request (handles X-Forwarded-For behind proxies)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        # First IP is the client when behind a proxy
        return xff.split(',')[0].strip() or request.META.get('REMOTE_ADDR', '') or None
    return request.META.get('REMOTE_ADDR') or None


class PageViewMiddleware(MiddlewareMixin):
    """Log a page view for each request (for visits-per-month and unique-visitor analytics)."""
    # Paths we don't log (admin, static, API, analytics)
    SKIP_PREFIXES = ('/admin/', '/static/', '/media/', '/analytics/', '/__debug__/', '/health/', '/favicon.ico')
    
    # User agents we don't log (bots, health checks)
    SKIP_USER_AGENTS = (
        'GoogleHC',
        'Googlebot',
        'bingbot',
        'AhrefsBot',
        'Baiduspider',
        'yandex',
        'python-requests',
        'SemrushBot',
        'DotBot',
        'MJ12bot',
    )

    def process_response(self, request, response):
        if response.status_code != 200:
            return response
            
        path = request.path
        if any(path.startswith(p) for p in self.SKIP_PREFIXES):
            return response
            
        # Filter out bots
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if any(bot in user_agent for bot in self.SKIP_USER_AGENTS):
            return response
            
        try:
            from .models import PageView
            PageView.objects.create(path=path[:500], ip_address=get_client_ip(request))
        except Exception:
            pass  # Don't break the request if DB/logging fails
        return response
