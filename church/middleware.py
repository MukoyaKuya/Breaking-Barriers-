"""Middleware for analytics (page view tracking)."""
from django.utils.deprecation import MiddlewareMixin


class PageViewMiddleware(MiddlewareMixin):
    """Log a page view for each request (for visits-per-month analytics)."""
    # Paths we don't log (admin, static, API, analytics)
    SKIP_PREFIXES = ('/admin/', '/static/', '/media/', '/analytics/', '/__debug__/', '/health/', '/favicon.ico')

    def process_response(self, request, response):
        if response.status_code != 200:
            return response
        path = request.path
        if any(path.startswith(p) for p in self.SKIP_PREFIXES):
            return response
        try:
            from .models import PageView
            PageView.objects.create(path=path[:500])
        except Exception:
            pass  # Don't break the request if DB/logging fails
        return response
