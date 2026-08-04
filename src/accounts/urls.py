from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    # path('register/', views.builder_register, name='builder_register'),
    # path('website-register/<str:subdomain>/', views.website_register, name='website_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # # Specific routes (force context)
    # path('builder/register/', views.builder_register, name='builder_register'),
    # path('website/register/<str:subdomain>/', views.website_register, name='website_register'),
    
    # # Dashboard & Profile
    # path('dashboard/', views.dashboard, name='dashboard'),
    # path('profile/', views.profile, name='profile'),
    # path('memberships/', views.website_memberships, name='memberships'),
    
    # # API endpoints
    # path('api/update-avatar/', views.update_profile_picture, name='update_avatar'),
    # path('api/website-register/<str:subdomain>/', views.public_website_register, name='api_website_register'),

    path('register/', views.universal_register, name='universal_register'),
    path('login/', views.universal_login, name='universal_login'),
    path('home/', views.home_view, name='home'),

   
    # Specific routes (force context)
    path('builder/register/', views.builder_register, name='builder_register'),
    path('website/register/<str:subdomain>/', views.website_register, name='website_register'),
    
    # Common routes
    path('user_login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    # path('dashboard/', views.dashboard, name='account_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('memberships/', views.website_memberships, name='memberships'),
    
    # API endpoints
    path('api/update-avatar/', views.update_profile_picture, name='update_avatar'),

    # path('reset_password/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name="reset_password"),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name="password_reset_done"),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name="password_reset_confirm"),
    # path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name="password_reset_complete"),
    # Your other URLs...
    
    # Password Reset URLs - Using Django's built-in views with custom templates
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt'
         ), 
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]

# Update main urls.py to include accounts
# In your main urls.py, add:
# path('accounts/', include('accounts.urls')),