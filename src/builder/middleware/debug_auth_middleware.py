class AuthDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log authentication info for every request
        if 'builder' in request.path or 'review' in request.path:
            print("\n" + "="*60)
            print("🔐 AUTHENTICATION DEBUG")
            print("="*60)
            print(f"Path: {request.path}")
            print(f"User: {request.user}")
            print(f"User ID: {request.user.id}")
            print(f"Username: {request.user.username}")
            print(f"Email: {request.user.email}")
            print(f"Is Authenticated: {request.user.is_authenticated}")
            print(f"Is Superuser: {request.user.is_superuser}")
            print(f"Is Staff: {request.user.is_staff}")
            print(f"Session Key: {request.session.session_key}")
            print(f"Session authenticated: {request.session.get('_auth_user_id')}")
            print("="*60 + "\n")
        
        response = self.get_response(request)
        return response

# Add to settings.py MIDDLEWARE after SessionMiddleware:
# 'middleware.debug_auth_middleware.AuthDebugMiddleware',