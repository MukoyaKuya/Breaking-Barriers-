"""
Cache decorators that safely handle user authentication.
Fixes Django issue #15855: @cache_page with @vary_on_headers('Cookie') can serve
cached content to wrong users because decorators run before session middleware.

Solution: Only cache for anonymous users, never cache authenticated user requests.
"""
from functools import wraps
from django.views.decorators.cache import cache_page


def cache_page_for_anonymous(timeout):
    """
    Safely cache page only for anonymous (non-authenticated) users.
    
    This decorator fixes the security issue where @cache_page with 
    @vary_on_headers('Cookie') can serve cached content to wrong users.
    
    Authenticated users (including staff/admin) always get fresh content.
    Anonymous users get cached content for better performance.
    
    Args:
        timeout: Cache timeout in seconds
        
    Usage:
        @cache_page_for_anonymous(60 * 15)  # 15 minutes
        def my_view(request):
            ...
    """
    def decorator(view_func):
        # Apply cache_page decorator to the view function
        cached_view = cache_page(timeout)(view_func)
        
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # CRITICAL: Check authentication AFTER middleware has processed the request
            # This ensures request.user is properly set by AuthenticationMiddleware
            if request.user.is_authenticated:
                # Never cache authenticated users - always return fresh content
                # This prevents security issues where one user's cached page
                # could be served to another authenticated user
                return view_func(request, *args, **kwargs)
            
            # Safe to cache for anonymous users - they all see the same public content
            return cached_view(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator
