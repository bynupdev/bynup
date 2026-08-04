

from django.urls import path
from . import views

urlpatterns = [
    path('analytics/<str:subdomain>/', views.analytics_dashboard, name='analytics_dashboard'),
    # path('analytics/<str:subdomain>/api/', views.analytics_api, name='analytics_api'),
    path('api/<str:subdomain>/', views.analytics_api, name='analytics_api'),
    path('track-event/<str:subdomain>/', views.track_event, name='track_event'),
    path('track-conversion/<str:subdomain>/', views.track_conversion, name='track_conversion'),
]