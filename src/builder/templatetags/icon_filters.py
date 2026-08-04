# from django import template
# from django.utils.safestring import mark_safe
# import json

# register = template.Library()

# @register.simple_tag
# def render_icon(icon_id, default_class="fas fa-heart", icon_customizations=None):
#     """
#     Render an icon with all customizations applied.
    
#     Usage in template:
#     {% load icon_filters %}
#     {% render_icon "1" "fas fa-heart" icon_customizations %}
#     """
#     # Get customizations for this icon if they exist
#     custom_class = default_class
#     custom_style = ""
    
#     if icon_customizations and icon_id in icon_customizations:
#         icon_data = icon_customizations[icon_id]
        
#         # Override class if customized
#         if icon_data.get('icon_class'):
#             custom_class = icon_data['icon_class']
        
#         # Build style string
#         style_parts = []
#         if icon_data.get('color'):
#             style_parts.append(f"color: {icon_data['color']};")
#         if icon_data.get('font_size'):
#             style_parts.append(f"font-size: {icon_data['font_size']};")
        
#         custom_style = ' '.join(style_parts)
    
#     # Build the HTML
#     style_attr = f' style="{custom_style}"' if custom_style else ''
#     html = f'<i class="{custom_class}" data-icon="{icon_id}"{style_attr}></i>'
    
#     return mark_safe(html)


# @register.simple_tag
# def render_icon_with_wrapper(icon_id, wrapper_tag='span', wrapper_class='', default_class="fas fa-heart", icon_customizations=None):
#     """
#     Render an icon inside a wrapper element (useful for buttons, links, etc.)
    
#     Usage:
#     {% render_icon_with_wrapper "1" wrapper_tag="button" wrapper_class="btn btn-primary" %}
#     """
#     icon_html = render_icon(icon_id, default_class, icon_customizations)
    
#     wrapper_class_attr = f' class="{wrapper_class}"' if wrapper_class else ''
#     html = f'<{wrapper_tag}{wrapper_class_attr}>{icon_html}</{wrapper_tag}>'
    
#     return mark_safe(html)


# @register.simple_tag
# def render_icon_grid(icon_ids, columns=4, icon_customizations=None):
#     """
#     Render a grid of icons with their customizations.
    
#     Usage:
#     {% render_icon_grid "1,2,3,4" columns=4 %}
#     """
#     if isinstance(icon_ids, str):
#         icon_ids = [id.strip() for id in icon_ids.split(',')]
    
#     html = '<div class="icon-grid row">'
    
#     for i, icon_id in enumerate(icon_ids):
#         if i % columns == 0:
#             if i > 0:
#                 html += '</div>'
#             html += '<div class="row">'
        
#         html += f'<div class="col-md-{12//columns}">'
#         html += render_icon(icon_id, "fas fa-heart", icon_customizations)
#         html += '</div>'
    
#     html += '</div></div>'
#     return mark_safe(html)


# @register.simple_tag
# def render_icon_script():
#     """
#     Render the JavaScript that applies icon customizations.
#     This should be placed once at the bottom of your template.
    
#     Usage:
#     {% render_icon_script %}
#     """
#     script = """
#     <script>
#     (function() {
#         // This runs once when the page loads
#         document.addEventListener('DOMContentLoaded', function() {
#             // Get all icons with data-icon attribute
#             document.querySelectorAll('[data-icon]').forEach(function(icon) {
#                 const iconId = icon.getAttribute('data-icon');
                
#                 // Get customizations from window object (set by Django)
#                 if (window.ICON_CUSTOMIZATIONS && window.ICON_CUSTOMIZATIONS[iconId]) {
#                     const custom = window.ICON_CUSTOMIZATIONS[iconId];
                    
#                     // Apply custom icon class if present
#                     if (custom.icon_class) {
#                         // Remove existing Font Awesome classes
#                         const classesToRemove = [];
#                         icon.classList.forEach(cls => {
#                             if (cls.startsWith('fa-') || ['fas', 'far', 'fab', 'fal'].includes(cls)) {
#                                 classesToRemove.push(cls);
#                             }
#                         });
#                         classesToRemove.forEach(cls => icon.classList.remove(cls));
                        
#                         // Add new icon classes
#                         custom.icon_class.split(' ').forEach(cls => {
#                             if (cls.trim()) {
#                                 icon.classList.add(cls.trim());
#                             }
#                         });
#                     }
                    
#                     // Apply custom color
#                     if (custom.color) {
#                         icon.style.color = custom.color;
#                     }
                    
#                     // Apply custom font size
#                     if (custom.font_size) {
#                         icon.style.fontSize = custom.font_size;
#                     }
#                 }
#             });
#         });
#     })();
#     </script>
#     """
#     return mark_safe(script)


# @register.simple_tag
# def render_icon_data(icon_customizations):
#     """
#     Render the icon customization data as JSON for JavaScript.
#     This should be placed in the head of your template.
    
#     Usage:
#     {% render_icon_data icon_customizations %}
#     """
#     if not icon_customizations:
#         return '<script>window.ICON_CUSTOMIZATIONS = {};</script>'
    
#     json_data = json.dumps(icon_customizations)
#     return mark_safe(f'<script>window.ICON_CUSTOMIZATIONS = {json_data};</script>')


# @register.inclusion_tag('builder/icon_styles.css')
# def render_icon_styles():
#     """
#     Render default icon styles.
#     This is optional - only if you want consistent icon sizing/spacing.
#     """
#     return {}


# @register.filter
# def icon_class(icon_customizations, icon_id):
#     """Get the custom icon class for an icon ID (filter version)"""
#     if icon_customizations and icon_id in icon_customizations:
#         return icon_customizations[icon_id].get('icon_class', '')
#     return ''


# @register.filter
# def icon_style(icon_customizations, icon_id):
#     """Get the custom style string for an icon ID (filter version)"""
#     if icon_customizations and icon_id in icon_customizations:
#         icon_data = icon_customizations[icon_id]
#         styles = []
#         if icon_data.get('color'):
#             styles.append(f"color: {icon_data['color']};")
#         if icon_data.get('font_size'):
#             styles.append(f"font-size: {icon_data['font_size']};")
#         return ' '.join(styles)
#     return ''








from django import template
from django.utils.safestring import mark_safe
from django.db.models import Q
import json

register = template.Library()

@register.simple_tag(takes_context=True)
def render_icon_data(context, icon_customizations=None):
    """
    Render the icon customization data as JSON for JavaScript.
    This will try multiple sources to get icon data:
    1. Provided icon_customizations parameter
    2. From context['icon_customizations']
    3. From database if page is in context
    
    Usage:
    {% load icon_filters %}
    {% render_icon_data %}  {# Auto-detects from context #}
    {% render_icon_data icon_customizations %}  {# Explicitly pass #}
    """
    
    # Initialize empty dict
    icon_data = {}
    
    # Try 1: Use provided parameter
    if icon_customizations:
        icon_data = icon_customizations
        print(f"🎨 Icon data loaded from parameter: {len(icon_data)} icons")
    
    # Try 2: Use from context
    elif context.get('icon_customizations'):
        icon_data = context['icon_customizations']
        print(f"🎨 Icon data loaded from context: {len(icon_data)} icons")
    
    # Try 3: Load from database if page is in context
    elif context.get('page'):
        try:
            from builder.models import IconCustomization
            
            page = context['page']
            icon_objects = IconCustomization.objects.filter(page=page)
            
            for icon in icon_objects:
                icon_data[icon.element_id] = {
                    'icon_class': icon.icon_class or '',
                    'color': icon.color or '',
                    'font_size': icon.font_size or ''
                }
            
            print(f"🎨 Icon data loaded from database: {len(icon_data)} icons for page {page.subdomain}")
            
            # Cache it in context for future use
            context['icon_customizations'] = icon_data
            
        except Exception as e:
            print(f"❌ Error loading icon customizations from database: {e}")
    
    # Try 4: Check if page is in request.published_page (for public pages)
    elif context.get('request') and hasattr(context['request'], 'published_page'):
        try:
            from builder.models import IconCustomization
            
            page = context['request'].published_page
            icon_objects = IconCustomization.objects.filter(page=page)
            
            for icon in icon_objects:
                icon_data[icon.element_id] = {
                    'icon_class': icon.icon_class or '',
                    'color': icon.color or '',
                    'font_size': icon.font_size or ''
                }
            
            print(f"🎨 Icon data loaded from request.published_page: {len(icon_data)} icons")
            
        except Exception as e:
            print(f"❌ Error loading icon customizations from request: {e}")
    
    # Convert to JSON
    try:
        json_data = json.dumps(icon_data)
    except (TypeError, ValueError) as e:
        print(f"❌ Error serializing icon data to JSON: {e}")
        json_data = '{}'
    
    # Create the script tag
    html = f'<script>window.ICON_CUSTOMIZATIONS = {json_data};</script>'
    
    # Add debug output in development
    if context.get('DEBUG', False):
        debug_info = {
            'source': 'database' if icon_data and not icon_customizations and not context.get('icon_customizations') else 'context',
            'count': len(icon_data),
            'icons': list(icon_data.keys())
        }
        html += f'\n<script>console.log("🎨 Icon data loaded:", {json.dumps(debug_info)});</script>'
    
    return mark_safe(html)


@register.simple_tag
def render_icon(icon_id, default_class="fas fa-heart", icon_customizations=None):
    """
    Render an icon with all customizations applied.
    
    Usage in template:
    {% load icon_filters %}
    {% render_icon "1" "fas fa-heart" icon_customizations %}
    """
    # Get customizations for this icon if they exist
    custom_class = default_class
    custom_style = ""
    
    if icon_customizations and icon_id in icon_customizations:
        icon_data = icon_customizations[icon_id]
        
        # Override class if customized
        if icon_data.get('icon_class'):
            custom_class = icon_data['icon_class']
        
        # Build style string
        style_parts = []
        if icon_data.get('color'):
            style_parts.append(f"color: {icon_data['color']};")
        if icon_data.get('font_size'):
            style_parts.append(f"font-size: {icon_data['font_size']};")
        
        custom_style = ' '.join(style_parts)
    
    # Build the HTML
    style_attr = f' style="{custom_style}"' if custom_style else ''
    html = f'<i class="{custom_class}" data-icon="{icon_id}"{style_attr}></i>'
    
    return mark_safe(html)


@register.simple_tag
def render_icon_with_wrapper(icon_id, wrapper_tag='span', wrapper_class='', default_class="fas fa-heart", icon_customizations=None):
    """
    Render an icon inside a wrapper element (useful for buttons, links, etc.)
    
    Usage:
    {% render_icon_with_wrapper "1" wrapper_tag="button" wrapper_class="btn btn-primary" %}
    """
    icon_html = render_icon(icon_id, default_class, icon_customizations)
    
    wrapper_class_attr = f' class="{wrapper_class}"' if wrapper_class else ''
    html = f'<{wrapper_tag}{wrapper_class_attr}>{icon_html}</{wrapper_tag}>'
    
    return mark_safe(html)


@register.simple_tag
def render_icon_grid(icon_ids, columns=4, icon_customizations=None):
    """
    Render a grid of icons with their customizations.
    
    Usage:
    {% render_icon_grid "1,2,3,4" columns=4 %}
    """
    if isinstance(icon_ids, str):
        icon_ids = [id.strip() for id in icon_ids.split(',')]
    
    html = '<div class="icon-grid row">'
    
    for i, icon_id in enumerate(icon_ids):
        if i % columns == 0:
            if i > 0:
                html += '</div>'
            html += '<div class="row">'
        
        html += f'<div class="col-md-{12//columns}">'
        html += render_icon(icon_id, "fas fa-heart", icon_customizations)
        html += '</div>'
    
    html += '</div></div>'
    return mark_safe(html)


@register.simple_tag(takes_context=True)
def render_icon_script(context):
    """
    Render the JavaScript that applies icon customizations.
    This should be placed once at the bottom of your template.
    
    Usage:
    {% render_icon_script %}
    """
    script = """
    <script>
    (function() {
        // This runs once when the page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Check if window.ICON_CUSTOMIZATIONS exists
            if (!window.ICON_CUSTOMIZATIONS) {
                console.warn('⚠️ window.ICON_CUSTOMIZATIONS not found');
                return;
            }
            
            console.log('🎨 Applying icon customizations:', window.ICON_CUSTOMIZATIONS);
            
            // Get all icons with data-icon attribute
            document.querySelectorAll('[data-icon]').forEach(function(icon) {
                const iconId = icon.getAttribute('data-icon');
                
                // Get customizations for this icon
                if (window.ICON_CUSTOMIZATIONS && window.ICON_CUSTOMIZATIONS[iconId]) {
                    const custom = window.ICON_CUSTOMIZATIONS[iconId];
                    console.log(`🎨 Applying customizations to icon ${iconId}:`, custom);
                    
                    // Apply custom icon class if present
                    if (custom.icon_class) {
                        // Remove existing Font Awesome classes
                        const classesToRemove = [];
                        icon.classList.forEach(cls => {
                            if (cls.startsWith('fa-') || ['fas', 'far', 'fab', 'fal'].includes(cls)) {
                                classesToRemove.push(cls);
                            }
                        });
                        classesToRemove.forEach(cls => icon.classList.remove(cls));
                        
                        // Add new icon classes
                        custom.icon_class.split(' ').forEach(cls => {
                            if (cls.trim()) {
                                icon.classList.add(cls.trim());
                            }
                        });
                    }
                    
                    // Apply custom color
                    if (custom.color) {
                        icon.style.color = custom.color;
                    }
                    
                    // Apply custom font size
                    if (custom.font_size) {
                        icon.style.fontSize = custom.font_size;
                    }
                }
            });
            
            console.log('✅ Icon customizations applied');
        });
    })();
    </script>
    """
    return mark_safe(script)


@register.simple_tag
def render_icon_styles():
    """
    Render default icon styles.
    This is optional - only if you want consistent icon sizing/spacing.
    """
    styles = """
    <style>
    [data-icon] {
        transition: all 0.3s ease;
    }
    </style>
    """
    return mark_safe(styles)


@register.filter
def icon_class(icon_customizations, icon_id):
    """Get the custom icon class for an icon ID (filter version)"""
    if icon_customizations and icon_id in icon_customizations:
        return icon_customizations[icon_id].get('icon_class', '')
    return ''


@register.filter
def icon_style(icon_customizations, icon_id):
    """Get the custom style string for an icon ID (filter version)"""
    if icon_customizations and icon_id in icon_customizations:
        icon_data = icon_customizations[icon_id]
        styles = []
        if icon_data.get('color'):
            styles.append(f"color: {icon_data['color']};")
        if icon_data.get('font_size'):
            styles.append(f"font-size: {icon_data['font_size']};")
        return ' '.join(styles)
    return ''