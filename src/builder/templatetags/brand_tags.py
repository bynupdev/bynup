# builder/templatetags/brand_tags.py

from django import template

register = template.Library()

# ✅ Tag version
@register.simple_tag
def brand_name(page):
    """Get brand name from page object."""
    if page and hasattr(page, 'brand_name') and page.brand_name:
        return page.brand_name
    return 'My Store'

# ✅ Tag that takes context
@register.simple_tag(takes_context=True)
def brand_name_from_context(context):
    """Get brand name from context."""
    page = context.get('page')
    if page and hasattr(page, 'brand_name') and page.brand_name:
        return page.brand_name
    
    if context.get('brand_name'):
        return context.get('brand_name')
    
    return 'My Store'

# ✅ Filter version
@register.filter
def get_brand_name(page):
    """Get brand name from page object as filter."""
    if page and hasattr(page, 'brand_name') and page.brand_name:
        return page.brand_name
    return 'My Store'