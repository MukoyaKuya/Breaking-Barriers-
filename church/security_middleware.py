class SecurityHeadersMiddleware:
    """
    Middleware to add additional security headers that are not yet 
    supported natively by Django's SecurityMiddleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Permissions-Policy
        # Disable unused browser features for better privacy and security
        permissions_policy = (
            "camera=(), "
            "microphone=(), "
            "geolocation=(), "
            "interest-cohort=()"
        )
        response['Permissions-Policy'] = permissions_policy
        
        # Content-Security-Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://storage.googleapis.com https://bb-international.org https://www.bb-international.org https://i.ytimg.com https://img.youtube.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "frame-src 'self' https://www.youtube.com https://youtube.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "base-uri 'self';"
        )
        response['Content-Security-Policy'] = csp
        
        # Cross-Origin-Embedder-Policy (Optional, depends on requirements)
        # response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        
        return response
