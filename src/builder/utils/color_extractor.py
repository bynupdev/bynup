# builder/utils/color_extractor.py

import re
import cssutils
from cssutils.css import CSSStyleSheet
import logging

logger = logging.getLogger(__name__)

class TemplateColorExtractor:
    """
    Extracts CSS color variables from template CSS files
    """
    
    # Regex patterns for finding CSS variables
    VAR_PATTERN = re.compile(r'--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);')
    COLOR_VALUE_PATTERN = re.compile(
        r'^#(?:[0-9a-fA-F]{3}){1,2}$|'  # Hex colors
        r'^rgb\(.*\)$|'                 # RGB
        r'^rgba\(.*\)$|'               # RGBA
        r'^hsl\(.*\)$|'                # HSL
        r'^hsla\(.*\)$|'              # HSLA
        r'^(red|blue|green|yellow|black|white|gray|grey|'  # Named colors
        r'purple|orange|pink|brown|cyan|magenta|teal|lime|'
        r'indigo|violet|gold|silver|coral|navy|maroon|olive)$',
        re.IGNORECASE
    )
    
   
    # builder/utils/color_extractor.py - Add debug output

    @classmethod
    def extract_from_template(cls, template_name):
        """Extract all CSS color variables from a template's CSS files"""
        from pathlib import Path
        from django.conf import settings
        
        template_css_files = []
        color_variables = {}
        
        # Get ALL possible template directories
        search_paths = []
        
        # Add TEMPLATES['DIRS'] from settings
        for template_dir in settings.TEMPLATES[0]['DIRS']:
            search_paths.append(Path(template_dir) / 'builder' / 'public_templates' / template_name)
            search_paths.append(Path(template_dir) / 'public_templates' / template_name)
        
        # Add app templates directory
        search_paths.append(Path(settings.BASE_DIR) / 'builder' / 'public_templates' / template_name)
        search_paths.append(Path(settings.BASE_DIR) / 'builder' / 'templates' / template_name)
        search_paths.append(Path(settings.BASE_DIR) / 'templates' / 'builder' / 'public_templates' / template_name)
        
        print(f"\n🔍 Searching for template '{template_name}' in:")
        for path in search_paths:
            print(f"   {path}")
        
        for base_path in search_paths:
            if base_path.exists():
                print(f"  ✅ Found template at: {base_path}")
                
                # Find all CSS files
                css_files = list(base_path.glob('**/*.css'))
                template_css_files.extend(css_files)
                
                # Also check inline styles in HTML files
                html_files = list(base_path.glob('**/*.html'))
                
                for css_file in css_files:
                    try:
                        with open(css_file, 'r', encoding='utf-8') as f:
                            css_content = f.read()
                            variables = cls._extract_from_css(css_content)
                            for var_name, var_data in variables.items():
                                if var_name not in color_variables:
                                    color_variables[var_name] = var_data
                                    color_variables[var_name]['source'] = str(css_file)
                    except Exception as e:
                        logger.error(f"Error reading CSS file {css_file}: {e}")
                
                # Extract from inline styles in HTML
                for html_file in html_files:
                    try:
                        with open(html_file, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                            variables = cls._extract_from_inline_styles(html_content)
                            for var_name, var_data in variables.items():
                                if var_name not in color_variables:
                                    color_variables[var_name] = var_data
                                    color_variables[var_name]['source'] = f"{html_file} (inline)"
                    except Exception as e:
                        logger.error(f"Error reading HTML file {html_file}: {e}")
        
        print(f"  📊 Found {len(color_variables)} color variables")
        if color_variables:
            print(f"  📋 Variables: {list(color_variables.keys())}")
        
        return {
            'variables': color_variables,
            'file_sources': [str(f) for f in template_css_files]
        }

    @classmethod
    def _extract_from_css(cls, css_content):
        """Extract color variables from CSS content"""
        variables = {}
        
        # Find :root and other selector blocks
        root_pattern = re.compile(r':root\s*\{([^}]+)\}', re.DOTALL)
        root_matches = root_pattern.findall(css_content)
        
        for root_content in root_matches:
            var_matches = cls.VAR_PATTERN.findall(root_content)
            for var_name, var_value in var_matches:
                var_value = var_value.strip()
                if cls._is_color_value(var_value):
                    variables[var_name] = {
                        'value': var_value,
                        'type': cls._get_color_type(var_value),
                        'original_value': var_value
                    }
        
        # Also find variables in other selectors
        other_vars = cls.VAR_PATTERN.findall(css_content)
        for var_name, var_value in other_vars:
            var_value = var_value.strip()
            if cls._is_color_value(var_value) and var_name not in variables:
                variables[var_name] = {
                    'value': var_value,
                    'type': cls._get_color_type(var_value),
                    'original_value': var_value
                }
        
        return variables
    
    @classmethod
    def _extract_from_inline_styles(cls, html_content):
        """Extract CSS variables from inline style tags"""
        variables = {}
        
        # Find style tags
        style_pattern = re.compile(r'<style[^>]*>([^<]+)</style>', re.DOTALL)
        style_matches = style_pattern.findall(html_content)
        
        for style_content in style_matches:
            # Look for :root in style tags
            root_pattern = re.compile(r':root\s*\{([^}]+)\}', re.DOTALL)
            root_matches = root_pattern.findall(style_content)
            
            for root_content in root_matches:
                var_matches = cls.VAR_PATTERN.findall(root_content)
                for var_name, var_value in var_matches:
                    var_value = var_value.strip()
                    if cls._is_color_value(var_value):
                        variables[var_name] = {
                            'value': var_value,
                            'type': cls._get_color_type(var_value),
                            'original_value': var_value,
                            'source': 'inline'
                        }
        
        return variables
    
    @classmethod
    def _is_color_value(cls, value):
        """Check if a CSS value is a color"""
        value = value.strip().lower()
        
        # Check hex colors
        if cls.COLOR_VALUE_PATTERN.match(value):
            return True
        
        # Check CSS color functions with numbers
        if value.startswith('rgb') or value.startswith('hsl'):
            return True
        
        # Check for CSS variables that might reference colors
        if value.startswith('var(--'):
            return True
        
        return False
    
    @classmethod
    def _get_color_type(cls, value):
        """Determine the type of color value"""
        value = value.strip().lower()
        
        if value.startswith('#'):
            return 'hex'
        elif value.startswith('rgb'):
            return 'rgb'
        elif value.startswith('hsl'):
            return 'hsl'
        elif value.startswith('var(--'):
            return 'variable'
        else:
            return 'named'
    
    @classmethod
    def generate_color_map(cls, template_name):
        """
        Generate a mapping of color variables to their roles
        This helps intelligently map palette colors to template variables
        """
        extracted = cls.extract_from_template(template_name)
        variables = extracted['variables']
        
        color_map = {
            'variables': variables,
            'suggested_mapping': cls._suggest_role_mapping(variables)
        }
        
        return color_map
    
    @classmethod
    def _suggest_role_mapping(cls, variables):
        """
        Suggest which palette color should map to which variable
        based on naming patterns
        """
        suggestions = {}
        
        role_keywords = {
            'primary': ['primary', 'brand', 'main', 'theme'],
            'secondary': ['secondary', 'accent-2', 'alt'],
            'accent': ['accent', 'highlight', 'cta'],
            'background': ['background', 'bg', 'surface', 'paper'],
            'text': ['text', 'font', 'body', 'paragraph'],
            'heading': ['heading', 'title', 'header', 'h1'],
            'border': ['border', 'outline', 'stroke', 'divider'],
            'success': ['success', 'positive', 'valid'],
            'warning': ['warning', 'caution', 'alert'],
            'error': ['error', 'danger', 'negative', 'invalid'],
            'info': ['info', 'information', 'note']
        }
        
        for var_name in variables.keys():
            var_lower = var_name.lower()
            
            for role, keywords in role_keywords.items():
                if any(keyword in var_lower for keyword in keywords):
                    suggestions[var_name] = {
                        'role': role,
                        'confidence': 0.8
                    }
                    break
            else:
                # Low confidence guess
                suggestions[var_name] = {
                    'role': 'custom',
                    'confidence': 0.3
                }
        
        return suggestions