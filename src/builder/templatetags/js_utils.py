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
    """
    Convert value to JSON that is safe to embed inside an inline
    <script> block.

    The critical part is escaping '</script' so that any component HTML
    containing '</script>' cannot prematurely close the surrounding
    <script> tag in editor.html. Also escapes '<' after '</' generically
    for safety and escapes HTML comment openers '<!--'.
    """
    if value is None:
        return mark_safe('null')

    def convert_bools(obj):
        if isinstance(obj, bool):
            return obj
        if isinstance(obj, dict):
            return {k: convert_bools(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [convert_bools(v) for v in obj]
        return obj

    try:
        s = json.dumps(convert_bools(value), default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return mark_safe('null')

    # Prevent premature </script> closing — case-insensitive, tolerant of
    # whitespace or attributes right after 'script'.
    s = s.replace('</script', '<\\/script')
    s = s.replace('</SCRIPT', '<\\/SCRIPT')
    s = s.replace('</Script', '<\\/Script')

    # Also neutralise HTML comment openers which can confuse the parser.
    s = s.replace('<!--', '<\\!--')

    return mark_safe(s)