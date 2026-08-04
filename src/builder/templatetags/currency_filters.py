from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def currency(amount, page=None):
    """Format amount as currency using page settings"""
    if amount is None:
        return ''
    
    if page and hasattr(page, 'format_price'):
        return page.format_price(amount)
    
    # Fallback to default formatting
    try:
        return f"${float(amount):.2f}"
    except (ValueError, TypeError):
        return str(amount)

@register.filter
def currency_code(page):
    """Get currency code from page"""
    if page and hasattr(page, 'currency_code'):
        return page.currency_code
    return 'USD'

@register.simple_tag(takes_context=True)
def price_with_currency(context, amount):
    """Template tag for consistent price formatting"""
    page = context.get('page')
    if page and hasattr(page, 'format_price'):
        return page.format_price(amount)
    try:
        return f"${float(amount):.2f}"
    except (ValueError, TypeError):
        return str(amount)

@register.simple_tag
def currency_js_config(page):
    """Generate JavaScript config for currency formatting"""
    if not page:
        return '{}'
    
    config = {
        'code': page.currency_code,
        'symbol': page.currency_symbol,
        'position': page.currency_position,
        'thousandSeparator': page.thousand_separator,
        'decimalSeparator': page.decimal_separator,
        'decimalPlaces': page.decimal_places,
    }
    return mark_safe(json.dumps(config))

@register.filter
def payment_currency(amount, gateway='stripe'):
    """Convert amount to payment gateway currency format"""
    try:
        # Most payment gateways expect amounts in smallest unit (cents for USD)
        # and don't accept decimal separators
        return int(float(amount) * 100)
    except (ValueError, TypeError):
        return 0