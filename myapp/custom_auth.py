from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class Backend(ModelBackend):
    """
    Custom authentication backend.
    This extends Django's default ModelBackend.
    You can add custom authentication logic here.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Custom authentication logic.
        Currently uses default behavior but can be extended.
        """
        return super().authenticate(request, username=username, password=password, **kwargs)
    
    def get_user(self, user_id):
        """
        Retrieve a user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
