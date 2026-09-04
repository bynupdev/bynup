# builder/management/commands/extract_copy.py

from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import json
import re
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Extract and manage template copywriting data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--template',
            type=str,
            help='Specific template to extract'
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Export template copy to JSON file'
        )
        parser.add_argument(
            '--import',
            type=str,
            dest='import_file',
            help='Import copy from JSON file'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available templates'
        )
        parser.add_argument(
            '--prompt',
            action='store_true',
            help='Generate AI prompt for the template'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all templates'
        )

    def handle(self, *args, **options):
        if options.get('list'):
            self.list_templates()
            return
        
        template_name = options.get('template')
        
        if options.get('all'):
            self.process_all_templates()
            return
        
        if not template_name:
            self.stdout.write(self.style.ERROR('❌ Please specify a template name'))
            self.stdout.write('   Usage: python manage.py extract_copy --template ModernEcommerce1')
            self.stdout.write('   Or list all templates: python manage.py extract_copy --list')
            return
        
        # Import from file
        if options.get('import_file'):
            self.import_copy(template_name, options['import_file'])
            return
        
        # Export to file
        if options.get('export'):
            self.export_copy(template_name, options['export'])
            return
        
        # Generate AI prompt
        if options.get('prompt'):
            self.generate_prompt(template_name)
            return
        
        # Extract and save
        self.extract_template(template_name)
    
    def list_templates(self):
        """List all available templates"""
        templates_path = Path(settings.BASE_DIR) / 'templates' / 'builder' / 'templates'
        
        if not templates_path.exists():
            templates_path = Path(settings.BASE_DIR) / 'builder' / 'templates'
        
        if not templates_path.exists():
            self.stdout.write(self.style.ERROR('❌ Templates directory not found'))
            return
        
        self.stdout.write(self.style.SUCCESS('📂 Available Templates:'))
        for template_dir in templates_path.iterdir():
            if template_dir.is_dir():
                # Check if JSON exists
                json_path = Path(settings.BASE_DIR) / 'builder' / 'copywriting' / 'templates' / f'{template_dir.name}.json'
                has_copy = '✅' if json_path.exists() else '❌'
                self.stdout.write(f'  {has_copy} {template_dir.name}')
    
    def extract_template(self, template_name):
        """Extract copy from a template"""
        self.stdout.write(f'🔍 Extracting copy from template: {template_name}')
        
        # Find the template path
        possible_paths = [
            Path(settings.BASE_DIR) / 'templates' / 'builder' / 'templates' / template_name,
            Path(settings.BASE_DIR) / 'builder' / 'templates' / template_name,
            Path(settings.BASE_DIR) / 'templates' / template_name,
        ]
        
        template_path = None
        for path in possible_paths:
            if path.exists():
                template_path = path
                break
        
        if not template_path:
            self.stdout.write(self.style.ERROR(f'❌ Template "{template_name}" not found'))
            return
        
        self.stdout.write(f'  📁 Found at: {template_path}')
        
        # Find all HTML files
        html_files = list(template_path.glob('*.html'))
        if not html_files:
            self.stdout.write(self.style.WARNING(f'⚠️ No HTML files found'))
            return
        
        all_texts = []
        all_pages = {}
        
        for html_file in html_files:
            page_name = html_file.stem
            self.stdout.write(f'  📄 Processing: {html_file.name}')
            
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            page_texts = self.extract_text_from_page(soup)
            
            if page_texts:
                all_pages[page_name] = page_texts
                all_texts.extend(page_texts)
                self.stdout.write(f'    Found {len(page_texts)} text elements')
        
        if not all_texts:
            self.stdout.write(self.style.WARNING('⚠️ No editable text found in this template'))
            return
        
        # Build the JSON data
        data = {
            'template': template_name,
            'pages': all_pages,
            'global_texts': all_texts,
            'metadata': {
                'total_elements': len(all_texts),
                'pages_count': len(all_pages),
                'components_count': 0
            }
        }
        
        # Save to JSON
        output_dir = Path(settings.BASE_DIR) / 'builder' / 'copywriting' / 'templates'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f'{template_name}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(self.style.SUCCESS(f'✅ JSON saved to: {output_file}'))
        self.stdout.write(f'   📊 Total elements: {len(all_texts)}')
        self.stdout.write(f'   📄 Pages: {list(all_pages.keys())}')
    
    def extract_text_from_page(self, soup):
        """Extract all editable text from a page"""
        texts = []
        seen = set()
        
        # 1. Elements with data-text attribute
        for el in soup.select('[data-text]'):
            text = el.get_text(strip=True)
            data_id = el.get('data-text', '')
            if text and data_id and data_id not in seen:
                seen.add(data_id)
                texts.append({
                    'id': data_id,
                    'text': text,
                    'type': self.get_element_type(el),
                    'customized': False
                })
        
        # 2. Elements with editable-text class
        for el in soup.select('.editable-text'):
            text = el.get_text(strip=True)
            if text and text not in seen:
                el_id = el.get('data-text', f'text-{len(texts)+1}')
                if el_id not in seen:
                    seen.add(el_id)
                    texts.append({
                        'id': el_id,
                        'text': text,
                        'type': self.get_element_type(el),
                        'customized': False
                    })
        
        # 3. Headings
        for el in soup.select('h1, h2, h3, h4, h5, h6'):
            text = el.get_text(strip=True)
            if text and len(text) > 2 and text not in seen:
                el_id = el.get('id', f'heading-{len(texts)+1}')
                if el_id not in seen:
                    seen.add(el_id)
                    texts.append({
                        'id': el_id,
                        'text': text,
                        'type': 'heading',
                        'customized': False
                    })
        
        # 4. Paragraphs
        for el in soup.select('p'):
            text = el.get_text(strip=True)
            if text and len(text) > 5 and text not in seen:
                el_id = el.get('id', f'paragraph-{len(texts)+1}')
                if el_id not in seen:
                    seen.add(el_id)
                    texts.append({
                        'id': el_id,
                        'text': text,
                        'type': 'paragraph',
                        'customized': False
                    })
        
        # 5. Buttons
        for el in soup.select('button, .btn'):
            text = el.get_text(strip=True)
            if text and len(text) > 1 and len(text) < 100 and text not in seen:
                el_id = el.get('id', f'button-{len(texts)+1}')
                if el_id not in seen:
                    seen.add(el_id)
                    texts.append({
                        'id': el_id,
                        'text': text,
                        'type': 'button',
                        'customized': False
                    })
        
        # 6. Links
        for el in soup.select('a'):
            text = el.get_text(strip=True)
            if text and len(text) > 1 and len(text) < 100 and text not in seen:
                el_id = el.get('id', f'link-{len(texts)+1}')
                if el_id not in seen:
                    seen.add(el_id)
                    texts.append({
                        'id': el_id,
                        'text': text,
                        'type': 'link',
                        'customized': False
                    })
        
        # 7. Title tag
        title = soup.find('title')
        if title:
            text = title.get_text(strip=True)
            if text:
                texts.append({
                    'id': 'page-title',
                    'text': text,
                    'type': 'title',
                    'customized': False
                })
        
        return texts
    
    def get_element_type(self, el):
        """Detect element type"""
        tag = el.name.lower() if el.name else ''
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return 'heading'
        if tag == 'button' or 'btn' in el.get('class', []):
            return 'button'
        if tag == 'a':
            return 'link'
        if tag == 'p':
            return 'paragraph'
        return 'text'
    
    def export_copy(self, template_name, export_path):
        """Export template copy to JSON file"""
        json_path = Path(settings.BASE_DIR) / 'builder' / 'copywriting' / 'templates' / f'{template_name}.json'
        
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ No copy data found for "{template_name}"'))
            self.stdout.write('   Run: python manage.py extract_copy --template ' + template_name)
            return
        
        import shutil
        shutil.copy(json_path, export_path)
        self.stdout.write(self.style.SUCCESS(f'✅ Exported to: {export_path}'))
    
    def import_copy(self, template_name, import_file):
        """Import copy from JSON file"""
        import_path = Path(import_file)
        
        if not import_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ File not found: {import_file}'))
            return
        
        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        output_dir = Path(settings.BASE_DIR) / 'builder' / 'copywriting' / 'templates'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f'{template_name}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Imported to: {output_file}'))
    
    def generate_prompt(self, template_name):
        """Generate AI prompt for the template"""
        json_path = Path(settings.BASE_DIR) / 'builder' / 'copywriting' / 'templates' / f'{template_name}.json'
        
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ No copy data found for "{template_name}"'))
            self.stdout.write('   Run: python manage.py extract_copy --template ' + template_name)
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        prompt = self.build_ai_prompt(data)
        
        # Save prompt to file
        prompt_dir = Path(settings.BASE_DIR) / 'builder' / 'copywriting' / 'prompts'
        prompt_dir.mkdir(parents=True, exist_ok=True)
        prompt_file = prompt_dir / f'{template_name}_prompt.txt'
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Prompt saved to: {prompt_file}'))
        self.stdout.write('\n' + prompt[:500] + '...\n')
    
    def build_ai_prompt(self, data):
        """Build AI prompt from copy data"""
        prompt = """# AI Copywriting Assistant

## Instructions
Rewrite the following text to be more engaging, professional, and persuasive.
Keep the same structure and element IDs.

## Current Content

"""
        for page_name, page_texts in data.get('pages', {}).items():
            prompt += f"\n### Page: {page_name}\n\n"
            for text in page_texts:
                prompt += f"[data-text=\"{text['id']}\"]\n"
                prompt += f"Current: \"{text['text']}\"\n\n"
        
        prompt += "\n## Rewritten Content\n\n"
        prompt += "[Provide rewritten text here, maintaining the same data-text IDs]\n"
        
        return prompt
    
    def process_all_templates(self):
        """Extract all templates"""
        templates_path = Path(settings.BASE_DIR) / 'templates' / 'builder' / 'templates'
        
        if not templates_path.exists():
            templates_path = Path(settings.BASE_DIR) / 'builder' / 'templates'
        
        if not templates_path.exists():
            self.stdout.write(self.style.ERROR('❌ Templates directory not found'))
            return
        
        self.stdout.write('📂 Processing all templates...\n')
        
        for template_dir in templates_path.iterdir():
            if template_dir.is_dir():
                self.stdout.write('=' * 50)
                self.extract_template(template_dir.name)