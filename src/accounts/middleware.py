from django.shortcuts import redirect
from django.urls import reverse

class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Handle auth redirects for authenticated users
        if request.user.is_authenticated and request.path in [
            # reverse('accounts:universal_login'),
            reverse('accounts:universal_register'),
            reverse('accounts:builder_register'),
        ]:
            return redirect('dashboard')
        
        return response