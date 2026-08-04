# Create a new file: builder/templatetags/website_auth_tags.py
from django import template
from django.urls import reverse
from accounts.helpers import get_website_homepage_url
from accounts.models import WebsiteUser

register = template.Library()

@register.simple_tag(takes_context=True)
def website_login_url(context):
    """Generate login URL that redirects to website homepage"""
    request = context.get('request')
    if hasattr(request, 'published_page') and request.published_page:
        page = request.published_page
        # Include next parameter to redirect to homepage
        from django.urls import reverse
        login_url = reverse('accounts:universal_login')
        homepage_url = get_website_homepage_url(page)  # Use helper function
        return f"{login_url}?website_id={page.id}&next={homepage_url}"
    return reverse('accounts:universal_login')

# def website_login_url(context):
#     """Generate login URL for the current website"""
#     request = context.get('request')
#     if hasattr(request, 'published_page') and request.published_page:
#         page = request.published_page
#         return reverse('accounts:universal_login') + f'?website_id={page.id}'
#     return reverse('accounts:universal_login')

@register.simple_tag(takes_context=True)
def website_register_url(context):
    """Generate register URL that stays on website"""
    request = context.get('request')
    if hasattr(request, 'published_page') and request.published_page:
        page = request.published_page
        return reverse('accounts:website_register', args=[page.subdomain])
    return reverse('accounts:universal_register')

# def website_register_url(context):
#     """Generate register URL for the current website"""
#     request = context.get('request')
#     if hasattr(request, 'published_page') and request.published_page:
#         page = request.published_page
#         return reverse('accounts:website_register', args=[page.subdomain])
#     return reverse('accounts:universal_register')

@register.simple_tag(takes_context=True)
def is_website_member(context):
    """Check if current user is a member of this website"""
    request = context.get('request')
    if not request.user.is_authenticated:
        return False
    
    if hasattr(request, 'published_page') and request.published_page:
        page = request.published_page
        return WebsiteUser.objects.filter(
            user=request.user,
            website=page,
            is_active=True
        ).exists()
    
    return False

@register.simple_tag(takes_context=True)
def get_website_user_data(context):
    """Get website-specific user data"""
    request = context.get('request')
    if not request.user.is_authenticated:
        return {}
    
    if hasattr(request, 'published_page') and request.published_page:
        page = request.published_page
        try:
            website_user = WebsiteUser.objects.get(
                user=request.user,
                website=page,
                is_active=True
            )
            return {
                'is_member': True,
                'role': website_user.role,
                'joined_date': website_user.registered_at,
                'is_verified': website_user.is_verified,
            }
        except WebsiteUser.DoesNotExist:
            return {'is_member': False}
    
    return {'is_member': False}