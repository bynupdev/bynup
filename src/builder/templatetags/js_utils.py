from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def js_bool(value):
    """Convert Python boolean to JavaScript boolean"""
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    return 'null'

@register.filter
def safe_json(value):
    """Convert value to JSON with proper JavaScript boolean handling"""
    def convert_bools(obj):
        if isinstance(obj, bool):
            return obj  # Let json.dumps handle it properly
        if isinstance(obj, dict):
            return {k: convert_bools(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [convert_bools(v) for v in obj]
        return obj
    
    converted = convert_bools(value)
    return mark_safe(json.dumps(converted))


