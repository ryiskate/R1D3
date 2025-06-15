from django.contrib.auth.mixins import LoginRequiredMixin

class TemporaryLoginRequiredMixin(LoginRequiredMixin):
    """
    A temporary replacement for LoginRequiredMixin that uses a local URL
    while allauth is disabled.
    """
    login_url = '/'  # Temporarily point to home page instead of allauth login
