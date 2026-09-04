from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value

@register.filter
def subtract(value, arg):
    """Subtract the argument from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def add_float(value, arg):
    """Add the argument to the value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value