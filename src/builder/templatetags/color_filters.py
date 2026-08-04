# builder/templatetags/color_filters.py

from django import template
from django.template.defaultfilters import safe
import json

register = template.Library()

@register.simple_tag(takes_context=True)
def generate_color_variables(context):
    """
    Generate CSS :root variables from page's active palette
    Format:
    :root {
        --primary-color: #4361ee;
        --secondary-color: #3a0ca3;
        --accent-color: #f72585;
    }
    """
    page = context.get('page')
    
    if page and hasattr(page, 'active_palette_colors') and page.active_palette_colors:
        colors = page.active_palette_colors
        css_lines = [":root {"]
        
        for var_name, color_data in colors.items():
            # Handle both string and dict formats
            if isinstance(color_data, dict):
                hex_value = color_data.get('hex', '')
            else:
                hex_value = color_data
            
            if hex_value:
                css_lines.append(f"    --{var_name}: {hex_value};")
        
        css_lines.append("}")
        return safe("\n".join(css_lines))
    
    return ""


@register.simple_tag
def get_color_value(page, var_name, default=''):
    """Get a specific color value from page's active palette"""
    if page and hasattr(page, 'active_palette_colors') and page.active_palette_colors:
        color_data = page.active_palette_colors.get(var_name)
        if color_data:
            if isinstance(color_data, dict):
                return color_data.get('hex', default)
            return color_data
    return default


@register.filter
def css_color_var(var_name):
    """Convert variable name to CSS var() function"""
    return f'var(--{var_name})'


@register.simple_tag
def palette_json(page):
    """Output active palette as JSON for JavaScript"""
    if page and hasattr(page, 'active_palette_colors') and page.active_palette_colors:
        colors_dict = {}
        for var_name, color_data in page.active_palette_colors.items():
            if isinstance(color_data, dict):
                colors_dict[var_name] = color_data.get('hex', '')
            else:
                colors_dict[var_name] = color_data
        
        return safe(json.dumps({
            'id': page.active_palette.id if page.active_palette else None,
            'name': page.active_palette.name if page.active_palette else None,
            'colors': colors_dict
        }))
    return safe('null')