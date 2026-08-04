# middleware/fix_auth_middleware.py
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

class FixAuthenticationMiddleware:
    """Middleware to fix authentication issues - should be LAST in MIDDLEWARE list"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # This runs AFTER all other middleware
        
        # Check if user is still anonymous but session says otherwise
        if isinstance(request.user, AnonymousUser) and request.session.get('_auth_user_id'):
            User = get_user_model()
            try:
                user_id = request.session.get('_auth_user_id')
                if user_id:
                    user = User.objects.get(id=user_id)
                    # Force set the user
                    request.user = user
                    print(f"🔧 FixAuthenticationMiddleware: Fixed user to {user.username}")
            except Exception as e:
                print(f"🔧 FixAuthenticationMiddleware: Error fixing user: {e}")
        
        response = self.get_response(request)
        return response

# Add to settings.py as the LAST middleware:
# 'middleware.fix_auth_middleware.FixAuthenticationMiddleware',