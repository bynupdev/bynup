from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django import forms
import json

from src import settings

from .forms import (
    BuilderUserRegistrationForm, 
    WebsiteUserRegistrationForm,
    UserLoginForm,
    UserProfileForm,
    UserUpdateForm
)
from .models import UserProfile, WebsiteUser, UserActivity, UserType
from builder.models import PublishedPage

def track_activity(user, activity_type, request=None, metadata=None):
    """Helper function to track user activity"""
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata or {}
    )

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# def builder_register(request):
#     """Registration for website builder users"""
#     if request.user.is_authenticated:
#         return redirect('accounts:dashboard')
    
#     if request.method == 'POST':
#         form = BuilderUserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
            
#             # Track activity
#             track_activity(user, 'builder_register', request)
            
#             # Auto-login after registration with explicit backend
#             backend = 'django.contrib.auth.backends.ModelBackend'
#             login(request, user, backend=backend)
            
#             messages.success(request, 'Account created successfully! Welcome to SiteBuilder.')
#             return redirect('accounts:dashboard')
#     else:
#         form = BuilderUserRegistrationForm()
    
#     return render(request, 'accounts/builder_register.html', {'form': form})

import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from anymail.exceptions import AnymailAPIError

# Set up logging to see errors in Render logs
logger = logging.getLogger(__name__)

def builder_register(request):
    """Registration for website builder users with Resend Email Integration"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = BuilderUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # 1. Track Activity (Your existing function)
            # track_activity(user, 'builder_register', request)
            
            # 2. Prepare Email Content
            context = {
                'user': user,
                'dashboard_url': request.build_absolute_uri('/accounts/dashboard/'),
            }
            
            subject = "Welcome to Bynup | Your account is ready"
            from_email = settings.DEFAULT_FROM_EMAIL # info@bynup.store
            to_email = [user.email]
            
            text_content = render_to_string('emails/welcome_builder.txt', context)
            html_content = render_to_string('emails/welcome_builder.html', context)

            # 3. Construct Multi-Part Email (Text + HTML)
            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            
            # Add Resend Tags for tracking in your Resend Dashboard
            email.tags = ["onboarding", "builder"]

            # 4. Send with Fail-Safe Logic
            try:
                # fail_silently=True ensures registration doesn't crash 
                # if you hit the 100-email daily limit on Resend
                email.send(fail_silently=True) 
            except AnymailAPIError as e:
                logger.error(f"Resend API Error: {e}")
            except Exception as e:
                logger.error(f"Unexpected Email Error: {e}")

            # 5. Finalize Login
            backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend=backend)
            
            messages.success(request, 'Account created successfully! Welcome to Bynup.')
            return redirect('accounts:dashboard')
    else:
        form = BuilderUserRegistrationForm()
    
    return render(request, 'accounts/builder_register.html', {'form': form})



# def website_register(request, subdomain):
#     """Registration for end-users on specific published websites"""
#     # Get the website
#     website = get_object_or_404(PublishedPage, subdomain=subdomain, is_published=True)
    
#     if request.method == 'POST':
#         form = WebsiteUserRegistrationForm(request.POST)
#         form.fields['website_slug'].initial = subdomain
        
#         if form.is_valid():
#             # Check if user already exists with this email
#             email = form.cleaned_data['email']
#             existing_user = None
            
#             try:
#                 existing_user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 pass
            
#             if existing_user:
#                 # User exists, create website membership
#                 user = existing_user
#             else:
#                 # Create new user
#                 user = form.save()
#                 # Set user type to "Website Member"
#                 website_member_type, _ = UserType.objects.get_or_create(
#                     name='Website Member',
#                     defaults={'slug': 'website-member', 'description': 'Users registered on built websites'}
#                 )
#                 user.profile.user_type = website_member_type
#                 user.profile.save()
            
#             # Create website membership
#             website_user, created = WebsiteUser.objects.get_or_create(
#                 user=user,
#                 website=website,
#                 defaults={'is_active': True}
#             )
            
#             # Track activity
#             track_activity(user, 'website_register', request, {'website': website.brand_name})
            
#             # Auto-login with explicit backend
#             backend = 'django.contrib.auth.backends.ModelBackend'
#             login(request, user, backend=backend)
            
#             messages.success(request, f'Successfully registered for {website.brand_name}!')
            
#             # NEW: Redirect to the website's homepage with page=home parameter
#             # Get the correct URL based on domain type
#             if website.is_custom_domain_active and website.custom_domain:
#                 # For custom domains
#                 redirect_url = f"https://{website.custom_domain}/?page=home"
#             else:
#                 # For subdomains
#                 if settings.DEBUG:
#                     redirect_url = f"http://{website.subdomain}.localhost:8000/?page=home"
#                 else:
#                     # Remove any protocol from PRODUCTION_DOMAIN to avoid duplication
#                     production_domain = settings.PRODUCTION_DOMAIN.replace('https://', '').replace('http://', '')
#                     redirect_url = f"https://{website.subdomain}.{production_domain}/?page=home"
                        
#             return redirect(redirect_url)
    
#     else:
#         form = WebsiteUserRegistrationForm()
#         form.fields['website_slug'].initial = subdomain
    
#     context = {
#         'form': form,
#         'website': website,
#     }
#     return render(request, 'accounts/website_register.html', context)


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from anymail.exceptions import AnymailAPIError
import logging
from email.utils import formataddr, parseaddr

logger = logging.getLogger(__name__)

def website_register(request, subdomain):
    """Registration for end-users on specific published websites"""
    website = get_object_or_404(PublishedPage, subdomain=subdomain, is_published=True)
    
    if request.method == 'POST':
        form = WebsiteUserRegistrationForm(request.POST)
        form.fields['website_slug'].initial = subdomain
        
        if form.is_valid():
            email_addr = form.cleaned_data['email']
            existing_user = User.objects.filter(email=email_addr).first()
            
            if existing_user:
                user = existing_user
            else:
                user = form.save()
                website_member_type, _ = UserType.objects.get_or_create(
                    name='Website Member',
                    defaults={'slug': 'website-member'}
                )
                user.profile.user_type = website_member_type
                user.profile.save()
            
            website_user, created = WebsiteUser.objects.get_or_create(
                user=user,
                website=website,
                defaults={'is_active': True}
            )
            
            track_activity(user, 'website_register', request, {'website': website.brand_name})

            # --- DYNAMIC WHITE-LABEL EMAIL LOGIC ---
            # Determine the site URL for the email button
            if website.is_custom_domain_active and website.custom_domain:
                site_url = f"https://{website.custom_domain}"
            else:
                prod_domain = settings.PRODUCTION_DOMAIN.replace('https://', '').replace('http://', '')
                site_url = f"https://{website.subdomain}.{prod_domain}" if not settings.DEBUG else f"http://{website.subdomain}.localhost:8000"

            context = {
                'user': user,
                'website': website,
                'website_url': site_url
            }

            subject = f"Welcome to {website.brand_name}"
            # Custom From: "Brand Name <info@bynup.store>"
            # from_email = f"{website.brand_name} <{settings.DEFAULT_FROM_EMAIL}>"
            # to_email = [user.email]

            text_content = render_to_string('emails/website_welcome.txt', context)
            html_content = render_to_string('emails/website_welcome.html', context)

            # try:
            #     msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            #     msg.attach_alternative(html_content, "text/html")
            #     # Tag it with the subdomain for easy filtering in Resend analytics
            #     msg.tags = ["website_member", subdomain]
            #     msg.send(fail_silently=True)
            # except Exception as e:
            #     logger.error(f"Failed to send white-label welcome email for {subdomain}: {e}")
            # ---------------------------------------
            _, clean_email = parseaddr(settings.DEFAULT_FROM_EMAIL)
            # This creates: "faithy <info@bynup.store>"
            safe_from_name = formataddr((website.brand_name, clean_email))            
            try:
                subject = f"Welcome to {website.brand_name}"
                text_content = render_to_string('emails/website_welcome.txt', context)
                html_content = render_to_string('emails/website_welcome.html', context)

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=safe_from_name, 
                    to=[user.email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.tags = ["website_member", subdomain]
                
                # We set fail_silently=False TEMPORARILY to see the error in Render logs
                msg.send(fail_silently=False) 
                
            except AnymailAPIError as e:
                # This will show up in your 'render log'
                logger.error(f"RESEND API ERROR for {subdomain}: {e.status_code} {e.response.text}")
            except Exception as e:
                logger.error(f"GENERAL EMAIL ERROR for {subdomain}: {str(e)}")

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Successfully registered for {website.brand_name}!')
            
            # Use your existing redirect logic
            if website.is_custom_domain_active and website.custom_domain:
                redirect_url = f"https://{website.custom_domain}/?page=home"
            else:
                production_domain = settings.PRODUCTION_DOMAIN.replace('https://', '').replace('http://', '')
                redirect_url = f"https://{website.subdomain}.{production_domain}/?page=home" if not settings.DEBUG else f"http://{website.subdomain}.localhost:8000/?page=home"
                        
            return redirect(redirect_url)
    
    else:
        form = WebsiteUserRegistrationForm()
        form.fields['website_slug'].initial = subdomain
    
    return render(request, 'accounts/website_register.html', {'form': form, 'website': website})




# accounts/views.py - SIMPLIFIED user_login view
def user_login(request):
    """Simple login that redirects to website homepage"""
    if request.user.is_authenticated:
        # User is already logged in
        
        # METHOD 1: Check if we came from a website (via website_id parameter)
        website_id = request.GET.get('website_id')
        if website_id:
            try:
                website = PublishedPage.objects.get(id=website_id)
                # Redirect to this website's homepage
                return redirect_to_website_homepage(website)
            except PublishedPage.DoesNotExist:
                pass
        
        # METHOD 2: Check referer URL to see if we came from a website
        referer = request.META.get('HTTP_REFERER', '')
        if referer:
            website = find_website_from_url(referer)
            if website:
                return redirect_to_website_homepage(website)
        
        # Default to dashboard
        # return redirect('accounts:dashboard')
        return redirect('template_selection')
    
    # Store where we came from for redirect after login
    next_url = request.GET.get('next', '')
    website_id = request.GET.get('website_id', '')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Track activity
            track_activity(user, 'login', request)
            
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # SIMPLE REDIRECT LOGIC:
            # 1. First check if we have a website_id in POST
            website_id = request.POST.get('website_id') or website_id
            
            if website_id:
                try:
                    website = PublishedPage.objects.get(id=website_id)
                    # Redirect to this website's homepage
                    return redirect_to_website_homepage(website)
                except PublishedPage.DoesNotExist:
                    pass
            
            # 2. Check next URL
            if next_url:
                return redirect(next_url)
            
            # 3. Default to dashboard
            # return redirect('accounts:dashboard')
            return redirect('template_selection')
    
    else:
        form = UserLoginForm()
        
        # Add website_id to form as hidden field if provided
        if website_id:
            form.fields['website_id'] = forms.CharField(
                widget=forms.HiddenInput(),
                required=False,
                initial=website_id
            )
    
    context = {
        'form': form,
        'next_url': next_url,
        'website_id': website_id,
    }
    
    return render(request, 'accounts/login.html', context)



def universal_login(request):
    """Simple universal login that redirects to website homepage using subdomain from POST"""
    subdomain = request.POST.get('website_subdomain')
    website = PublishedPage.objects.get(
                        subdomain=subdomain, 
                        is_published=True
                    )
    # If user is already logged in, redirect appropriately
    if request.user.is_authenticated:
        # Check if we have subdomain in GET or session
        subdomain = request.GET.get('subdomain') or request.session.get('login_subdomain')
        if subdomain:
            try:
                website = PublishedPage.objects.get(subdomain=subdomain, is_published=True)
                return redirect_to_website_homepage(website)
            except PublishedPage.DoesNotExist:
                pass
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Set session expiry
            if not form.cleaned_data.get('remember_me', False):
                request.session.set_expiry(0)
            
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # CRITICAL: Get subdomain from POST data
            subdomain = request.POST.get('website_subdomain')
            
            if subdomain:
                try:
                    # Find the website by subdomain
                    website = PublishedPage.objects.get(
                        subdomain=subdomain, 
                        is_published=True
                    )
                    # Redirect to this website's homepage
                    return redirect_to_website_homepage(website)
                except PublishedPage.DoesNotExist:
                    # Website not found, redirect to dashboard
                    pass
            
            # If no subdomain or website not found, go to dashboard
            return redirect('dashboard')
    
    else:
        # GET request - initialize form
        form = UserLoginForm()
        
        # Get subdomain from GET parameter (for pre-filling)
        subdomain = request.GET.get('subdomain')
        if subdomain:
            # Store in form context for template
            request.session['login_subdomain'] = subdomain
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'subdomain': subdomain,
    })

# Add helper function to find website from URL
def find_website_from_url(url):
    """Extract website from any URL"""
    from urllib.parse import urlparse
    from django.conf import settings
    
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        if not hostname:
            return None
        
        # Try custom domain
        try:
            website = PublishedPage.objects.get(
                custom_domain=hostname,
                is_custom_domain_active=True,
                is_published=True
            )
            return website
        except PublishedPage.DoesNotExist:
            pass
        
        # Try subdomain (development)
        if settings.DEBUG and ('localhost' in hostname or '127.0.0.1' in hostname):
            parts = hostname.split('.')
            if len(parts) > 1 and parts[0] not in ['localhost', '127', 'www']:
                subdomain = parts[0]
                try:
                    website = PublishedPage.objects.get(
                        subdomain=subdomain,
                        is_published=True
                    )
                    return website
                except PublishedPage.DoesNotExist:
                    pass
        
        # Try subdomain (production)
        production_domain = getattr(settings, 'PRODUCTION_DOMAIN', None)
        if production_domain and hostname.endswith(f'.{production_domain}'):
            subdomain = hostname.replace(f'.{production_domain}', '')
            try:
                website = PublishedPage.objects.get(
                    subdomain=subdomain,
                    is_published=True
                )
                return website
            except PublishedPage.DoesNotExist:
                pass
    
    except Exception as e:
        print(f"Error finding website from URL: {e}")
    
    return None



def redirect_to_website_homepage(website):
    """Helper function to redirect to the website's homepage with proper domain"""
    from django.conf import settings
    
    if website.is_custom_domain_active and website.custom_domain:
        # For custom domains
        return redirect(f"https://{website.custom_domain}/")
    else:
        # For subdomains
        if settings.DEBUG:
            return redirect(f"http://{website.subdomain}.localhost:8000/")
        else:
            # Remove protocol from PRODUCTION_DOMAIN to avoid duplication
            production_domain = settings.PRODUCTION_DOMAIN.replace('https://', '').replace('http://', '')
            return redirect(f"https://{website.subdomain}.{production_domain}/")






def user_logout(request):
    """Logout user and redirect to current website's homepage"""
    current_website = None
    
    # Get current website before logout
    if hasattr(request, 'published_page') and request.published_page:
        current_website = request.published_page
    else:
        # Try to get from referer or session
        referer = request.META.get('HTTP_REFERER', '')
        if referer:
            # Extract subdomain from referer
            from urllib.parse import urlparse
            parsed = urlparse(referer)
            hostname = parsed.hostname
            
            if hostname:
                # Check if it's a custom domain first
                try:
                    current_website = PublishedPage.objects.get(
                        custom_domain=hostname,
                        is_custom_domain_active=True,
                        is_published=True
                    )
                except PublishedPage.DoesNotExist:
                    # Try subdomain
                    try:
                        if settings.DEBUG and 'localhost' in hostname:
                            parts = hostname.split('.')
                            if len(parts) > 1 and parts[0] != 'localhost':
                                subdomain = parts[0]
                                current_website = PublishedPage.objects.get(
                                    subdomain=subdomain,
                                    is_published=True
                                )
                        else:
                            # Production environment
                            # Remove protocol from PRODUCTION_DOMAIN for comparison
                            production_domain = settings.PRODUCTION_DOMAIN.replace('https://', '').replace('http://', '')
                            
                            # Check if hostname ends with production domain
                            if hostname.endswith(production_domain):
                                subdomain = hostname.replace(f'.{production_domain}', '')
                                if subdomain and subdomain not in ['www', 'admin', 'api', 'static']:
                                    current_website = PublishedPage.objects.get(
                                        subdomain=subdomain,
                                        is_published=True
                                    )
                    except PublishedPage.DoesNotExist:
                        pass
    
    if request.user.is_authenticated:
        # Track activity
        track_activity(request.user, 'logout', request, {
            'website': current_website.brand_name if current_website else None
        })
        
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
    
    # Redirect to appropriate homepage
    if current_website:
        return redirect_to_website_homepage(current_website)
    else:
        return redirect('template_selection')  # Your main site homepage

@login_required
def dashboard(request):
    """User dashboard showing different content based on user type"""
    user = request.user
    profile = user.profile
    
    # Get website memberships
    website_memberships = WebsiteUser.objects.filter(user=user, is_active=True).select_related('website')
    
    # Get built websites if user is a website owner
    built_websites = []
    if profile.user_type.name == 'Website Owner':
        built_websites = PublishedPage.objects.filter(user=user).order_by('-created_at')
    
    # Recent activity
    recent_activity = UserActivity.objects.filter(user=user).order_by('-timestamp')[:10]
    
    context = {
        'profile': profile,
        'website_memberships': website_memberships,
        'built_websites': built_websites,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile(request):
    """User profile management"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # Track activity
            track_activity(request.user, 'profile_update', request)
            
            messages.success(request, 'Your profile has been updated!')
            return ('reprofile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def website_memberships(request):
    """Show all website memberships for the user"""
    memberships = WebsiteUser.objects.filter(user=request.user, is_active=True).select_related('website')
    
    context = {
        'memberships': memberships,
    }
    return render(request, 'accounts/website_memberships.html', context)

# API Views for AJAX functionality
@login_required
@csrf_exempt
def update_profile_picture(request):
    """Update profile picture via AJAX"""
    if request.method == 'POST' and request.FILES.get('avatar'):
        profile = request.user.profile
        profile.avatar = request.FILES['avatar']
        profile.save()
        
        track_activity(request.user, 'avatar_update', request)
        
        return JsonResponse({
            'success': True,
            'avatar_url': profile.avatar.url if profile.avatar else ''
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# Public website user registration endpoint
@csrf_exempt
def public_website_register(request, subdomain):
    """Public API endpoint for website user registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            website = get_object_or_404(PublishedPage, subdomain=subdomain, is_published=True)
            
            # Create or get user
            user, created = User.objects.get_or_create(
                email=data.get('email'),
                defaults={
                    'username': data.get('email'),  # Use email as username
                    'first_name': data.get('first_name', ''),
                    'last_name': data.get('last_name', ''),
                }
            )
            
            if created:
                user.set_password(data.get('password'))
                user.save()
                
                # Set user type
                website_member_type, _ = UserType.objects.get_or_create(
                    name='Website Member',
                    defaults={'slug': 'website-member', 'description': 'Users registered on built websites'}
                )
                user.profile.user_type = website_member_type
                user.profile.save()
            
            # Create website membership
            website_user, created = WebsiteUser.objects.get_or_create(
                user=user,
                website=website,
                defaults={'is_active': True}
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Registration successful',
                'user_id': user.id
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import Http404

def detect_registration_context(request):
    """
    Detect whether user is registering on builder or a built website
    Returns: ('builder', None) or ('website', website_object)
    """
    # Check if we're on a built website via subdomain
    if hasattr(request, 'published_page') and request.published_page:
        return ('website', request.published_page)
    
    # Check if we're on a built website via custom domain
    if hasattr(request, 'domain_type') and request.domain_type == 'custom':
        if hasattr(request, 'published_page') and request.published_page:
            return ('website', request.published_page)
    
    # Check URL pattern for website registration
    if 'website-register' in request.path:
        try:
            subdomain = request.path.split('/website-register/')[1].split('/')[0]
            website = PublishedPage.objects.get(subdomain=subdomain, is_published=True)
            return ('website', website)
        except (IndexError, PublishedPage.DoesNotExist):
            pass
    
    # Default to builder context
    return ('builder', None)

def universal_register(request):
    """
    Universal registration view that detects context and shows appropriate form
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    context_type, website = detect_registration_context(request)
    
    if context_type == 'website' and website:
        # Show website-specific registration
        return website_register(request, website.subdomain)
    else:
        # Show builder registration
        return builder_register(request)
    



def home_view(request):
    return HttpResponse("Welcome Home")



def detect_registration_context(request):
    """
    Detect whether user is registering on builder or a built website
    Returns: ('builder', None) or ('website', website_object)
    """
    # Method 1: Check if we're on a built website via middleware
    if hasattr(request, 'published_page') and request.published_page:
        return ('website', request.published_page)
    
    # Method 2: Check URL pattern for website registration/login
    path = request.path
    
    # Check for website registration
    if 'website-register' in path:
        try:
            # Extract subdomain from URL like /website-register/mystore/
            parts = path.split('/website-register/')
            if len(parts) > 1:
                subdomain = parts[1].strip('/').split('/')[0]
                website = PublishedPage.objects.get(subdomain=subdomain, is_published=True)
                return ('website', website)
        except (IndexError, PublishedPage.DoesNotExist):
            pass
    
    # Check for universal login with website_id parameter
    website_id = request.GET.get('website_id')
    if website_id:
        try:
            website = PublishedPage.objects.get(id=website_id, is_published=True)
            return ('website', website)
        except PublishedPage.DoesNotExist:
            pass
    
    # Check referer for website context
    referer = request.META.get('HTTP_REFERER', '')
    if referer:
        from urllib.parse import urlparse
        parsed = urlparse(referer)
        hostname = parsed.hostname
        
        if hostname:
            # Check if referer is from a website
            try:
                # Try custom domain
                website = PublishedPage.objects.get(
                    custom_domain=hostname,
                    is_custom_domain_active=True
                )
                return ('website', website)
            except PublishedPage.DoesNotExist:
                # Try subdomain
                if settings.DEBUG and 'localhost' in hostname:
                    parts = hostname.split('.')
                    if len(parts) > 1 and parts[0] != 'localhost':
                        subdomain = parts[0]
                        website = PublishedPage.objects.get(subdomain=subdomain, is_published=True)
                        return ('website', website)
    
    # Default to builder context
    return ('builder', None)