"""
Middleware for the R1D3 system.
"""
from django.core.cache import cache
from django.db import connection

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
