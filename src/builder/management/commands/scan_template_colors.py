# # builder/management/commands/scan_template_colors.py

# from django.core.management.base import BaseCommand
# from django.db import transaction
# from builder.models import Template, TemplateColorMapping
# from builder.utils.color_extractor import TemplateColorExtractor
# import logging

# logger = logging.getLogger(__name__)

# class Command(BaseCommand):
#     help = 'Scan all templates to discover CSS color variables'
    
#     def add_arguments(self, parser):
#         parser.add_argument('--template', type=str, help='Specific template name to scan')
#         parser.add_argument('--force', action='store_true', help='Force rescan even if exists')
    
#     def handle(self, *args, **options):
#         template_name = options.get('template')
#         force = options.get('force', False)
        
#         if template_name:
#             templates = Template.objects.filter(name=template_name)
#         else:
#             templates = Template.objects.filter(is_active=True)
        
#         self.stdout.write(f"Scanning {templates.count()} templates for color variables...")
        
#         for template in templates:
#             self.stdout.write(f"  Scanning: {template.name}...", ending='')
            
#             try:
#                 with transaction.atomic():
#                     # Extract color variables
#                     color_map = TemplateColorExtractor.generate_color_map(template.name)
                    
#                     # Check if mapping exists
#                     try:
#                         mapping = TemplateColorMapping.objects.get(template=template)
                        
#                         # UPDATE existing record
#                         mapping.variables = color_map['variables']
#                         mapping.suggested_mapping = color_map['suggested_mapping']
#                         mapping.scan_count += 1  # This works on update
#                         mapping.save(update_fields=['variables', 'suggested_mapping', 'scan_count', 'updated_at'])
#                         created = False
                        
#                     except TemplateColorMapping.DoesNotExist:
#                         # CREATE new record - DON'T use F() expressions here
#                         mapping = TemplateColorMapping.objects.create(
#                             template=template,
#                             variables=color_map['variables'],
#                             suggested_mapping=color_map['suggested_mapping'],
#                             scan_count=1  # Start at 1 for first scan
#                         )
#                         created = True
                    
#                     status = self.style.SUCCESS(" Created") if created else self.style.SUCCESS(" Updated")
#                     var_count = len(color_map['variables'])
#                     self.stdout.write(f"{status} ({var_count} variables found, scan #{mapping.scan_count})")
                    
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f" Error: {e}"))
#                 logger.exception(f"Error scanning template {template.name}")
        
#         self.stdout.write(self.style.SUCCESS("\n✅ Template color scanning complete!"))


# builder/management/commands/scan_template_colors.py

# builder/management/commands/scan_template_colors.py

from django.core.management.base import BaseCommand
from django.db import transaction
from builder.models import Template, TemplateColorMapping
from builder.utils.color_extractor import TemplateColorExtractor
import logging
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scan editable templates to discover CSS color variables from home.html'

    def add_arguments(self, parser):
        parser.add_argument('--template', type=str, help='Specific template name to scan')
        parser.add_argument('--force', action='store_true', help='Force rescan even if exists')

    def handle(self, *args, **options):
        template_name = options.get('template')
        force = options.get('force', False)

        if template_name:
            templates = Template.objects.filter(name=template_name)
        else:
            templates = Template.objects.filter(is_active=True)

        self.stdout.write(f"Scanning {templates.count()} editable templates for color variables in home.html...")

        for template in templates:
            self.stdout.write(f"  Scanning: {template.name}/home.html...", ending='')

            try:
                with transaction.atomic():
                    # Extract color variables from EDITABLE template's home.html
                    color_map = self.extract_colors_from_editable_template(template.name)

                    if not color_map or not color_map.get('variables'):
                        self.stdout.write(self.style.WARNING(f" No variables found in home.html"))
                        continue

                    # Check if mapping exists
                    try:
                        mapping = TemplateColorMapping.objects.get(template=template)

                        # UPDATE existing record
                        mapping.variables = color_map['variables']
                        mapping.suggested_mapping = color_map['suggested_mapping']
                        mapping.scan_count += 1
                        mapping.save(update_fields=['variables', 'suggested_mapping', 'scan_count', 'updated_at'])
                        created = False

                    except TemplateColorMapping.DoesNotExist:
                        # CREATE new record
                        mapping = TemplateColorMapping.objects.create(
                            template=template,
                            variables=color_map['variables'],
                            suggested_mapping=color_map['suggested_mapping'],
                            scan_count=1
                        )
                        created = True

                    status = self.style.SUCCESS(" Created") if created else self.style.SUCCESS(" Updated")
                    var_count = len(color_map['variables'])
                    self.stdout.write(f"{status} ({var_count} variables found, scan #{mapping.scan_count})")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f" Error: {e}"))
                logger.exception(f"Error scanning template {template.name}")

        self.stdout.write(self.style.SUCCESS("\n✅ Editable template color scanning complete!"))

    def extract_colors_from_editable_template(self, template_name):
        """
        Extract CSS color variables from an EDITABLE template's home.html file.
        Looks ONLY in builder/templates/ directory (NOT public_templates).
        """
        from django.conf import settings
        import re
        import os

        # ONLY look in editable templates directory
        # These are the templates used by the editor
        possible_paths = [
            # Main editable templates directory
            os.path.join(settings.BASE_DIR, 'builder', 'templates', 'builder', 'templates', template_name, 'home.html'),
            # Alternative: direct templates folder
            os.path.join(settings.BASE_DIR, 'builder', 'templates', template_name, 'home.html'),
            # Some projects use this structure
            os.path.join(settings.BASE_DIR, 'templates', 'builder', 'templates', template_name, 'home.html'),
        ]

        html_content = None
        found_path = None

        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                found_path = path
                self.stdout.write(f"\n    Found: {found_path}")
                break

        # If not found, try to search the editable templates directory
        if not html_content:
            editable_template_dir = os.path.join(settings.BASE_DIR, 'builder', 'templates', 'builder', 'templates', template_name)
            if not os.path.exists(editable_template_dir):
                editable_template_dir = os.path.join(settings.BASE_DIR, 'builder', 'templates', template_name)
            
            if os.path.exists(editable_template_dir):
                # Look for home.html or any .html file that might be the main template
                priority_files = ['home.html', 'index.html', 'base.html', f'{template_name}.html']
                for filename in priority_files:
                    filepath = os.path.join(editable_template_dir, filename)
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        found_path = filepath
                        self.stdout.write(f"\n    Found: {found_path}")
                        break

        if not html_content:
            self.stdout.write(f"\n    ⚠️ No editable template found at: {possible_paths[0]}")
            return {'variables': {}, 'suggested_mapping': {}}

        return self.parse_css_variables(html_content, template_name)

    def parse_css_variables(self, html_content, template_name):
        """
        Parse CSS variables from HTML content.
        Looks for :root blocks and extracts --variable-name: value; pairs.
        """
        import re

        variables = {}
        suggested_mapping = {}

        # Pattern to find :root blocks
        root_pattern = r':root\s*\{([^}]+)\}'
        root_matches = re.findall(root_pattern, html_content, re.DOTALL)

        # Also check <style> tags specifically
        style_pattern = r'<style[^>]*>(.*?)</style>'
        style_matches = re.findall(style_pattern, html_content, re.DOTALL | re.IGNORECASE)

        all_css = ' '.join(root_matches + style_matches)

        if not all_css:
            return {'variables': {}, 'suggested_mapping': {}}

        # Pattern to extract CSS custom properties
        var_pattern = r'--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);'
        var_matches = re.findall(var_pattern, all_css)

        for var_name, var_value in var_matches:
            var_name = var_name.strip()
            var_value = var_value.strip()

            # Skip if empty
            if not var_value:
                continue

            # Skip non-color variables (shadows, transitions, spacing, etc.)
            non_color_keywords = ['shadow', 'transition', 'spacing', 'border-radius', 'padding', 'margin', 'width', 'height']
            if any(keyword in var_name.lower() for keyword in non_color_keywords):
                continue

            # Determine color type based on variable name
            color_type = self.infer_color_type(var_name)

            # Store variable info
            variables[var_name] = {
                'value': var_value,
                'type': 'hex' if var_value.startswith('#') else 'other',
                'source': 'editable_template'
            }

            # Create suggested mapping
            if color_type != 'custom':
                suggested_mapping[var_name] = {
                    'role': color_type,
                    'confidence': 0.8
                }

        return {
            'variables': variables,
            'suggested_mapping': suggested_mapping
        }

    def infer_color_type(self, var_name):
        """
        Infer the semantic role of a CSS variable based on its name.
        Returns one of: background, text, heading, primary, secondary, 
                       accent, border, success, warning, error, custom
        """
        var_lower = var_name.lower()

        # Priority-based matching
        type_patterns = [
            (['background', 'bg-', '-bg'], 'background'),
            (['text-', '-text', 'font-color'], 'text'),
            (['heading', 'title', 'header-'], 'heading'),
            (['primary', 'brand', 'main-'], 'primary'),
            (['secondary', 'alt-'], 'secondary'),
            (['accent', 'highlight', 'cta'], 'accent'),
            (['border', 'outline', 'stroke'], 'border'),
            (['success', 'confirm', 'valid', 'green'], 'success'),
            (['warning', 'alert', 'caution', 'yellow'], 'warning'),
            (['error', 'danger', 'invalid', 'red'], 'error'),
        ]

        for patterns, role in type_patterns:
            if any(pattern in var_lower for pattern in patterns):
                return role

        return 'custom'