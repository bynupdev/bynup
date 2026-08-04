# builder/management/commands/standardize_template_variables.py

from django.core.management.base import BaseCommand
from django.conf import settings
from builder.models import Template, TemplateColorMapping
import os
import re
from pathlib import Path

class Command(BaseCommand):
    help = 'Standardize all template CSS variables to semantic names and update references (both editable and public)'

    # Standard semantic variables (in order)
    STANDARD_VARIABLES = [
        ('--background', 'Background color', '#ffffff'),
        ('--text', 'Text color', '#333333'),
        ('--heading', 'Heading color', '#222222'),
        ('--primary', 'Primary brand color', '#4361ee'),
        ('--secondary', 'Secondary color', '#3a0ca3'),
        ('--accent', 'Accent/highlight color', '#f72585'),
        ('--border', 'Border color', '#dee2e6'),
        ('--success', 'Success state color', '#06d6a0'),
        ('--warning', 'Warning state color', '#ffd166'),
        ('--error', 'Error state color', '#ef476f'),
    ]
    
    # Role detection patterns (ordered by priority)
    ROLE_PATTERNS = {
        'background': [
            (r'background(-color)?:\s*var\(--([a-zA-Z0-9_-]+)\)', 3),
            (r'--[a-zA-Z0-9_-]*bg[a-zA-Z0-9_-]*', 2),
            (r'--[a-zA-Z0-9_-]*background[a-zA-Z0-9_-]*', 3),
        ],
        'text': [
            (r'color:\s*var\(--([a-zA-Z0-9_-]+)\)(?!.*background)', 3),
            (r'--[a-zA-Z0-9_-]*text[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*font[a-zA-Z0-9_-]*', 2),
        ],
        'heading': [
            (r'h[1-6][^}]*color:\s*var\(--([a-zA-Z0-9_-]+)\)', 3),
            (r'--[a-zA-Z0-9_-]*heading[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*title[a-zA-Z0-9_-]*', 2),
        ],
        'primary': [
            (r'\.btn[^}]*background:\s*var\(--([a-zA-Z0-9_-]+)\)', 3),
            (r'--[a-zA-Z0-9_-]*primary[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*brand[a-zA-Z0-9_-]*', 2),
            (r'--[a-zA-Z0-9_-]*main[a-zA-Z0-9_-]*', 2),
        ],
        'secondary': [
            (r'--[a-zA-Z0-9_-]*secondary[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*alt[a-zA-Z0-9_-]*', 2),
        ],
        'accent': [
            (r'--[a-zA-Z0-9_-]*accent[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*highlight[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*cta[a-zA-Z0-9_-]*', 2),
        ],
        'border': [
            (r'border(-color)?:\s*var\(--([a-zA-Z0-9_-]+)\)', 3),
            (r'--[a-zA-Z0-9_-]*border[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*outline[a-zA-Z0-9_-]*', 2),
        ],
        'success': [
            (r'--[a-zA-Z0-9_-]*success[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*green[a-zA-Z0-9_-]*', 2),
            (r'--[a-zA-Z0-9_-]*valid[a-zA-Z0-9_-]*', 2),
        ],
        'warning': [
            (r'--[a-zA-Z0-9_-]*warning[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*yellow[a-zA-Z0-9_-]*', 2),
            (r'--[a-zA-Z0-9_-]*alert[a-zA-Z0-9_-]*', 2),
            (r'--[a-zA-Z0-9_-]*caution[a-zA-Z0-9_-]*', 2),
        ],
        'error': [
            (r'--[a-zA-Z0-9_-]*error[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*danger[a-zA-Z0-9_-]*', 3),
            (r'--[a-zA-Z0-9_-]*red[a-zA-Z0-9_-]*', 2),
            (r'--[a-zA-Z0-9_-]*invalid[a-zA-Z0-9_-]*', 2),
        ],
    }

    def add_arguments(self, parser):
        parser.add_argument('--template', type=str, help='Specific template to standardize')
        parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving')
        parser.add_argument('--backup', action='store_true', help='Create backup before modifying')
        parser.add_argument('--editable-only', action='store_true', help='Only standardize editable templates')
        parser.add_argument('--public-only', action='store_true', help='Only standardize public templates')

    def handle(self, *args, **options):
        template_name = options.get('template')
        dry_run = options.get('dry_run', False)
        create_backup = options.get('backup', False)
        editable_only = options.get('editable_only', False)
        public_only = options.get('public_only', False)
        
        if template_name:
            templates = Template.objects.filter(name=template_name)
        else:
            templates = Template.objects.filter(is_active=True)
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS(f"Standardizing {templates.count()} templates"))
        if editable_only:
            self.stdout.write(self.style.WARNING("📝 Editable templates only"))
        elif public_only:
            self.stdout.write(self.style.WARNING("🌐 Public templates only"))
        else:
            self.stdout.write(self.style.SUCCESS("📝 Editable + 🌐 Public templates"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}\n"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("⚠️ DRY RUN - No files will be modified\n"))
        
        total_editable_updated = 0
        total_public_updated = 0
        total_renamed = 0
        
        for template in templates:
            self.stdout.write(f"\n📁 Processing: {template.name}")
            self.stdout.write("-" * 50)
            
            # Standardize editable templates
            if not public_only:
                self.stdout.write("  📝 Editable Templates:")
                editable_result = self.standardize_editable_template(template, dry_run, create_backup)
                if editable_result:
                    files_updated, vars_renamed = editable_result
                    total_editable_updated += files_updated
                    total_renamed = max(total_renamed, vars_renamed)
            
            # Standardize public templates
            if not editable_only:
                self.stdout.write("  🌐 Public Templates:")
                public_result = self.standardize_public_template(template, dry_run, create_backup)
                if public_result:
                    files_updated, vars_renamed = public_result
                    total_public_updated += files_updated
                    total_renamed = max(total_renamed, vars_renamed)
            
            # Update TemplateColorMapping (based on editable template)
            if not dry_run and not public_only:
                self.update_template_mapping_from_editable(template)
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS(f"✅ Complete!"))
        self.stdout.write(self.style.SUCCESS(f"   Editable files updated: {total_editable_updated}"))
        self.stdout.write(self.style.SUCCESS(f"   Public files updated: {total_public_updated}"))
        self.stdout.write(self.style.SUCCESS(f"   Variables standardized: {total_renamed}"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}"))

    def standardize_editable_template(self, template, dry_run=False, create_backup=False):
        """Standardize editable template files."""
        template_files = self.find_editable_template_files(template.name)
        
        if not template_files:
            self.stdout.write(self.style.WARNING("     ⚠️ No editable template files found"))
            return None
        
        return self.standardize_files(template_files, dry_run, create_backup, indent="     ")

    def standardize_public_template(self, template, dry_run=False, create_backup=False):
        """Standardize public template files."""
        template_files = self.find_public_template_files(template.name)
        
        if not template_files:
            self.stdout.write(self.style.WARNING("     ⚠️ No public template files found"))
            return None
        
        return self.standardize_files(template_files, dry_run, create_backup, indent="     ")

    def standardize_files(self, template_files, dry_run=False, create_backup=False, indent=""):
        """Standardize a list of template files."""
        files_updated = 0
        all_mappings = {}
        
        # First pass: discover all CSS variables and determine their roles
        for filepath in template_files:
            rel_path = self.get_relative_path(filepath)
            self.stdout.write(f"{indent}📄 Scanning: {rel_path}")
            
            content = self.read_file(filepath)
            if not content:
                continue
            
            # Extract all CSS variables from :root
            root_vars = self.extract_root_variables(content)
            
            # Detect roles for each variable
            var_roles = self.detect_variable_roles(content, root_vars)
            
            # Create mapping to standard variables
            mappings = self.create_variable_mapping(root_vars, var_roles)
            all_mappings.update(mappings)
        
        # Show detected mappings
        if all_mappings:
            self.stdout.write(f"\n{indent}🔍 Detected variable mappings:")
            for old_var, new_var in sorted(all_mappings.items()):
                self.stdout.write(f"{indent}   {old_var} → {new_var}")
        
        # Second pass: apply the changes
        if not dry_run and all_mappings:
            for filepath in template_files:
                rel_path = self.get_relative_path(filepath)
                self.stdout.write(f"{indent}✏️ Updating: {rel_path}")
                
                content = self.read_file(filepath)
                if not content:
                    continue
                
                # Replace variable names in :root
                new_content = self.replace_variable_names(content, all_mappings)
                
                # Replace variable references throughout the file
                new_content = self.replace_variable_references(new_content, all_mappings)
                
                if new_content != content:
                    if create_backup:
                        backup_path = str(filepath) + '.backup'
                        self.write_file(backup_path, content)
                        self.stdout.write(f"{indent}   💾 Backup saved")
                    
                    self.write_file(filepath, new_content)
                    files_updated += 1
                    self.stdout.write(f"{indent}   ✅ Updated")
        
        return files_updated, len(all_mappings)

    def find_editable_template_files(self, template_name):
        """Find all HTML and CSS files for an editable template."""
        from django.conf import settings
        
        files = []
        
        # Editable templates directory paths
        search_paths = [
            os.path.join(settings.BASE_DIR, 'builder', 'templates', 'builder', 'templates', template_name),
            os.path.join(settings.BASE_DIR, 'builder', 'templates', template_name),
            os.path.join(settings.BASE_DIR, 'templates', 'builder', 'templates', template_name),
        ]
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirs, filenames in os.walk(search_path):
                    for filename in filenames:
                        if filename.endswith(('.html', '.css')):
                            files.append(os.path.join(root, filename))
                break
        
        return files

    def find_public_template_files(self, template_name):
        """Find all HTML and CSS files for a public template."""
        from django.conf import settings
        
        files = []
        
        # Public templates directory paths
        search_paths = [
            os.path.join(settings.BASE_DIR, 'builder', 'public_templates', template_name),
            os.path.join(settings.BASE_DIR, 'builder', 'templates', 'builder', 'public_templates', template_name),
            os.path.join(settings.BASE_DIR, 'templates', 'builder', 'public_templates', template_name),
        ]
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirs, filenames in os.walk(search_path):
                    for filename in filenames:
                        if filename.endswith(('.html', '.css')):
                            files.append(os.path.join(root, filename))
                break
        
        # Also check for single-file public templates
        single_file_paths = [
            os.path.join(settings.BASE_DIR, 'builder', 'public_templates', f'{template_name}.html'),
            os.path.join(settings.BASE_DIR, 'builder', 'templates', 'builder', 'public_templates', f'{template_name}.html'),
        ]
        
        for filepath in single_file_paths:
            if os.path.exists(filepath):
                files.append(filepath)
        
        return files

    def get_relative_path(self, filepath):
        """Get a shorter relative path for display."""
        parts = Path(filepath).parts
        # Find 'builder' or 'templates' in path and show from there
        for i, part in enumerate(parts):
            if part in ['builder', 'templates']:
                return str(Path(*parts[i:]))
        return Path(filepath).name

    def read_file(self, filepath):
        """Read file content with proper encoding."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"     ❌ Error reading: {e}"))
            return None

    def write_file(self, filepath, content):
        """Write file content with proper encoding."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"     ❌ Error writing: {e}"))
            return False

    def extract_root_variables(self, content):
        """Extract all CSS variables defined in :root blocks."""
        variables = {}
        
        # Find all :root blocks
        root_pattern = r':root\s*\{([^}]+)\}'
        style_pattern = r'<style[^>]*>(.*?)</style>'
        
        all_css = content
        
        # Extract from <style> tags
        style_matches = re.findall(style_pattern, content, re.DOTALL | re.IGNORECASE)
        for style_content in style_matches:
            all_css += style_content
        
        # Find :root blocks
        root_matches = re.findall(root_pattern, all_css, re.DOTALL)
        
        for root_block in root_matches:
            # Extract variable definitions
            var_pattern = r'--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);'
            var_matches = re.findall(var_pattern, root_block)
            
            for var_name, var_value in var_matches:
                var_name = var_name.strip()
                var_value = var_value.strip()
                
                # Skip non-color variables
                if self.is_non_color_variable(var_name, var_value):
                    continue
                
                variables[f'--{var_name}'] = var_value
        
        return variables

    def is_non_color_variable(self, var_name, var_value):
        """Check if a variable is not a color variable."""
        non_color_keywords = [
            'shadow', 'transition', 'spacing', 'padding', 'margin',
            'width', 'height', 'radius', 'font-', 'weight', 'family',
            'size', 'duration', 'delay', 'timing', 'ease', 'z-index',
            'display', 'position', 'flex', 'grid', 'gap', 'transform',
            'animation', 'keyframe', 'opacity', 'visibility'
        ]
        
        var_lower = var_name.lower()
        if any(keyword in var_lower for keyword in non_color_keywords):
            return True
        
        # Check if value looks like a color
        color_patterns = [
            r'^#[0-9A-Fa-f]{3,8}$',
            r'^rgb',
            r'^hsl',
            r'^var\(--',
        ]
        
        for pattern in color_patterns:
            if re.match(pattern, var_value.strip()):
                return False
        
        return True

    def detect_variable_roles(self, content, root_vars):
        """Detect the semantic role of each variable based on usage."""
        var_roles = {}
        
        for var_name in root_vars.keys():
            var_short = var_name[2:]  # Remove '--'
            scores = {}
            
            for role, patterns in self.ROLE_PATTERNS.items():
                for pattern, weight in patterns:
                    try:
                        if '([a-zA-Z0-9_-]+)' in pattern:
                            # Pattern that captures variable name
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if isinstance(match, tuple):
                                    captured_var = match[-1]
                                else:
                                    captured_var = match
                                if captured_var == var_short:
                                    scores[role] = scores.get(role, 0) + weight
                        else:
                            # Simple pattern match
                            if re.search(pattern, content, re.IGNORECASE):
                                scores[role] = scores.get(role, 0) + weight
                    except Exception:
                        continue
            
            # Also check variable name for hints
            name_hints = self.get_name_hints(var_short)
            for role, weight in name_hints.items():
                scores[role] = scores.get(role, 0) + weight
            
            # Determine best role
            if scores:
                best_role = max(scores, key=scores.get)
                if scores[best_role] >= 2:  # Minimum confidence threshold
                    var_roles[var_name] = best_role
                else:
                    var_roles[var_name] = 'custom'
            else:
                var_roles[var_name] = 'custom'
        
        return var_roles

    def get_name_hints(self, var_name):
        """Get role hints from variable name."""
        hints = {}
        var_lower = var_name.lower()
        
        name_mappings = {
            'background': ['bg', 'background', 'back'],
            'text': ['text', 'font', 'copy', 'body', 'paragraph'],
            'heading': ['heading', 'title', 'header', 'h1', 'h2', 'headline'],
            'primary': ['primary', 'brand', 'main'],
            'secondary': ['secondary', 'alt', 'second'],
            'accent': ['accent', 'highlight', 'cta'],
            'border': ['border', 'outline', 'stroke', 'divider'],
            'success': ['success', 'green', 'valid', 'confirm'],
            'warning': ['warning', 'yellow', 'alert', 'caution'],
            'error': ['error', 'danger', 'red', 'invalid'],
        }
        
        for role, keywords in name_mappings.items():
            for keyword in keywords:
                if keyword in var_lower:
                    hints[role] = hints.get(role, 0) + 1
        
        return hints

    def create_variable_mapping(self, root_vars, var_roles):
        """Create mapping from original variables to standard variables."""
        mappings = {}
        
        # Standard role to variable name
        role_to_standard = {
            'background': '--background',
            'text': '--text',
            'heading': '--heading',
            'primary': '--primary',
            'secondary': '--secondary',
            'accent': '--accent',
            'border': '--border',
            'success': '--success',
            'warning': '--warning',
            'error': '--error',
        }
        
        # Track which standard variables are already assigned
        assigned_standards = set()
        
        # First pass: assign based on detected roles
        for var_name, role in var_roles.items():
            if role != 'custom' and role in role_to_standard:
                standard_var = role_to_standard[role]
                if standard_var not in assigned_standards:
                    mappings[var_name] = standard_var
                    assigned_standards.add(standard_var)
        
        # Second pass: fill remaining with unused variables
        remaining_vars = [v for v in root_vars.keys() if v not in mappings]
        standard_order = [v[0] for v in self.STANDARD_VARIABLES]
        
        for standard_var in standard_order:
            if standard_var not in assigned_standards and remaining_vars:
                mappings[remaining_vars.pop(0)] = standard_var
                assigned_standards.add(standard_var)
        
        return mappings

    def replace_variable_names(self, content, mappings):
        """Replace variable names in :root definitions."""
        
        def replace_in_root(match):
            root_content = match.group(1)
            
            for old_var, new_var in mappings.items():
                old_name = old_var[2:]  # Remove '--'
                new_name = new_var[2:]  # Remove '--'
                
                # Replace the variable name
                pattern = f'--{re.escape(old_name)}\\s*:'
                replacement = f'--{new_name}:'
                root_content = re.sub(pattern, replacement, root_content)
            
            return f':root {{{root_content}}}'
        
        # Replace in :root blocks
        content = re.sub(r':root\s*\{([^}]+)\}', replace_in_root, content, flags=re.DOTALL)
        
        return content

    def replace_variable_references(self, content, mappings):
        """Replace all var(--old-name) references with var(--new-name)."""
        
        for old_var, new_var in mappings.items():
            old_name = old_var[2:]  # Remove '--'
            new_name = new_var[2:]  # Remove '--'
            
            # Replace var(--old-name)
            pattern = f'var\\(--{re.escape(old_name)}\\)'
            replacement = f'var(--{new_name})'
            content = re.sub(pattern, replacement, content)
            
            # Replace var(--old-name, fallback)
            pattern = f'var\\(--{re.escape(old_name)}\\s*,'
            replacement = f'var(--{new_name},'
            content = re.sub(pattern, replacement, content)
        
        return content

    def update_template_mapping_from_editable(self, template):
        """Update TemplateColorMapping based on editable template."""
        from builder.models import TemplateColorMapping
        
        # Try to read the standardized editable template to get the new variables
        editable_files = self.find_editable_template_files(template.name)
        
        if not editable_files:
            self.stdout.write("  ⚠️ No editable files found for TemplateColorMapping update")
            return
        
        # Parse the first file to get variables
        content = self.read_file(editable_files[0])
        if not content:
            return
        
        root_vars = self.extract_root_variables(content)
        
        # Build variables dict
        variables = {}
        for var_name, var_value in root_vars.items():
            var_short = var_name[2:]
            variables[var_short] = {
                'value': var_value,
                'type': 'hex' if var_value.startswith('#') else 'other',
                'source': 'standardized'
            }
        
        # Create suggested mapping
        role_mapping = ['background', 'text', 'heading', 'primary', 
                       'secondary', 'accent', 'border', 'success', 'warning', 'error']
        standard_order = ['--background', '--text', '--heading', '--primary',
                         '--secondary', '--accent', '--border', '--success', 
                         '--warning', '--error']
        
        suggested_mapping = {}
        for i, std_var in enumerate(standard_order):
            var_short = std_var[2:]
            if std_var in root_vars or f'--{var_short}' in root_vars:
                suggested_mapping[var_short] = {
                    'role': role_mapping[i] if i < len(role_mapping) else 'custom',
                    'confidence': 1.0
                }
        
        # Update or create
        TemplateColorMapping.objects.update_or_create(
            template=template,
            defaults={
                'variables': variables,
                'suggested_mapping': suggested_mapping,
                'custom_mapping': {},
                'scan_count': 1
            }
        )
        
        self.stdout.write(f"  📊 Updated TemplateColorMapping for {template.name}")