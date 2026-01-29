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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from django.http import JsonResponse
from django.db import connection


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
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('church.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/images/logo.png', permanent=False)),
    path('offline/', TemplateView.as_view(template_name='church/offline.html'), name='offline'),
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
