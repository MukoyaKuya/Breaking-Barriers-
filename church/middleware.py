"""Middleware for analytics (page view tracking)."""
from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip as ipware_get_client_ip


def anonymize_ip(ip):
    """Anonymize the given IP address by masking the last octet (IPv4) or last 80 bits (IPv6)."""
    if not ip:
        return None
    if '.' in ip:
        # IPv4: Zero out the last octet
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
    elif ':' in ip:
        # IPv6: Keep only the first 48 bits (3 segments) to follow best practices
        parts = ip.split(':')
        if len(parts) >= 3:
            return f"{parts[0]}:{parts[1]}:{parts[2]}::"
    return ip


def get_client_ip(request):
    """Return the client IP for the request (proxy-aware via django-ipware)."""
    client_ip, _ = ipware_get_client_ip(request)
    return anonymize_ip(client_ip)


class PageViewMiddleware(MiddlewareMixin):
    """Log a page view for each request (for visits-per-month and unique-visitor analytics)."""
    # Paths we don't log (admin, static, API, analytics)
    SKIP_PREFIXES = ('/office/', '/static/', '/media/', '/analytics/', '/__debug__/', '/health/', '/favicon.ico')
    
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
            import threading
            from django.db import connections
            
            def log_page_view_async(p, ip):
                try:
                    from .models import PageView
                    PageView.objects.create(path=p, ip_address=ip)
                except Exception:
                    pass
                finally:
                    for conn in connections.all():
                        conn.close()
            
            threading.Thread(
                target=log_page_view_async, 
                args=(path[:500], get_client_ip(request)),
                daemon=True
            ).start()
        except Exception:
            pass  # Don't break the request if DB/logging fails
        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Global lockdown middleware. If MN.is_active is True, all non-admin/non-static 
    requests are diverted to the maintenance page.
    """
    SKIP_PATHS = ('/office/', '/static/', '/media/', '/staff-login/', '/favicon.ico')

    def process_request(self, request):
        # Allow admin and static files
        if any(request.path.startswith(p) for p in self.SKIP_PATHS):
            return None

        try:
            from .models import MN
            mn_settings = MN.load()
            if mn_settings.is_active:
                # If we are already on the home page, home_view will handle it, 
                # but for all other pages, we force the maintenance template.
                from django.shortcuts import render
                if request.path != '/':
                    return render(request, 'church/maintenance.html', {'mn': mn_settings})
        except Exception:
            pass
        return None
