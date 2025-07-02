from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

class TemporaryLoginRequiredMixin(LoginRequiredMixin):
    """
    A temporary replacement for LoginRequiredMixin that uses a local URL
    while allauth is disabled.
    """
    login_url = '/'  # Temporarily point to home page instead of allauth login


class BreadcrumbMixin:
    """
    Mixin to add breadcrumbs to a view.
    
    Usage:
    1. Add this mixin to your view
    2. Define breadcrumbs in get_breadcrumbs method or breadcrumbs attribute
    
    Example:
        class MyView(BreadcrumbMixin, TemplateView):
            breadcrumbs = [
                {'title': 'Home', 'url': '/'},
                {'title': 'My Page', 'url': None},  # Last item has no URL
            ]
    
    Or dynamically:
        def get_breadcrumbs(self):
            return [
                {'title': 'Home', 'url': reverse('home')},
                {'title': self.object.name, 'url': None},
            ]
    """
    breadcrumbs = []
    
    def get_breadcrumbs(self):
        """
        Return the breadcrumbs for this view.
        Override this method to provide dynamic breadcrumbs.
        """
        return self.breadcrumbs
    
    def dispatch(self, request, *args, **kwargs):
        # Set breadcrumbs on the request object
        request.breadcrumbs = self.get_breadcrumbs()
        return super().dispatch(request, *args, **kwargs)
