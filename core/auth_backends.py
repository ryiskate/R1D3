from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class TemporaryAuthBackend(ModelBackend):
    """
    A temporary authentication backend to use while allauth is disabled.
    This backend allows Django's built-in authentication to work without allauth.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
