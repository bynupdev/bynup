from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class MultiUserBackend(ModelBackend):
    """
    Custom authentication backend that handles both builder users
    and website-specific users with proper isolation
    """
    def authenticate(self, request, username=None, password=None, website_id=None, **kwargs):
        try:
            # Try to authenticate as builder user first
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
            
            if user.check_password(password):
                # If website_id is provided, check if user is registered for that website
                if website_id:
                    try:
                        from .models import WebsiteUser
                        website_user = WebsiteUser.objects.get(
                            user=user, 
                            website_id=website_id,
                            is_active=True
                        )
                        return user
                    except WebsiteUser.DoesNotExist:
                        return None  # User not registered for this website
                
                # No website_id - authenticating as builder user
                return user
                
        except User.DoesNotExist:
            return None
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None