# builder/decorators.py
from functools import wraps
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser

def debug_authentication(view_func):
    """Decorator to debug authentication issues"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        print(f"\n{'='*60}")
        print(f"🔐 DEBUG AUTHENTICATION - View: {view_func}")
        print(f"{'='*60}")
        
        # Method 1: Check current user
        print(f"1. request.user: {request.user}")
        # print(f"   Class: {request.user.class.name}")
        print(f"   Is AnonymousUser: {isinstance(request.user, AnonymousUser)}")
        print(f"   Is authenticated: {request.user.is_authenticated}")
        print(f"   User ID: {request.user.id}")
        
        # Method 2: Check session
        print(f"\n2. Session check:")
        print(f"   Session key: {request.session.session_key}")
        print(f"   Auth user ID in session: {request.session.get('_auth_user_id')}")
        
        # Method 3: Try to get user from session
        if request.session.get('_auth_user_id'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_id = request.session.get('_auth_user_id')
                user_from_session = User.objects.get(id=user_id)
                print(f"   ✓ User found from session ID: {user_from_session.username}")
                
                # Compare with request.user
                if request.user != user_from_session:
                    print(f"   ⚠️ MISMATCH: request.user != user from session")
                    print(f"      request.user: {request.user} (id: {request.user.id})")
                    print(f"      session user: {user_from_session} (id: {user_from_session.id})")
            except Exception as e:
                print(f"   ✗ Error getting user from session: {e}")
        
        # Method 4: Check if AuthenticationMiddleware has run
        print(f"\n3. Authentication check:")
        # This is a hack to check if auth middleware ran
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            print(f"   ✓ AuthenticationMiddleware appears to have run")
        else:
            print(f"   ⚠️ AuthenticationMiddleware may not have run or user is anonymous")
        
        print(f"{'='*60}\n")
        
        # Call the original view
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view