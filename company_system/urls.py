"""
URL configuration for company_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import the specific views we need for direct URL patterns
from projects.debug_views import DebugAllTasksView, TemplateDebugView, DebugSidebarView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('strategy/', include('strategy.urls')),
    path('projects/', include('projects.urls')),
    path('games/', include('projects.game_urls')),
    # Debug URL patterns
    path('debug-tasks/', DebugAllTasksView.as_view(), name='debug_all_tasks'),
    path('template-debug/', TemplateDebugView.as_view(), name='template_debug'),
    path('debug-sidebar/', DebugSidebarView.as_view(), name='debug_sidebar'),
    # Department URLs
    path('education/', include('education.urls', namespace='education')),
    path('social-media/', include('social_media.urls', namespace='social_media')),
    path('arcade/', include('arcade.urls', namespace='arcade')),
    path('theme-park/', include('theme_park.urls', namespace='theme_park')),
    # The following paths may not be implemented yet
    # path('resources/', include('resources.urls')),
    # path('docs/', include('docs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
