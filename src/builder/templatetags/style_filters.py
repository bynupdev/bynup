
# # builder/templatetags/style_filters.py

# from django import template
# from django.template.defaultfilters import safe
# import json

# register = template.Library()

# @register.filter
# def get_style(styles, key):
#     """Get style value by key with fallback"""
#     if isinstance(styles, dict):
#         return styles.get(key, '')
#     return ''

# @register.simple_tag
# def generate_section_styles(style_customizations, start=1, end=1000):
#     """
#     Generate CSS for multiple sections dynamically including hover effects
#     Output format:
#     #section-123 { ... }
#     #section-123:hover { ... }
#     """
#     css_rules = []
    
#     for section_id in range(start, end + 1):
#         section_id_str = str(section_id)
#         section_styles = style_customizations.get(section_id_str, {})
        
#         # Skip if no styles at all
#         if not section_styles:
#             continue
            
#         # Filter out non-style keys and empty values for normal state
#         normal_styles = {}
#         excluded_keys = ['hover', 'hover_animation', 'hover_settings']
        
#         for key, value in section_styles.items():
#             if key in excluded_keys:
#                 continue
#             if value and isinstance(value, str) and value.strip():
#                 normal_styles[key] = value
        
#         # Generate normal state CSS if there are styles
#         if normal_styles:
#             normal_css = f"#section-{section_id} {{\n"
#             for key, value in normal_styles.items():
#                 css_property = key.replace('_', '-')
#                 normal_css += f"    {css_property}: {value};\n"
#             normal_css += "}\n"
#             css_rules.append(normal_css)
        
#         # Generate hover state CSS if hover is enabled
#         hover_enabled = False
#         hover_styles = {}
        
#         # Check different possible hover data structures
#         if 'hover' in section_styles and isinstance(section_styles['hover'], dict):
#             hover_data = section_styles['hover']
#             hover_enabled = hover_data.get('enabled', False)
#             if hover_enabled and 'styles' in hover_data:
#                 hover_styles = hover_data['styles']
        
#         # Alternative structure (as seen in your data)
#         elif 'hover_animation' in section_styles:
#             hover_enabled = True
#             animation = section_styles.get('hover_animation')
#             settings = section_styles.get('hover_settings', {})
            
#             # Build hover styles based on animation type
#             hover_styles = build_hover_styles_from_animation(animation, settings, section_styles)
        
#         # Generate hover CSS if enabled
#         if hover_enabled and hover_styles:
#             hover_css = f"#section-{section_id}:hover {{\n"
            
#             # Add transition if specified
#             transition = hover_styles.get('transition', '0.3s')
#             hover_css += f"    transition: all {transition} ease;\n"
            
#             # Add transform if present
#             if hover_styles.get('transform'):
#                 hover_css += f"    transform: {hover_styles['transform']};\n"
            
#             # Add background color if present
#             if hover_styles.get('background_color'):
#                 hover_css += f"    background-color: {hover_styles['background_color']};\n"
            
#             # Add text color if present
#             if hover_styles.get('text_color'):
#                 hover_css += f"    color: {hover_styles['text_color']};\n"
            
#             # Add border if present
#             if hover_styles.get('border'):
#                 hover_css += f"    border: {hover_styles['border']};\n"
            
#             # Add box shadow if present
#             if hover_styles.get('box_shadow'):
#                 hover_css += f"    box-shadow: {hover_styles['box_shadow']};\n"
            
#             # Add animation if present
#             if hover_styles.get('animation'):
#                 animation_value = hover_styles['animation']
#                 # For infinite animations like pulse, bounce, shake
#                 if animation_value in ['pulse', 'bounce', 'shake', 'glow']:
#                     hover_css += f"    animation: {animation_value} 1s infinite;\n"
#                 else:
#                     hover_css += f"    animation: {animation_value} 0.3s ease;\n"
            
#             hover_css += "}\n"
#             css_rules.append(hover_css)
    
#     return safe('\n'.join(css_rules))

# def build_hover_styles_from_animation(animation, settings, base_styles):
#     """
#     Build hover styles dictionary from animation type and settings
#     """
#     hover_styles = {
#         'transition': settings.get('transition', '0.3s'),
#         'animation': animation
#     }
    
#     # Handle different animation types
#     if animation == 'scale':
#         scale_x = settings.get('scaleX', '1.1')
#         scale_y = settings.get('scaleY', '1.1')
#         hover_styles['transform'] = f'scale({scale_x}, {scale_y})'
    
#     elif animation == 'scale-down':
#         scale_x = settings.get('scaleX', '0.9')
#         scale_y = settings.get('scaleY', '0.9')
#         hover_styles['transform'] = f'scale({scale_x}, {scale_y})'
    
#     elif animation in ['lift', 'slide-up']:
#         translate_y = settings.get('translateY', '-5')
#         hover_styles['transform'] = f'translateY({translate_y}px)'
    
#     elif animation == 'rotate':
#         rotate = settings.get('rotate', '5')
#         hover_styles['transform'] = f'rotate({rotate}deg)'
    
#     elif animation == 'skew':
#         hover_styles['transform'] = 'skew(5deg, 0deg)'
    
#     elif animation == 'color-shift':
#         hover_styles['background_color'] = settings.get('bgColor', '#4361ee')
#         hover_styles['text_color'] = settings.get('textColor', '#ffffff')
    
#     elif animation == 'border':
#         border_width = settings.get('borderWidth', '2px')
#         border_style = settings.get('borderStyle', 'solid')
#         border_color = settings.get('borderColor', '#4361ee')
#         hover_styles['border'] = f'{border_width} {border_style} {border_color}'
    
#     elif animation in ['shadow', 'glow']:
#         shadow_color = settings.get('shadowColor', '#4361ee')
#         shadow_opacity = settings.get('shadowOpacity', '0.3')
#         # Convert hex to rgba if needed
#         if shadow_color.startswith('#'):
#             r = int(shadow_color[1:3], 16)
#             g = int(shadow_color[3:5], 16)
#             b = int(shadow_color[5:7], 16)
#             shadow_color = f'rgba({r}, {g}, {b}, {shadow_opacity})'
#         hover_styles['box_shadow'] = f'0 0 20px {shadow_color}'
    
#     return hover_styles

# @register.simple_tag
# def generate_background_images(background_images, start=1, end=1000):
#     """Generate background image styles dynamically"""
#     css_rules = []
    
#     for section_id in range(start, end + 1):
#         section_id_str = str(section_id)
#         bg_data = background_images.get(section_id_str)
        
#         if bg_data:
#             image_url = None
#             if isinstance(bg_data, dict):
#                 image_url = bg_data.get('image_url')
#             elif isinstance(bg_data, str):
#                 image_url = bg_data
            
#             if image_url and image_url != 'none' and image_url.strip():
#                 css_rule = f"""
# #section-{section_id} {{
#     background-image: url('{image_url}') !important;
#     background-size: cover !important;
#     background-position: center !important;
#     background-repeat: no-repeat !important;
# }}
# """.strip()
#                 css_rules.append(css_rule)
    
#     return safe('\n'.join(css_rules))

# @register.simple_tag
# def generate_component_styles(component_customizations):
#     """Generate CSS for component customizations"""
#     css_rules = []
    
#     if not component_customizations:
#         return ''
    
#     for customization in component_customizations:
#         if not isinstance(customization, dict):
#             continue
            
#         instance_id = customization.get('instance_id')
#         customizations = customization.get('customizations', {})
        
#         if not instance_id or not customizations:
#             continue
        
#         # Handle component-level styles
#         if 'styles' in customizations:
#             for element_id, styles in customizations['styles'].items():
#                 if not styles:
#                     continue
                
#                 # Normal state
#                 normal_styles = {k: v for k, v in styles.items() 
#                                if k not in ['hover', 'hover_animation', 'hover_settings'] 
#                                and v and isinstance(v, str) and v.strip()}
                
#                 if normal_styles:
#                     selector = f'[data-instance-id="{instance_id}"] [data-section="{element_id}"]'
#                     css = f"{selector} {{\n"
#                     for key, value in normal_styles.items():
#                         css_property = key.replace('_', '-')
#                         css += f"    {css_property}: {value};\n"
#                     css += "}\n"
#                     css_rules.append(css)
                
#                 # Hover state
#                 hover_enabled = False
#                 hover_data = {}
                
#                 if 'hover' in styles and isinstance(styles['hover'], dict):
#                     hover_data = styles['hover']
#                     hover_enabled = hover_data.get('enabled', False)
                
#                 if hover_enabled and 'styles' in hover_data:
#                     hover_styles = hover_data['styles']
#                     selector = f'[data-instance-id="{instance_id}"] [data-section="{element_id}"]:hover'
#                     css = f"{selector} {{\n"
                    
#                     transition = hover_styles.get('transition', '0.3s')
#                     css += f"    transition: all {transition} ease;\n"
                    
#                     if hover_styles.get('transform'):
#                         css += f"    transform: {hover_styles['transform']};\n"
#                     if hover_styles.get('background_color'):
#                         css += f"    background-color: {hover_styles['background_color']};\n"
#                     if hover_styles.get('text_color'):
#                         css += f"    color: {hover_styles['text_color']};\n"
#                     if hover_styles.get('border'):
#                         css += f"    border: {hover_styles['border']};\n"
#                     if hover_styles.get('box_shadow'):
#                         css += f"    box-shadow: {hover_styles['box_shadow']};\n"
#                     if hover_styles.get('animation'):
#                         animation = hover_styles['animation']
#                         if animation in ['pulse', 'bounce', 'shake', 'glow']:
#                             css += f"    animation: {animation} 1s infinite;\n"
#                         else:
#                             css += f"    animation: {animation} 0.3s ease;\n"
                    
#                     css += "}\n"
#                     css_rules.append(css)
    
#     return safe('\n'.join(css_rules))

# @register.simple_tag
# def generate_hover_keyframes():
#     """Generate keyframes for hover animations"""
#     keyframes = """
# @keyframes pulse {
#     0% { transform: scale(1); }
#     50% { transform: scale(1.05); }
#     100% { transform: scale(1); }
# }

# @keyframes bounce {
#     0%, 100% { transform: translateY(0); }
#     50% { transform: translateY(-10px); }
# }

# @keyframes shake {
#     0%, 100% { transform: translateX(0); }
#     25% { transform: translateX(-5px); }
#     75% { transform: translateX(5px); }
# }

# @keyframes glow {
#     0% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0.7); }
#     50% { box-shadow: 0 0 20px 5px rgba(67, 97, 238, 0.5); }
#     100% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0); }
# }
# """
#     return safe(keyframes)






# builder/templatetags/style_filters.py

from django import template
from django.template.defaultfilters import safe
import json

register = template.Library()

@register.filter
def get_style(styles, key):
    """Get style value by key with fallback"""
    if isinstance(styles, dict):
        return styles.get(key, '')
    return ''

@register.simple_tag
def generate_section_styles(style_customizations, start=1, end=1000):
    """
    Generate CSS for multiple sections dynamically including hover effects,
    dimensions, and opacity
    Output format:
    #section-123 { ... }
    #section-123:hover { ... }
    """
    css_rules = []
    
    for section_id in range(start, end + 1):
        section_id_str = str(section_id)
        section_styles = style_customizations.get(section_id_str, {})
        
        # Skip if no styles at all
        if not section_styles:
            continue
            
        # Filter out non-style keys and empty values for normal state
        normal_styles = {}
        excluded_keys = ['hover', 'hover_animation', 'hover_settings', 'text_opacity_children']
        
        for key, value in section_styles.items():
            if key in excluded_keys:
                continue
            if value and isinstance(value, str) and value.strip():
                normal_styles[key] = value
        
        # Generate normal state CSS if there are styles
        if normal_styles:
            normal_css = f"#section-{section_id} {{\n"
            for key, value in normal_styles.items():
                css_property = key.replace('_', '-')
                normal_css += f"    {css_property}: {value};\n"
            normal_css += "}\n"
            css_rules.append(normal_css)
        
        # ===== HANDLE TEXT OPACITY (NEW) =====
        text_opacity = section_styles.get('text_opacity')
        text_opacity_children = section_styles.get('text_opacity_children', False)
        
        if text_opacity is not None:
            opacity_value = float(text_opacity) if isinstance(text_opacity, str) else text_opacity
            
            if opacity_value < 1.0:
                if text_opacity_children:
                    # Apply to all text elements inside the section
                    text_opacity_css = f"""
#section-{section_id} .editable-text,
#section-{section_id} p,
#section-{section_id} h1,
#section-{section_id} h2,
#section-{section_id} h3,
#section-{section_id} h4,
#section-{section_id} h5,
#section-{section_id} h6,
#section-{section_id} span,
#section-{section_id} a,
#section-{section_id} label,
#section-{section_id} li,
#section-{section_id} [data-text],
#section-{section_id} [class*="text"],
#section-{section_id} [class*="heading"],
#section-{section_id} [class*="title"] {{
    color: rgba(var(--text-color-rgb, 0, 0, 0), {opacity_value}) !important;
}}
"""
                    css_rules.append(text_opacity_css.strip())
                else:
                    # Apply only to direct text content of the section
                    text_opacity_css = f"""
#section-{section_id} {{
    color: rgba(var(--text-color-rgb, 0, 0, 0), {opacity_value}) !important;
}}
#section-{section_id} > .editable-text,
#section-{section_id} > p,
#section-{section_id} > h1,
#section-{section_id} > h2,
#section-{section_id} > h3,
#section-{section_id} > h4,
#section-{section_id} > h5,
#section-{section_id} > h6,
#section-{section_id} > span {{
    color: rgba(var(--text-color-rgb, 0, 0, 0), {opacity_value}) !important;
}}
"""
                    css_rules.append(text_opacity_css.strip())
        
        # Generate hover state CSS if hover is enabled
        hover_enabled = False
        hover_styles = {}
        
        # Check different possible hover data structures
        if 'hover' in section_styles and isinstance(section_styles['hover'], dict):
            hover_data = section_styles['hover']
            hover_enabled = hover_data.get('enabled', False)
            if hover_enabled and 'styles' in hover_data:
                hover_styles = hover_data['styles']
        
        # Alternative structure (as seen in your data)
        elif 'hover_animation' in section_styles:
            hover_enabled = True
            animation = section_styles.get('hover_animation')
            settings = section_styles.get('hover_settings', {})
            
            # Build hover styles based on animation type
            hover_styles = build_hover_styles_from_animation(animation, settings, section_styles)
        
        # Generate hover CSS if enabled
        if hover_enabled and hover_styles:
            hover_css = f"#section-{section_id}:hover {{\n"
            
            # Add transition if specified
            transition = hover_styles.get('transition', '0.3s')
            hover_css += f"    transition: all {transition} ease;\n"
            
            # Add transform if present
            if hover_styles.get('transform'):
                hover_css += f"    transform: {hover_styles['transform']};\n"
            
            # Add background color if present
            if hover_styles.get('background_color'):
                hover_css += f"    background-color: {hover_styles['background_color']};\n"
            
            # Add text color if present
            if hover_styles.get('text_color'):
                hover_css += f"    color: {hover_styles['text_color']};\n"
            
            # Add border if present
            if hover_styles.get('border'):
                hover_css += f"    border: {hover_styles['border']};\n"
            
            # Add box shadow if present
            if hover_styles.get('box_shadow'):
                hover_css += f"    box-shadow: {hover_styles['box_shadow']};\n"
            
            # Add animation if present
            if hover_styles.get('animation'):
                animation_value = hover_styles['animation']
                # For infinite animations like pulse, bounce, shake
                if animation_value in ['pulse', 'bounce', 'shake', 'glow']:
                    hover_css += f"    animation: {animation_value} 1s infinite;\n"
                else:
                    hover_css += f"    animation: {animation_value} 0.3s ease;\n"
            
            hover_css += "}\n"
            css_rules.append(hover_css)
    
    return safe('\n'.join(css_rules))


def build_hover_styles_from_animation(animation, settings, base_styles):
    """
    Build hover styles dictionary from animation type and settings
    """
    hover_styles = {
        'transition': settings.get('transition', '0.3s'),
        'animation': animation
    }
    
    # Handle different animation types
    if animation == 'scale':
        scale_x = settings.get('scaleX', '1.1')
        scale_y = settings.get('scaleY', '1.1')
        hover_styles['transform'] = f'scale({scale_x}, {scale_y})'
    
    elif animation == 'scale-down':
        scale_x = settings.get('scaleX', '0.9')
        scale_y = settings.get('scaleY', '0.9')
        hover_styles['transform'] = f'scale({scale_x}, {scale_y})'
    
    elif animation in ['lift', 'slide-up']:
        translate_y = settings.get('translateY', '-5')
        hover_styles['transform'] = f'translateY({translate_y}px)'
    
    elif animation == 'rotate':
        rotate = settings.get('rotate', '5')
        hover_styles['transform'] = f'rotate({rotate}deg)'
    
    elif animation == 'skew':
        hover_styles['transform'] = 'skew(5deg, 0deg)'
    
    elif animation == 'color-shift':
        hover_styles['background_color'] = settings.get('bgColor', '#4361ee')
        hover_styles['text_color'] = settings.get('textColor', '#ffffff')
    
    elif animation == 'border':
        border_width = settings.get('borderWidth', '2px')
        border_style = settings.get('borderStyle', 'solid')
        border_color = settings.get('borderColor', '#4361ee')
        hover_styles['border'] = f'{border_width} {border_style} {border_color}'
    
    elif animation in ['shadow', 'glow']:
        shadow_color = settings.get('shadowColor', '#4361ee')
        shadow_opacity = settings.get('shadowOpacity', '0.3')
        # Convert hex to rgba if needed
        if shadow_color.startswith('#'):
            r = int(shadow_color[1:3], 16)
            g = int(shadow_color[3:5], 16)
            b = int(shadow_color[5:7], 16)
            shadow_color = f'rgba({r}, {g}, {b}, {shadow_opacity})'
        hover_styles['box_shadow'] = f'0 0 20px {shadow_color}'
    
    return hover_styles


@register.simple_tag
def generate_background_images(background_images, start=1, end=1000):
    """Generate background image styles dynamically"""
    css_rules = []
    
    for section_id in range(start, end + 1):
        section_id_str = str(section_id)
        bg_data = background_images.get(section_id_str)
        
        if bg_data:
            image_url = None
            if isinstance(bg_data, dict):
                image_url = bg_data.get('image_url')
            elif isinstance(bg_data, str):
                image_url = bg_data
            
            if image_url and image_url != 'none' and image_url.strip():
                css_rule = f"""
#section-{section_id} {{
    background-image: url('{image_url}') !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
}}
""".strip()
                css_rules.append(css_rule)
    
    return safe('\n'.join(css_rules))


@register.simple_tag
def generate_component_styles(component_customizations):
    """Generate CSS for component customizations including dimensions and opacity"""
    css_rules = []
    
    if not component_customizations:
        return ''
    
    for customization in component_customizations:
        if not isinstance(customization, dict):
            continue
            
        instance_id = customization.get('instance_id')
        customizations = customization.get('customizations', {})
        
        if not instance_id or not customizations:
            continue
        
        # Handle component-level styles
        if 'styles' in customizations:
            for element_id, styles in customizations['styles'].items():
                if not styles:
                    continue
                
                # Normal state - include all dimension and opacity properties
                normal_styles = {}
                excluded_keys = ['hover', 'hover_animation', 'hover_settings', 'text_opacity_children']
                
                for k, v in styles.items():
                    if k in excluded_keys:
                        continue
                    if v and isinstance(v, str) and v.strip():
                        normal_styles[k] = v
                
                if normal_styles:
                    selector = f'[data-instance-id="{instance_id}"] [data-section="{element_id}"]'
                    css = f"{selector} {{\n"
                    for key, value in normal_styles.items():
                        css_property = key.replace('_', '-')
                        css += f"    {css_property}: {value};\n"
                    css += "}\n"
                    css_rules.append(css)
                
                # ===== HANDLE TEXT OPACITY IN COMPONENTS (NEW) =====
                text_opacity = styles.get('text_opacity')
                text_opacity_children = styles.get('text_opacity_children', False)
                
                if text_opacity is not None:
                    opacity_value = float(text_opacity) if isinstance(text_opacity, str) else text_opacity
                    
                    if opacity_value < 1.0:
                        if text_opacity_children:
                            text_opacity_css = f"""
[data-instance-id="{instance_id}"] [data-section="{element_id}"] .editable-text,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] p,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] h1,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] h2,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] h3,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] h4,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] h5,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] h6,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] span,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] a,
[data-instance-id="{instance_id}"] [data-section="{element_id}"] [data-text] {{
    color: rgba(var(--text-color-rgb, 0, 0, 0), {opacity_value}) !important;
}}
"""
                            css_rules.append(text_opacity_css.strip())
                        else:
                            text_opacity_css = f"""
[data-instance-id="{instance_id}"] [data-section="{element_id}"] {{
    color: rgba(var(--text-color-rgb, 0, 0, 0), {opacity_value}) !important;
}}
"""
                            css_rules.append(text_opacity_css.strip())
                
                # Hover state
                hover_enabled = False
                hover_data = {}
                
                if 'hover' in styles and isinstance(styles['hover'], dict):
                    hover_data = styles['hover']
                    hover_enabled = hover_data.get('enabled', False)
                
                if hover_enabled and 'styles' in hover_data:
                    hover_styles = hover_data['styles']
                    selector = f'[data-instance-id="{instance_id}"] [data-section="{element_id}"]:hover'
                    css = f"{selector} {{\n"
                    
                    transition = hover_styles.get('transition', '0.3s')
                    css += f"    transition: all {transition} ease;\n"
                    
                    if hover_styles.get('transform'):
                        css += f"    transform: {hover_styles['transform']};\n"
                    if hover_styles.get('background_color'):
                        css += f"    background-color: {hover_styles['background_color']};\n"
                    if hover_styles.get('text_color'):
                        css += f"    color: {hover_styles['text_color']};\n"
                    if hover_styles.get('border'):
                        css += f"    border: {hover_styles['border']};\n"
                    if hover_styles.get('box_shadow'):
                        css += f"    box-shadow: {hover_styles['box_shadow']};\n"
                    if hover_styles.get('animation'):
                        animation = hover_styles['animation']
                        if animation in ['pulse', 'bounce', 'shake', 'glow']:
                            css += f"    animation: {animation} 1s infinite;\n"
                        else:
                            css += f"    animation: {animation} 0.3s ease;\n"
                    
                    css += "}\n"
                    css_rules.append(css)
    
    return safe('\n'.join(css_rules))


@register.simple_tag
def generate_hover_keyframes():
    """Generate keyframes for hover animations"""
    keyframes = """
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

@keyframes glow {
    0% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0.7); }
    50% { box-shadow: 0 0 20px 5px rgba(67, 97, 238, 0.5); }
    100% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0); }
}
"""
    return safe(keyframes)


# ===== NEW TAG: Generate dimension variables for text opacity =====
@register.simple_tag
def generate_text_color_rgb_variables(page):
    """
    Generate RGB variables for text colors to support text opacity
    Output: --text-color-rgb: 0, 0, 0;
    """
    if not page:
        return ''
    
    css_vars = []
    
    # Get the primary text color from active palette or default
    text_color = '#000000'
    if hasattr(page, 'active_palette_colors') and page.active_palette_colors:
        text_color_data = page.active_palette_colors.get('text-color') or \
                         page.active_palette_colors.get('text_color') or \
                         page.active_palette_colors.get('heading-color')
        if text_color_data:
            if isinstance(text_color_data, dict):
                text_color = text_color_data.get('hex', '#000000')
            else:
                text_color = text_color_data
    
    # Convert hex to RGB
    if text_color.startswith('#'):
        r = int(text_color[1:3], 16)
        g = int(text_color[3:5], 16)
        b = int(text_color[5:7], 16)
        css_vars.append(f'--text-color-rgb: {r}, {g}, {b};')
    
    # Also add a default white text RGB for dark backgrounds
    css_vars.append('--text-color-light-rgb: 255, 255, 255;')
    
    if css_vars:
        return safe(f":root {{\n    {''.join(css_vars)}\n}}")
    return ''