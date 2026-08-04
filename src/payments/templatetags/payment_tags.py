from django import template
from ..models import PaymentGateway

register = template.Library()

@register.filter
def status_class(status):
    """Get CSS class for status"""
    classes = {
        'pending': 'warning',
        'pending_pod': 'warning',
        'processing': 'info',
        'ready_for_delivery': 'primary',
        'out_for_delivery': 'primary',
        'completed': 'success',
        'cancelled': 'danger',
        'refunded': 'secondary',
        'failed': 'dark',
    }
    return classes.get(status, 'secondary')

@register.simple_tag
def get_pod_gateway(page):
    """Get POD gateway for a page"""
    return page.payment_gateways.filter(
        gateway_type='pay_on_delivery',
        is_active=True
    ).first()


# @register.filter
# def div(value, arg):
#     return value / arg





@register.filter
def div(value, arg):
    try:
        if arg == 0:
            return "Cannot divide by zero"  # or return 0 or None based on your requirement
        return value / arg
    except (TypeError, ValueError):
        return None  # Handle cases where value or arg are not numbers
