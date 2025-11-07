"""
Middleware for the R1D3 system.
"""
from django.core.cache import cache
from django.db import connection
from django.shortcuts import redirect
from django.urls import reverse

class ClearCacheMiddleware:
    """
    Middleware to clear Django's cache and reset database connections on every request.
    This ensures that we always get fresh data for the milestone display.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Clear Django's cache
        cache.clear()
        
        # Reset database connections to ensure fresh queries
        connection.close()
        
        # Process the request
        response = self.get_response(request)
        
        return response

class BreadcrumbsMiddleware:
    """
    Middleware to add breadcrumbs support to requests.
    This allows views to set breadcrumbs by adding to request.breadcrumbs.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Initialize empty breadcrumbs list
        request.breadcrumbs = []
        
        # Process the request
        response = self.get_response(request)
        
        return response


class ProfileSelectionMiddleware:
    """
    Middleware to ensure users have selected their profile (team member name)
    before accessing the system.
    """
    
    # URLs that don't require profile selection
    EXEMPT_URLS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/admin/',
        '/profile/select/',
        '/profile/clear/',
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if this URL is exempt
            path = request.path
            is_exempt = any(path.startswith(url) for url in self.EXEMPT_URLS)
            
            # If not exempt and no profile selected, redirect to profile selection
            if not is_exempt and 'current_user_name' not in request.session:
                return redirect(f"{reverse('core:select_profile')}?next={path}")
        
        # Process the request
        response = self.get_response(request)
        
        return response
