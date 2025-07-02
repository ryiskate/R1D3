"""
Middleware for the R1D3 system.
"""

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
