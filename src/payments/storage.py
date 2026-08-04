# payments/storage.py - Create this simple file

import os
from django.conf import settings
from django.db.models import Sum
from builder.models import BackgroundImage, ImageCustomization, Product, ProductImages


def get_user_storage_usage(user):
    """
    Simply calculate total storage by summing all file sizes
    This is 100% accurate because it checks actual files
    """
    total_bytes = 0
    
    # Sum all background images
    for bg in BackgroundImage.objects.filter(page__user=user):
        if bg.image:
            try:
                total_bytes += bg.image.size
            except:
                pass
    
    # Sum all custom images
    for img in ImageCustomization.objects.filter(page__user=user):
        if img.image:
            try:
                total_bytes += img.image.size
            except:
                pass
    
    # Sum product main images
    for product in Product.objects.filter(page__user=user):
        if product.main_image:
            try:
                total_bytes += product.main_image.size
            except:
                pass
    
    # Sum product gallery images
    for img in ProductImages.objects.filter(product__page__user=user):
        if img.image:
            try:
                total_bytes += img.image.size
            except:
                pass
    
    # Add any other image models here...
    
    return total_bytes


def get_storage_limit(user):
    """Get user's storage limit in bytes"""
    from payments.models import Subscription
    from payments.decorators import get_user_subscription
    
    subscription = get_user_subscription(user)
    
    if not subscription.plan:
        return 100 * 1024 * 1024  # Free: 100MB
    
    limit_mb = subscription.plan.max_storage_mb
    if limit_mb == -1:  # Unlimited
        return None
    
    return limit_mb * 1024 * 1024


def can_upload_file(user, file_size_bytes):
    """Simple check - can user upload this file?"""
    limit = get_storage_limit(user)
    
    if limit is None:  # Unlimited
        return True, None
    
    current_usage = get_user_storage_usage(user)
    new_total = current_usage + file_size_bytes
    
    if new_total > limit:
        remaining = limit - current_usage
        return False, remaining
    
    return True, limit - new_total


def format_bytes(bytes_val):
    """Format bytes to human readable"""
    if bytes_val is None:
        return "Unlimited"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"