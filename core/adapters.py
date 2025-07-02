"""
Custom adapters for django-allauth to modify default behavior.
"""
from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError


class NoNewUsersAccountAdapter(DefaultAccountAdapter):
    """
    Adapter that disables user registration.
    Only admin users can create new accounts through the admin interface.
    """
    def is_open_for_signup(self, request):
        """
        Disable signup for all users.
        """
        return False
    
    def clean_email(self, email):
        """
        Validate email - this will still be used for login.
        """
        return super().clean_email(email)
    
    def save_user(self, request, user, form, commit=True):
        """
        This method is called when saving a new user, but since signup is disabled,
        it should never be called except by admin.
        """
        raise ValidationError("User registration is disabled. Please contact an administrator.")
