# builder/templatetags/product_filters.py

from django import template

register = template.Library()

@register.filter
def sum_quantity(variants):
    """Sum the quantity of all variants in a queryset"""
    if not variants:
        return 0
    return sum(v.quantity for v in variants)