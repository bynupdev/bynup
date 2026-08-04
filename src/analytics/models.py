from django.db import models
from builder.models import *
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import re


# Create your models here.
# Add to models.py
class WebsiteAnalytics(models.Model):
    """Main analytics model for each published page"""
    page = models.OneToOneField(PublishedPage, on_delete=models.CASCADE, related_name='analytics')
    total_visits = models.PositiveBigIntegerField(default=0)
    unique_visitors = models.PositiveBigIntegerField(default=0)
    bounce_rate = models.FloatField(default=0.0)  # Percentage
    avg_session_duration = models.DurationField(default=timedelta(0))
    conversion_rate = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Website Analytics"

    def __str__(self):
        return f"Analytics - {self.page.brand_name}"
    


class PageView(models.Model):
    """Individual page view tracking"""
    analytics = models.ForeignKey(WebsiteAnalytics, on_delete=models.CASCADE, related_name='page_views')
    session_id = models.CharField(max_length=100)
    visitor_id = models.CharField(max_length=100)
    page_url = models.CharField(max_length=500)
    page_name = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    referrer = models.CharField(max_length=500, blank=True, null=True)
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet'),
        ('mobile', 'Mobile')
    ])
    browser = models.CharField(max_length=100)
    operating_system = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True, blank=True)
    is_bounce = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['session_id']),
            models.Index(fields=['visitor_id']),
        ]

    def get_traffic_source_type(self):
        """Determine traffic source type from referrer"""
        referrer = self.referrer or ''
        
        if not referrer:
            return 'direct'
        elif 'google' in referrer or 'bing' in referrer or 'yahoo' in referrer:
            return 'organic'
        elif any(social in referrer for social in ['facebook', 'twitter', 'instagram', 'linkedin']):
            return 'social'
        else:
            return 'referral'

class Event(models.Model):
    """Custom events tracking"""
    analytics = models.ForeignKey(WebsiteAnalytics, on_delete=models.CASCADE, related_name='events')
    session_id = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50, choices=[
        ('page_view', 'Page View'),
        ('click', 'Click'),
        ('form_submit', 'Form Submit'),
        ('purchase', 'Purchase'),
        ('download', 'Download'),
        ('scroll', 'Scroll'),
        ('video_play', 'Video Play'),
        ('social_share', 'Social Share')
    ])
    event_name = models.CharField(max_length=200)
    element_id = models.CharField(max_length=100, blank=True, null=True)
    element_class = models.CharField(max_length=200, blank=True, null=True)
    element_text = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class Conversion(models.Model):
    """Conversion tracking for goals"""
    analytics = models.ForeignKey(WebsiteAnalytics, on_delete=models.CASCADE, related_name='conversions')
    session_id = models.CharField(max_length=100)
    conversion_type = models.CharField(max_length=50, choices=[
        ('purchase', 'Purchase'),
        ('form_submit', 'Form Submission'),
        ('signup', 'Sign Up'),
        ('contact', 'Contact'),
        ('download', 'Download'),
        ('newsletter', 'Newsletter Signup')
    ])
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class TrafficSource(models.Model):
    """Traffic source breakdown"""
    analytics = models.ForeignKey(WebsiteAnalytics, on_delete=models.CASCADE, related_name='traffic_sources')
    date = models.DateField()
    source_type = models.CharField(max_length=20, choices=[
        ('direct', 'Direct'),
        ('organic', 'Organic Search'),
        ('social', 'Social Media'),
        ('referral', 'Referral'),
        ('email', 'Email'),
        ('paid', 'Paid Search')
    ])
    source_name = models.CharField(max_length=200)  # e.g., 'google', 'facebook'
    visits = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['analytics', 'date', 'source_type', 'source_name']

class GeographicData(models.Model):
    """Geographic visitor data"""
    analytics = models.ForeignKey(WebsiteAnalytics, on_delete=models.CASCADE, related_name='geographic_data')
    date = models.DateField()
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    visits = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['analytics', 'date', 'country', 'region', 'city']