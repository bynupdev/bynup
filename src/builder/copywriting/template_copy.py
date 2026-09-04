# builder/copywriting/template_copy.py

import os
import json
import re
from pathlib import Path
from django.conf import settings
from datetime import datetime
from bs4 import BeautifulSoup

class TemplateCopyManager:
    """Manages copywriting content for templates"""
    
    def __init__(self):
        self.copy_dir = Path(settings.BASE_DIR) / 'builder' / 'copywriting' / 'templates'
        self.copy_dir.mkdir(parents=True, exist_ok=True)
        self.template_files = {}
    
    def get_template_copy_path(self, template_name):
        """Get the path for a template's copy file"""
        return self.copy_dir / f'{template_name}.json'
    
    def extract_template_text(self, template_name, html_content):
        """Extract all editable text from template HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        text_data = {
            'template': template_name,
            'extracted_at': datetime.now().isoformat(),
            'pages': {},
            'components': {},
            'global_texts': [],
            'metadata': {
                'total_elements': 0,
                'pages_count': 0,
                'components_count': 0
            }
        }
        
        # Find ALL editable text elements
        elements = []
        processed_ids = set()
        
        # 1. Find elements with data-text attribute
        for el in soup.select('[data-text]'):
            text = el.get_text(strip=True)
            data_text = el.get('data-text', '')
            if text and data_text and data_text not in processed_ids:
                processed_ids.add(data_text)
                elements.append({
                    'id': data_text,
                    'text': text,
                    'type': self._detect_element_type(el),
                    'context': self._get_element_context(el),
                    'attributes': {
                        'tag': el.name,
                        'classes': ' '.join(el.get('class', [])),
                        'id': el.get('id', '')
                    },
                    'customized': False
                })
        
        # 2. Find elements with editable-text class
        for el in soup.select('.editable-text'):
            text = el.get_text(strip=True)
            if text and not el.get('data-text'):
                # Check if already captured by text content
                already_captured = False
                for e in elements:
                    if e.get('text') == text[:50]:
                        already_captured = True
                        break
                if not already_captured:
                    idx = len(elements) + 1
                    element_id = f'text-{idx}'
                    elements.append({
                        'id': element_id,
                        'text': text,
                        'type': self._detect_element_type(el),
                        'context': self._get_element_context(el),
                        'attributes': {
                            'tag': el.name,
                            'classes': ' '.join(el.get('class', [])),
                            'id': el.get('id', '')
                        },
                        'customized': False
                    })
        
        # 3. Find elements with contenteditable
        for el in soup.select('[contenteditable="true"]'):
            text = el.get_text(strip=True)
            if text:
                idx = len(elements) + 1
                element_id = f'editable-{idx}'
                # Check if already captured
                already_captured = False
                for e in elements:
                    if e.get('text') == text[:50]:
                        already_captured = True
                        break
                if not already_captured:
                    elements.append({
                        'id': element_id,
                        'text': text,
                        'type': self._detect_element_type(el),
                        'context': self._get_element_context(el),
                        'attributes': {
                            'tag': el.name,
                            'classes': ' '.join(el.get('class', [])),
                            'id': el.get('id', '')
                        },
                        'customized': False
                    })
        
        # 4. Find heading tags that might be editable
        for el in soup.select('h1, h2, h3, h4, h5, h6'):
            text = el.get_text(strip=True)
            if text and len(text) > 2:
                # Check if already captured
                already_captured = False
                for e in elements:
                    if e.get('text') == text:
                        already_captured = True
                        break
                if not already_captured:
                    idx = len(elements) + 1
                    element_id = f'heading-{idx}'
                    elements.append({
                        'id': element_id,
                        'text': text,
                        'type': 'heading',
                        'context': self._get_element_context(el),
                        'attributes': {
                            'tag': el.name,
                            'classes': ' '.join(el.get('class', [])),
                            'id': el.get('id', '')
                        },
                        'customized': False
                    })
        
        # 5. Find paragraph text that might be editable
        for el in soup.select('p, .text, .description, .content, .subtitle, .hero-text'):
            text = el.get_text(strip=True)
            if text and len(text) > 5:
                # Check if already captured
                already_captured = False
                for e in elements:
                    if e.get('text') == text:
                        already_captured = True
                        break
                if not already_captured:
                    idx = len(elements) + 1
                    element_id = f'paragraph-{idx}'
                    elements.append({
                        'id': element_id,
                        'text': text[:500],
                        'type': 'paragraph',
                        'context': self._get_element_context(el),
                        'attributes': {
                            'tag': el.name,
                            'classes': ' '.join(el.get('class', [])),
                            'id': el.get('id', '')
                        },
                        'customized': False
                    })
        
        # 6. Find button text
        for el in soup.select('button, .btn, .button, [role="button"]'):
            text = el.get_text(strip=True)
            if text and len(text) > 1 and len(text) < 100:
                # Check if already captured
                already_captured = False
                for e in elements:
                    if e.get('text') == text:
                        already_captured = True
                        break
                if not already_captured:
                    idx = len(elements) + 1
                    element_id = f'button-{idx}'
                    elements.append({
                        'id': element_id,
                        'text': text,
                        'type': 'button',
                        'context': self._get_element_context(el),
                        'attributes': {
                            'tag': el.name,
                            'classes': ' '.join(el.get('class', [])),
                            'id': el.get('id', '')
                        },
                        'customized': False
                    })
        
        # 7. Find link text
        for el in soup.select('a:not([href^="#"]):not([href^="javascript"])'):
            text = el.get_text(strip=True)
            if text and len(text) > 1 and len(text) < 100:
                # Check if already captured
                already_captured = False
                for e in elements:
                    if e.get('text') == text:
                        already_captured = True
                        break
                if not already_captured:
                    idx = len(elements) + 1
                    element_id = f'link-{idx}'
                    elements.append({
                        'id': element_id,
                        'text': text,
                        'type': 'link',
                        'context': self._get_element_context(el),
                        'attributes': {
                            'tag': el.name,
                            'classes': ' '.join(el.get('class', [])),
                            'id': el.get('id', '')
                        },
                        'customized': False
                    })
        
        # 8. Find editable sections that might contain text
        for section in soup.select('.editable-section, [data-section], section, .section'):
            # Get direct text children (not inside other editable elements)
            direct_text = section.get_text(strip=True)
            if direct_text and len(direct_text) > 20:
                # Check if this section has editable children already
                has_editable_children = bool(section.select('.editable-text, [data-text]'))
                if not has_editable_children:
                    section_id = section.get('data-section', '') or section.get('id', '')
                    if section_id:
                        # Check if already captured
                        already_captured = False
                        for e in elements:
                            if e.get('id') == f'section-{section_id}':
                                already_captured = True
                                break
                        if not already_captured:
                            elements.append({
                                'id': f'section-{section_id}',
                                'text': direct_text[:500],
                                'type': 'section',
                                'context': '',
                                'attributes': {
                                    'tag': section.name,
                                    'classes': ' '.join(section.get('class', [])),
                                    'id': section.get('id', '')
                                },
                                'customized': False
                            })
        
        # 9. Find placeholder text in inputs
        for el in soup.select('input[placeholder], textarea[placeholder]'):
            placeholder = el.get('placeholder', '')
            if placeholder and len(placeholder) > 2:
                idx = len(elements) + 1
                element_id = f'placeholder-{idx}'
                elements.append({
                    'id': element_id,
                    'text': placeholder,
                    'type': 'placeholder',
                    'context': f'Input field: {el.get("name", "")}',
                    'attributes': {
                        'tag': el.name,
                        'placeholder': placeholder,
                        'id': el.get('id', '')
                    },
                    'customized': False
                })
        
        # 10. Find title and meta description
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            if title_text:
                elements.append({
                    'id': 'page-title',
                    'text': title_text,
                    'type': 'title',
                    'context': 'Page Title',
                    'attributes': {
                        'tag': 'title'
                    },
                    'customized': False
                })
        
        # Add to page data
        text_data['pages'][template_name] = elements
        text_data['global_texts'] = elements
        text_data['metadata']['total_elements'] = len(elements)
        text_data['metadata']['pages_count'] = 1
        
        return text_data
    
    def _detect_element_type(self, element):
        """Detect the type of text element"""
        tag = element.name.lower() if element.name else ''
        classes = ' '.join(element.get('class', [])).lower()
        
        # Heading detection
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return 'heading'
        
        # Button detection
        if tag == 'button' or 'btn' in classes or 'button' in classes:
            return 'button'
        
        # Link detection
        if tag == 'a':
            return 'link'
        
        # Paragraph detection
        if tag == 'p':
            return 'paragraph'
        
        # Title detection
        if 'title' in classes or 'heading' in classes:
            return 'title'
        
        # Hero text
        if 'hero' in classes:
            return 'hero'
        
        # Subtitle
        if 'subtitle' in classes:
            return 'subtitle'
        
        # Default
        return 'text'
    
    def _get_element_context(self, element):
        """Get context around an element"""
        context_parts = []
        
        # Get parent section
        parent_section = element.find_parent(['[data-section]', '.section', 'section'])
        if parent_section:
            section_id = parent_section.get('data-section', '') or parent_section.get('id', '')
            if section_id:
                context_parts.append(f'Section: {section_id}')
        
        # Get parent container
        parent_container = element.find_parent(['.container', '.wrapper'])
        if parent_container:
            container_class = ' '.join(parent_container.get('class', []))
            if container_class:
                context_parts.append(f'Container: {container_class}')
        
        # Get nearby headings
        prev_heading = element.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if prev_heading:
            heading_text = prev_heading.get_text(strip=True)[:50]
            context_parts.append(f'Near heading: {heading_text}')
        
        return ' | '.join(context_parts) if context_parts else 'No context'
    
    def save_template_copy(self, template_name, text_data):
        """Save extracted text data to file"""
        file_path = self.get_template_copy_path(template_name)
        
        # Add metadata
        text_data['saved_at'] = datetime.now().isoformat()
        text_data['file_version'] = '1.0'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(text_data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def load_template_copy(self, template_name):
        """Load saved copy data for a template"""
        file_path = self.get_template_copy_path(template_name)
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_templates_copy(self):
        """Get copy data for all templates"""
        all_copy = {}
        for file_path in self.copy_dir.glob('*.json'):
            template_name = file_path.stem
            all_copy[template_name] = self.load_template_copy(template_name)
        return all_copy
    
    def apply_custom_copy(self, template_name, copy_data):
        """Apply custom copy to template"""
        # Validate the copy data
        if not self._validate_copy_data(copy_data):
            raise ValueError("Invalid copy data format")
        
        # Save the custom copy
        file_path = self.get_template_copy_path(template_name)
        
        # Check if original exists
        original = self.load_template_copy(template_name)
        
        # Merge with custom data
        if original:
            # Update only the text fields
            for page_name, page_texts in copy_data.get('pages', {}).items():
                if page_name in original.get('pages', {}):
                    # Update existing page texts
                    for new_text in page_texts:
                        for original_text in original['pages'][page_name]:
                            if original_text['id'] == new_text['id']:
                                original_text['text'] = new_text['text']
                                original_text['customized'] = True
                                original_text['customized_at'] = datetime.now().isoformat()
            
            original['last_modified'] = datetime.now().isoformat()
            original['custom_version'] = original.get('custom_version', 0) + 1
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(original, f, indent=2, ensure_ascii=False)
            
            return original
        else:
            # Save as new copy
            copy_data['custom_version'] = 1
            copy_data['created_at'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(copy_data, f, indent=2, ensure_ascii=False)
            
            return copy_data
    
    def _validate_copy_data(self, copy_data):
        """Validate copy data structure"""
        required_keys = ['pages']
        for key in required_keys:
            if key not in copy_data:
                return False
        
        # Check pages structure
        for page_name, page_texts in copy_data.get('pages', {}).items():
            if not isinstance(page_texts, list):
                return False
            for text in page_texts:
                if 'id' not in text or 'text' not in text:
                    return False
        
        return True
    
    def export_to_json(self, template_name):
        """Export template copy as JSON string"""
        data = self.load_template_copy(template_name)
        if data:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return None
    
    def import_from_json(self, template_name, json_data):
        """Import copy from JSON string"""
        try:
            data = json.loads(json_data)
            return self.apply_custom_copy(template_name, data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    def generate_ai_prompt(self, template_name, context_instructions=None):
        """Generate AI prompt from template copy"""
        data = self.load_template_copy(template_name)
        if not data:
            return None
        
        prompt = self._build_ai_prompt(data, context_instructions)
        return prompt
    
    def _build_ai_prompt(self, data, context_instructions=None):
        """Build the AI prompt from copy data"""
        prompt = """# AI Copywriting Assistant\n\n"""
        prompt += f"## Template: {data.get('template', 'Unknown')}\n"
        prompt += f"## Extracted At: {data.get('extracted_at', 'Unknown')}\n\n"
        
        if context_instructions:
            prompt += f"## User Instructions\n{context_instructions}\n\n"
        
        prompt += """## Instructions for AI
You are an expert copywriter. Rewrite the following text to be:
1. More engaging and persuasive
2. Better aligned with the brand voice
3. Clearer and more concise
4. SEO-friendly
5. Action-oriented (especially for CTAs)

Keep the same structure and element IDs. Provide the rewritten text in the same format.
\n"""
        
        prompt += "## Current Content\n\n"
        
        # Add pages
        for page_name, page_texts in data.get('pages', {}).items():
            prompt += f"### Page: {page_name}\n\n"
            
            # Group by type
            grouped = {}
            for text in page_texts:
                type_key = text.get('type', 'text')
                if type_key not in grouped:
                    grouped[type_key] = []
                grouped[type_key].append(text)
            
            for type_key, texts in grouped.items():
                prompt += f"#### {type_key.capitalize()}s\n\n"
                for text in texts:
                    prompt += f"[data-text=\"{text['id']}\"]\n"
                    prompt += f"Current: \"{text['text']}\"\n"
                    if text.get('context'):
                        prompt += f"Context: {text['context']}\n"
                    prompt += "\n"
        
        prompt += "## Rewritten Content\n\n"
        prompt += "[Provide rewritten text here, maintaining the same data-text IDs]\n\n"
        
        return prompt