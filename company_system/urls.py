"""
URL configuration for company_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('strategy/', include('strategy.urls')),
    path('projects/', include('projects.urls')),
    path('games/', include('projects.game_urls', namespace='games')),
    # The following paths may not be implemented yet
    # path('resources/', include('resources.urls')),
    # path('docs/', include('docs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
