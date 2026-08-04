# builder/management/commands/add_css_variables_to_templates.py

import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
import re

class Command(BaseCommand):
    help = 'Add CSS variable definitions to existing templates'
    
    def handle(self, *args, **options):
        templates_dir = Path(settings.BASE_DIR) /'templates'/ 'builder' / 'public_templates'
        
        if not templates_dir.exists():
            self.stdout.write(self.style.ERROR(f"Templates directory not found: {templates_dir}"))
            return
        
        for template_dir in templates_dir.iterdir():
            if template_dir.is_dir():
                base_html = template_dir / 'base.html'
                if base_html.exists():
                    self.add_variables_to_base(base_html)
                
                # Also check for direct HTML files
                for html_file in template_dir.glob('*.html'):
                    if html_file.name != 'base.html':
                        self.convert_hardcoded_colors(html_file)
        
        self.stdout.write(self.style.SUCCESS("✅ Templates updated with CSS variables!"))
    
    def add_variables_to_base(self, filepath):
        """Add :root CSS variables to base.html"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if variables already exist
        if ':root' in content and '--primary-color' in content:
            self.stdout.write(f"  ⏭️  Variables already exist in {filepath}")
            return
        
        # Find the <style> tag or create one
        variables_block = '''
        <style>
            :root {
                --primary-color: #4361ee;
                --secondary-color: #3a0ca3;
                --accent-color: #f72585;
                --background-color: #ffffff;
                --text-color: #212529;
                --heading-color: #0b1e33;
                --border-color: #dee2e6;
                --success-color: #06d6a0;
                --warning-color: #ffd166;
                --error-color: #ef476f;
                --nav-bg: #333333;
                --nav-text: #ffffff;
                --card-bg: #f8f9fa;
                --button-bg: #4361ee;
                --button-text: #ffffff;
                --button-hover: #3a0ca3;
            }
        </style>
        '''
        
        # Insert after <head>
        if '<head>' in content:
            content = content.replace('<head>', f'<head>\n{variables_block}')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.stdout.write(self.style.SUCCESS(f"  ✅ Added variables to {filepath}"))
    
    def convert_hardcoded_colors(self, filepath):
        """Convert hardcoded colors to CSS variables"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Color mapping dictionary
        color_mappings = [
            (r'background:\s*#667eea', 'background: var(--primary-color, #667eea)'),
            (r'background:\s*#764ba2', 'background: var(--secondary-color, #764ba2)'),
            (r'background:\s*#f72585', 'background: var(--accent-color, #f72585)'),
            (r'background:\s*#4361ee', 'background: var(--button-bg, #4361ee)'),
            (r'background:\s*#f8f9fa', 'background: var(--card-bg, #f8f9fa)'),
            (r'color:\s*white', 'color: var(--nav-text, white)'),
            (r'border:\s*1px\s+solid\s+#ddd', 'border: 1px solid var(--border-color, #ddd)'),
        ]
        
        modified = False
        for pattern, replacement in color_mappings:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.stdout.write(f"  ✅ Converted colors in {filepath}")