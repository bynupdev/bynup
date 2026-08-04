from django import template

register = template.Library()

@register.filter
def get_platform_field(platform, field_name):
    """
    Get platform-specific field information
    """
    from builder.models import SocialMedia
    fields = SocialMedia.PLATFORM_FIELDS.get(platform, {})
    return fields.get(field_name, '')

@register.filter
def format_social_handle(handle, platform):
    """
    Format a social media handle for display
    """
    if not handle:
        return ''
    
    if platform == 'whatsapp':
        # Format phone number
        if handle.startswith('+'):
            return handle
        return f'+{handle}'
    
    elif platform in ['instagram', 'twitter', 'tiktok', 'snapchat', 'threads']:
        return f'@{handle.lstrip("@")}'
    
    elif platform == 'youtube':
        if handle.startswith('UC'):
            return f'Channel ID: {handle[:8]}...'
        return handle
    
    return handle