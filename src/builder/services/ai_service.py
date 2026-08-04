# builder/services/ai_service.py

import json
import os
import re
import random
from django.conf import settings
from openai import OpenAI

# ============================================
# JSON REPAIR UTILITY
# ============================================

def repair_json(json_string):
    if not json_string:
        return None
    
    text = json_string.strip()
    
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0].strip()
    elif '```' in text:
        text = text.split('```')[1].split('```')[0].strip()
    
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        text = json_match.group(0)
    
    repairs = [
        (r',\s*}', '}'),
        (r',\s*]', ']'),
        (r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":'),
        (r'}\s*{', '},{'),
        (r"'([^']*)'", r'"\1"'),
        (r'(?<!")\\n(?=")', '\\n'),
        (r'(?<!")\n(?=")', '\\n'),
    ]
    
    for pattern, replacement in repairs:
        if callable(replacement):
            text = re.sub(pattern, replacement, text)
        else:
            text = re.sub(pattern, replacement, text)
    
    lines = text.split('\n')
    fixed_lines = []
    in_string = False
    
    for line in lines:
        quote_count = len(re.findall(r'(?<!\\)"', line))
        
        if in_string:
            if quote_count % 2 == 1:
                in_string = False
                fixed_lines.append(line)
            else:
                fixed_lines.append(line + '"')
                in_string = False
        else:
            if quote_count % 2 == 1:
                in_string = True
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
    
    text = '\n'.join(fixed_lines)
    
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')
    
    if open_braces > 0:
        text += '}' * open_braces
    if open_brackets > 0:
        text += ']' * open_brackets
    
    try:
        data = json.loads(text)
        return data
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON repair failed: {e}")
        try:
            match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return data
        except:
            pass
        return None


# ============================================
# OPENROUTER CLIENT
# ============================================

class OpenRouterClient:
    def __init__(self):
        api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in settings")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": getattr(settings, 'SITE_URL', 'http://localhost:8000'),
                "X-Title": "AI Website Builder"
            }
        )
        
        self.primary_models = [
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "anthropic/claude-3.5-sonnet",
            "meta-llama/llama-3.2-3b-instruct",
            "google/gemini-2.0-flash-exp:free",
        ]
        
        self.fallback_models = [
            "mistralai/mistral-7b-instruct:free",
            "meta-llama/llama-3.2-1b-instruct",
            "google/gemini-flash-1.5",
        ]
        
        self.tried_models = set()
    
    def generate(self, prompt, max_tokens=4000, temperature=0.9):
        last_error = None
        
        for model in self.primary_models:
            if model in self.tried_models:
                continue
                
            try:
                print(f"🔄 Trying OpenRouter model: {model}")
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a senior web designer at a top-tier design agency. Output only valid JSON with professional, production-ready designs."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9,
                )
                
                response_text = completion.choices[0].message.content
                self.tried_models.add(model)
                
                if response_text and len(response_text) > 100:
                    print(f"✅ Model {model} succeeded ({len(response_text)} chars)")
                    return response_text, model
                else:
                    print(f"⚠️ Model {model} returned empty/too short response")
                    continue
                    
            except Exception as e:
                error_msg = str(e).lower()
                print(f"⚠️ Model {model} failed: {error_msg[:100]}")
                
                if "quota" in error_msg or "rate" in error_msg or "limit" in error_msg:
                    print(f"⏳ Quota/rate limit on {model}, trying next...")
                    last_error = error_msg
                    continue
                elif "402" in error_msg or "credits" in error_msg or "insufficient" in error_msg:
                    print(f"💰 Model {model} needs credits, trying next...")
                    last_error = error_msg
                    continue
                    
                last_error = error_msg
                continue
        
        print("🔄 Primary models exhausted, trying fallback models...")
        for model in self.fallback_models:
            if model in self.tried_models:
                continue
                
            try:
                print(f"🔄 Trying fallback model: {model}")
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional web designer. Output only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens // 2,
                    temperature=temperature,
                    top_p=0.9,
                )
                
                response_text = completion.choices[0].message.content
                self.tried_models.add(model)
                
                if response_text and len(response_text) > 50:
                    print(f"✅ Fallback model {model} succeeded ({len(response_text)} chars)")
                    return response_text, model
                else:
                    print(f"⚠️ Fallback model {model} returned empty/too short response")
                    continue
                    
            except Exception as e:
                error_msg = str(e).lower()
                print(f"⚠️ Fallback model {model} failed: {error_msg[:100]}")
                last_error = error_msg
                continue
        
        raise Exception(f"All models failed. Last error: {last_error}")


# ============================================
# AI DESIGN SERVICE
# ============================================

class AIDesignService:
    def __init__(self, template_name='modernecommerce33'):
        self.template_name = template_name
        self.openrouter = None
        
        try:
            self.openrouter = OpenRouterClient()
            print(f"🚀 AI Design Service initialized with OpenRouter")
        except ValueError as e:
            print(f"⚠️ OpenRouter not configured: {e}")
            self.openrouter = None
        
        self.template_structure = self._get_fallback_structure()
        self.editable_elements = self._extract_editable_elements()
        
        print(f"   - Template: {template_name}")
        print(f"   - Text elements: {len(self.editable_elements['text_keys'])}")
        print(f"   - Sections: {len(self.editable_elements['section_keys'])}")

    def _get_fallback_structure(self):
        return {
            'pages': ['home'],
            'sections': {
                '1': {'id': '1', 'context': 'Navigation bar'},
                '2': {'id': '2', 'context': 'Brand logo'},
                '3': {'id': '3', 'context': 'Bookmarks button'},
                '4': {'id': '4', 'context': 'Cart button'},
                '5': {'id': '5', 'context': 'Account dropdown wrapper'},
                '6': {'id': '6', 'context': 'Account dropdown menu'},
                '7': {'id': '7', 'context': 'Sign Up link'},
                '8': {'id': '8', 'context': 'Sign In link'},
                '9': {'id': '9', 'context': 'Orders link'},
                '10': {'id': '10', 'context': 'Logout link'},
                '11': {'id': '11', 'context': 'Hero section'},
                '12': {'id': '12', 'context': 'Hero headline'},
                '13': {'id': '13', 'context': 'Hero context box'},
                '14': {'id': '14', 'context': 'Hero subtitle'},
                '15': {'id': '15', 'context': 'Hero description'},
                '16': {'id': '16', 'context': 'Products section title'},
                '17': {'id': '17', 'context': 'Modal size label'},
                '18': {'id': '18', 'context': 'Modal color label'},
                '19': {'id': '19', 'context': 'Reviews section title'},
                '20': {'id': '20', 'context': 'Review form label'},
                '21': {'id': '21', 'context': 'Review author input'},
                '22': {'id': '22', 'context': 'Review rating select'},
                '23': {'id': '23', 'context': 'Review text area'},
                '24': {'id': '24', 'context': 'Submit review button'},
                '25': {'id': '25', 'context': 'FAQ section'},
                '26': {'id': '26', 'context': 'FAQ title'},
                '27': {'id': '27', 'context': 'FAQ item 1 container'},
                '28': {'id': '28', 'context': 'FAQ item 1 header'},
                '29': {'id': '29', 'context': 'FAQ item 1 body'},
                '30': {'id': '30', 'context': 'FAQ item 2 container'},
                '31': {'id': '31', 'context': 'FAQ item 2 header'},
                '32': {'id': '32', 'context': 'FAQ item 2 body'},
                '33': {'id': '33', 'context': 'Cart drawer title'},
                '34': {'id': '34', 'context': 'Cart total label'},
                '35': {'id': '35', 'context': 'Checkout button'},
                '36': {'id': '36', 'context': 'Wishlist drawer title'},
                '37': {'id': '37', 'context': 'Sticky cart view button'},
                '38': {'id': '38', 'context': 'Sticky cart checkout button'},
                '40': {'id': '40', 'context': 'Contact section'},
                '41': {'id': '41', 'context': 'Contact card box'},
                '42': {'id': '42', 'context': 'Contact sidebar'},
                '43': {'id': '43', 'context': 'Contact sidebar label'},
                '44': {'id': '44', 'context': 'Contact sidebar heading'},
                '45': {'id': '45', 'context': 'Contact address'},
                '46': {'id': '46', 'context': 'Contact form container'},
                '47': {'id': '47', 'context': 'Contact name input'},
                '48': {'id': '48', 'context': 'Contact name label'},
                '49': {'id': '49', 'context': 'Contact email input'},
                '50': {'id': '50', 'context': 'Contact email label'},
                '51': {'id': '51', 'context': 'Contact message textarea'},
                '52': {'id': '52', 'context': 'Contact message label'},
                '53': {'id': '53', 'context': 'Contact submit button'},
                '54': {'id': '54', 'context': 'Footer section'},
                '55': {'id': '55', 'context': 'Footer brand section'},
                '56': {'id': '56', 'context': 'Footer logo'},
                '57': {'id': '57', 'context': 'Footer description'},
                '58': {'id': '58', 'context': 'Footer links section'},
                '59': {'id': '59', 'context': 'Footer links heading'},
                '60': {'id': '60', 'context': 'Footer link'},
                '61': {'id': '61', 'context': 'Footer copyright'},
                '62': {'id': '62', 'context': 'Footer engine text'},
                '100': {'id': '100', 'context': 'Product 1 card'},
                '101': {'id': '101', 'context': 'Product 1 tag'},
                '102': {'id': '102', 'context': 'Product 1 title'},
                '103': {'id': '103', 'context': 'Product 1 price'},
                '104': {'id': '104', 'context': 'Product 2 card'},
                '105': {'id': '105', 'context': 'Product 2 tag'},
                '106': {'id': '106', 'context': 'Product 2 title'},
                '107': {'id': '107', 'context': 'Product 2 price'},
                '108': {'id': '108', 'context': 'Product 3 card'},
                '109': {'id': '109', 'context': 'Product 3 tag'},
                '110': {'id': '110', 'context': 'Product 3 title'},
                '111': {'id': '111', 'context': 'Product 3 price'},
            },
            'text_elements': {
                '1': {'id': '1', 'context': 'Brand name'},
                '2': {'id': '2', 'context': 'Bookmarks button text'},
                '3': {'id': '3', 'context': 'Cart button text'},
                '4': {'id': '4', 'context': 'Sign Up link'},
                '5': {'id': '5', 'context': 'Sign In link'},
                '6': {'id': '6', 'context': 'Orders link'},
                '7': {'id': '7', 'context': 'Logout link'},
                '8': {'id': '8', 'context': 'Hero headline'},
                '9': {'id': '9', 'context': 'Hero subtitle'},
                '10': {'id': '10', 'context': 'Hero description'},
                '11': {'id': '11', 'context': 'Products section title'},
                '12': {'id': '12', 'context': 'Modal size label'},
                '13': {'id': '13', 'context': 'Modal color label'},
                '14': {'id': '14', 'context': 'Reviews section title'},
                '15': {'id': '15', 'context': 'Review form label'},
                '16': {'id': '16', 'context': 'Review author placeholder'},
                '17': {'id': '17', 'context': 'Review rating options'},
                '18': {'id': '18', 'context': 'Review text placeholder'},
                '19': {'id': '19', 'context': 'Submit review button'},
                '20': {'id': '20', 'context': 'FAQ title'},
                '21': {'id': '21', 'context': 'FAQ item 1 header'},
                '22': {'id': '22', 'context': 'FAQ item 1 body'},
                '23': {'id': '23', 'context': 'FAQ item 2 header'},
                '24': {'id': '24', 'context': 'FAQ item 2 body'},
                '25': {'id': '25', 'context': 'Cart drawer title'},
                '26': {'id': '26', 'context': 'Cart total label'},
                '27': {'id': '27', 'context': 'Checkout button text'},
                '28': {'id': '28', 'context': 'Wishlist drawer title'},
                '29': {'id': '29', 'context': 'Sticky cart view button'},
                '30': {'id': '30', 'context': 'Sticky cart checkout'},
                '31': {'id': '31', 'context': 'Footer brand name'},
                '32': {'id': '32', 'context': 'Footer description'},
                '33': {'id': '33', 'context': 'Footer links heading'},
                '34': {'id': '34', 'context': 'Footer link'},
                '35': {'id': '35', 'context': 'Footer copyright'},
                '36': {'id': '36', 'context': 'Footer engine text'},
                '37': {'id': '37', 'context': 'Contact sidebar label'},
                '38': {'id': '38', 'context': 'Contact sidebar heading'},
                '39': {'id': '39', 'context': 'Contact address'},
                '40': {'id': '40', 'context': 'Contact name placeholder'},
                '41': {'id': '41', 'context': 'Contact name label'},
                '42': {'id': '42', 'context': 'Contact email placeholder'},
                '43': {'id': '43', 'context': 'Contact email label'},
                '44': {'id': '44', 'context': 'Contact message placeholder'},
                '45': {'id': '45', 'context': 'Contact message label'},
                '46': {'id': '46', 'context': 'Contact submit button'},
                '100': {'id': '100', 'context': 'Product 1 tag'},
                '101': {'id': '101', 'context': 'Product 1 title'},
                '102': {'id': '102', 'context': 'Product 1 price'},
                '103': {'id': '103', 'context': 'Product 2 tag'},
                '104': {'id': '104', 'context': 'Product 2 title'},
                '105': {'id': '105', 'context': 'Product 2 price'},
                '106': {'id': '106', 'context': 'Product 3 tag'},
                '107': {'id': '107', 'context': 'Product 3 title'},
                '108': {'id': '108', 'context': 'Product 3 price'},
            }
        }

    def _extract_editable_elements(self):
        elements = {
            'text_keys': list(self.template_structure['text_elements'].keys()),
            'section_keys': list(self.template_structure['sections'].keys()),
            'text_contexts': {},
            'section_contexts': {}
        }
        for text_id, info in self.template_structure['text_elements'].items():
            elements['text_contexts'][text_id] = info.get('context', '')
        for section_id, info in self.template_structure['sections'].items():
            elements['section_contexts'][section_id] = info.get('context', '')
        return elements

    def generate_customizations(self, store_name, industry, style, palette):
        prompt = self._build_professional_prompt(store_name, industry, style, palette)
        
        if not self.openrouter:
            print("⚠️ OpenRouter not configured, using professional fallback")
            return self._get_professional_fallback(store_name, industry, style, palette)
        
        try:
            print(f"📝 Prompt size: ~{len(prompt)} chars")
            response_text, used_model = self.openrouter.generate(prompt, max_tokens=4000, temperature=0.85)
            print(f"✅ Response from {used_model} ({len(response_text)} chars)")
            
            customizations = self._parse_response(response_text)
            if customizations:
                return self._validate_and_enhance(customizations, store_name, industry, style, palette)
            else:
                raise ValueError("Failed to parse AI response")
                
        except Exception as e:
            print(f"⚠️ AI generation failed: {e}")
            print("🔄 Using professional fallback")
            return self._get_professional_fallback(store_name, industry, style, palette)

    def _build_professional_prompt(self, store_name, industry, style, palette):
        colors = self._get_professional_colors(style, palette)
        
        style_guides = {
            'minimalist': {
                'description': 'Ultra-clean, Scandinavian-inspired. Massive whitespace, thin borders, monochromatic with a single accent color. Think Acne Studios or COS.',
                'fonts': "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                'border_radius': '0px',
                'shadow': '0 1px 3px rgba(0,0,0,0.04)',
            },
            'bold': {
                'description': 'High-contrast, editorial. Dark backgrounds with neon accents. Oversized typography, glass-morphism, dramatic. Think Balenciaga or Off-White.',
                'fonts': "'Poppins', 'Inter', sans-serif",
                'border_radius': '0px',
                'shadow': '0 8px 32px rgba(0,0,0,0.2)',
            },
            'luxury': {
                'description': 'Refined, premium. Deep navies, charcoal, gold accents. Serif display fonts, generous spacing, subtle animations. Think Gucci or Cartier.',
                'fonts': "'Playfair Display', 'Georgia', serif",
                'border_radius': '4px',
                'shadow': '0 4px 24px rgba(0,0,0,0.06)',
            },
            'organic': {
                'description': 'Warm, natural, grounded. Terracotta, sage, cream. Rounded corners, flowing layouts, soft shadows. Think Patagonia or Aesop.',
                'fonts': "'Nunito', 'Inter', sans-serif",
                'border_radius': '16px',
                'shadow': '0 8px 40px rgba(0,0,0,0.04)',
            },
            'playful': {
                'description': 'Fun, approachable, creative. Bright colors, rounded everything, gradient backgrounds. Think Glossier or Canva.',
                'fonts': "'Quicksand', 'Inter', sans-serif",
                'border_radius': '24px',
                'shadow': '0 8px 40px rgba(0,0,0,0.06)',
            },
            'professional': {
                'description': 'Trustworthy, corporate, clean. Blue tones, structured grid, subtle shadows. Think Salesforce or Microsoft.',
                'fonts': "'Source Sans Pro', 'Inter', sans-serif",
                'border_radius': '6px',
                'shadow': '0 2px 12px rgba(0,0,0,0.04)',
            }
        }
        
        guide = style_guides.get(style, style_guides['professional'])
        
        return f"""
You are a senior designer at a world-class design agency. Create a professional, production-ready website design.

STORE: {store_name}
INDUSTRY: {industry}
STYLE: {style} - {guide['description']}

COLOR PALETTE (Use these exact colors):
- Primary: {colors['primary']}
- Secondary: {colors['secondary']}
- Accent: {colors['accent']}
- Background: {colors['bg']}
- Text: {colors['text']}
- Background Alt: {colors['bg_alt']}
- Muted: {colors.get('muted', '#f8f9fa')}
- Border: {colors.get('border', '#e9ecef')}

DESIGN SYSTEM:
- Font: {guide['fonts']}
- Border Radius: {guide['border_radius']}
- Shadow: {guide['shadow']}
- Transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)

CRITICAL COPYWRITING RULES:
1. Text 1 (Brand name): "{store_name}" - THIS IS THE ONLY PLACE FOR THE BRAND NAME
2. Text 2 (Bookmarks): "★" - Keep it minimal, just an icon
3. Text 3 (Cart): "🛒" - Keep it minimal, just an icon
4. Text 4-7 (Account links): Short action words only
5. Hero text (8-10): One powerful headline, one subheadline, one description
6. Products (11-19): Clean product section language
7. FAQ (20-24): Genuine questions and answers for {industry}
8. Product cards (100-108): Product tags, names, prices
9. Contact (37-46): Clean, professional contact section
10. Footer (31-36): Minimal, essential links only

Generate the complete JSON with professional text and styling.
"""

    def _get_professional_colors(self, style, palette):
        color_palettes = {
            'minimalist': {
                'primary': '#1a1a2e', 'secondary': '#16213e', 'accent': '#e94560',
                'bg': '#ffffff', 'text': '#1a1a2e', 'bg_alt': '#f8f9fa',
                'muted': '#f1f3f5', 'border': '#e9ecef'
            },
            'bold': {
                'primary': '#0d0d0d', 'secondary': '#1a1a2e', 'accent': '#ff006e',
                'bg': '#0d0d0d', 'text': '#ffffff', 'bg_alt': '#1a1a2e',
                'muted': '#2a2a3a', 'border': '#333344'
            },
            'luxury': {
                'primary': '#0a0a0a', 'secondary': '#1a1a1a', 'accent': '#c9a959',
                'bg': '#fcf8f4', 'text': '#0a0a0a', 'bg_alt': '#f5f0e8',
                'muted': '#edf0f5', 'border': '#e8e0d5'
            },
            'organic': {
                'primary': '#2d5a27', 'secondary': '#4a7a44', 'accent': '#d4877a',
                'bg': '#fcf8f4', 'text': '#2d3a2d', 'bg_alt': '#f5ede4',
                'muted': '#f0ece4', 'border': '#e8e0d5'
            },
            'playful': {
                'primary': '#ff6b6b', 'secondary': '#ffd93d', 'accent': '#6bcb77',
                'bg': '#fffcf5', 'text': '#2d2d2d', 'bg_alt': '#fff5f0',
                'muted': '#faf0ea', 'border': '#f5e8e0'
            },
            'professional': {
                'primary': '#1e3a5f', 'secondary': '#2d5a7a', 'accent': '#4a7a9a',
                'bg': '#ffffff', 'text': '#1a2a3a', 'bg_alt': '#f5f8fa',
                'muted': '#e8eef2', 'border': '#dee7f2'
            }
        }
        
        palette_map = {
            'corporate_trust': {'primary': '#4361ee', 'secondary': '#3a0ca3', 'accent': '#f72585'},
            'vibrant_modern': {'primary': '#ff006e', 'secondary': '#fbb13c', 'accent': '#3b9e9e'},
            'luxury_gold': {'primary': '#0b0c10', 'secondary': '#c6a15b', 'accent': '#fff8e7'},
            'nature_inspired': {'primary': '#2d5a27', 'secondary': '#606c38', 'accent': '#d4d8b3'},
        }
        
        base = color_palettes.get(style, color_palettes['professional'])
        
        if palette in palette_map:
            custom = palette_map[palette]
            base['primary'] = custom.get('primary', base['primary'])
            base['secondary'] = custom.get('secondary', base['secondary'])
            base['accent'] = custom.get('accent', base['accent'])
        
        return base

    def _parse_response(self, response_text):
        try:
            text = response_text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            return json.loads(text)
        except json.JSONDecodeError:
            print("⚠️ Initial JSON parse failed, attempting repair...")
            repaired = repair_json(response_text)
            if repaired:
                return repaired
            return None

    def _validate_and_enhance(self, customizations, store_name, industry, style, palette):
        if not customizations:
            return self._get_professional_fallback(store_name, industry, style, palette)
        
        if 'home' not in customizations:
            customizations = {'home': customizations}
        
        if 'text_contents' not in customizations['home']:
            customizations['home']['text_contents'] = {}
        
        if 'style_customizations' not in customizations['home']:
            customizations['home']['style_customizations'] = {}
        
        fallback = self._get_professional_fallback(store_name, industry, style, palette)
        
        for text_id in self.editable_elements['text_keys']:
            current = customizations['home']['text_contents'].get(text_id, '')
            if not current or current.strip() == '' or current.startswith('Text '):
                customizations['home']['text_contents'][text_id] = fallback['home']['text_contents'].get(text_id, '')
                print(f"📝 Enhanced text {text_id}")
        
        for section_id in self.editable_elements['section_keys']:
            if section_id not in customizations['home']['style_customizations']:
                customizations['home']['style_customizations'][section_id] = fallback['home']['style_customizations'].get(section_id, {})
                print(f"🎨 Enhanced style for section {section_id}")
            else:
                style_props = customizations['home']['style_customizations'][section_id]
                if 'custom_css' not in style_props:
                    style_props['custom_css'] = ''
                if 'background_color' not in style_props:
                    style_props['background_color'] = fallback['home']['style_customizations'].get(section_id, {}).get('background_color', '#ffffff')
                if 'text_color' not in style_props:
                    style_props['text_color'] = fallback['home']['style_customizations'].get(section_id, {}).get('text_color', '#000000')
                if 'font_family' not in style_props:
                    style_props['font_family'] = fallback['home']['style_customizations'].get(section_id, {}).get('font_family', "'Inter', sans-serif")
                if 'padding' not in style_props:
                    style_props['padding'] = '0px'
        
        return customizations

    def _get_professional_fallback(self, store_name, industry, style, palette):
        """Generate a professional, production-ready fallback design"""
        colors = self._get_professional_colors(style, palette)
        p = colors['primary']
        s = colors['secondary']
        a = colors['accent']
        bg = colors['bg']
        t = colors['text']
        bg_alt = colors['bg_alt']
        muted = colors.get('muted', '#f8f9fa')
        border = colors.get('border', '#e9ecef')
        
        fonts = {
            'minimalist': "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            'bold': "'Poppins', 'Inter', sans-serif",
            'luxury': "'Playfair Display', 'Georgia', serif",
            'organic': "'Nunito', 'Inter', sans-serif",
            'playful': "'Quicksand', 'Inter', sans-serif",
            'professional': "'Source Sans Pro', 'Inter', sans-serif"
        }
        font = fonts.get(style, fonts['professional'])
        
        radii = {
            'minimalist': '0px',
            'bold': '0px',
            'luxury': '4px',
            'organic': '16px',
            'playful': '24px',
            'professional': '6px'
        }
        radius = radii.get(style, '6px')
        
        industry_content = self._get_industry_content(store_name, industry)
        
        # Build professional text content
        text_contents = {
            # Navigation - Clean and minimal
            '1': store_name,
            '2': '★',
            '3': '🛒',
            '4': 'Sign Up',
            '5': 'Sign In',
            '6': 'Orders',
            '7': 'Logout',
            
            # Hero - Professional copy
            '8': industry_content['headline'],
            '9': industry_content['subheadline'],
            '10': industry_content['description'],
            
            # Products section
            '11': industry_content['products_title'],
            '12': 'Size:',
            '13': 'Color:',
            '14': 'Reviews',
            '15': 'Write a Review',
            '16': 'Your Name',
            '17': '★★★★★',
            '18': 'Share your experience...',
            '19': 'Submit Review',
            
            # FAQ
            '20': 'Frequently Asked Questions',
            '21': industry_content['faq1_q'],
            '22': industry_content['faq1_a'],
            '23': industry_content['faq2_q'],
            '24': industry_content['faq2_a'],
            
            # Drawers
            '25': 'Your Cart',
            '26': 'Total:',
            '27': 'Checkout →',
            '28': 'Your Wishlist',
            
            # Sticky cart
            '29': 'View Cart',
            '30': 'Checkout →',
            
            # Contact
            '37': 'Contact',
            '38': 'Get in Touch',
            '39': f'{store_name}\n123 Main Street\nCity, State 10001\nhello@{store_name.lower().replace(" ", "")}.com',
            '40': 'Your Name',
            '41': 'Your Name',
            '42': 'Your Email',
            '43': 'Your Email',
            '44': 'Your Message',
            '45': 'Your Message',
            '46': 'Send Message',
            
            # Footer
            '31': store_name,
            '32': industry_content['footer_tagline'],
            '33': 'Explore',
            '34': 'Back to Top ↑',
            '35': f'© 2026 {store_name}. All rights reserved.',
            '36': 'v3.0 | Design Studio',
            
            # Product cards
            '100': 'ICONIC',
            '101': industry_content['product1_name'],
            '102': industry_content['product1_price'],
            '103': 'ESSENTIAL',
            '104': industry_content['product2_name'],
            '105': industry_content['product2_price'],
            '106': 'BASIC',
            '107': industry_content['product3_name'],
            '108': industry_content['product3_price'],
        }
        
        # Build professional CSS for each section - ESCAPED PROPERLY
        style_customizations = {}
        
        # 1. Navigation CSS
        nav_css = f"""
        & {{
            background: {bg if style == 'minimalist' else p} !important;
            padding: 16px 5% !important;
            border-bottom: 1px solid {border} !important;
            backdrop-filter: blur(12px) !important;
            position: sticky !important;
            top: 0 !important;
            z-index: 1000 !important;
        }}
        & .brand-crest {{
            color: {t if style == 'minimalist' else bg} !important;
            font-size: 1.6rem !important;
            font-weight: {'700' if style == 'minimalist' else '600'} !important;
            letter-spacing: {'2px' if style == 'luxury' else '-0.5px'} !important;
            text-transform: uppercase !important;
            font-family: {font} !important;
        }}
        & .pill-action-btn {{
            background: transparent !important;
            border: 1px solid {t if style == 'minimalist' else bg} !important;
            color: {t if style == 'minimalist' else bg} !important;
            padding: 8px 20px !important;
            border-radius: {radius} !important;
            font-weight: 500 !important;
            font-size: 0.75rem !important;
            text-transform: {'none' if style == 'organic' else 'uppercase'} !important;
            transition: all 0.3s ease !important;
            font-family: {font} !important;
        }}
        & .pill-action-btn:hover {{
            background: {a} !important;
            border-color: {a} !important;
            color: {bg} !important;
            transform: translateY(-2px) !important;
        }}
        & .pill-action-btn:first-of-type {{
            background: {a} !important;
            border-color: {a} !important;
            color: {bg} !important;
        }}
        & .pill-action-btn:first-of-type:hover {{
            background: {p} !important;
            border-color: {p} !important;
        }}
        """
        
        for section_id in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
            style_customizations[section_id] = {
                'background_color': bg if style == 'minimalist' else p,
                'text_color': t if style == 'minimalist' else bg,
                'font_family': font,
                'padding': '0px',
                'custom_css': nav_css
            }

        # 2. Hero CSS
        hero_css = f"""
        & {{
            background: linear-gradient(135deg, {p} 0%, {s} 100%) !important;
            padding: 100px 5% !important;
            position: relative !important;
            overflow: hidden !important;
            min-height: 65vh !important;
            display: flex !important;
            align-items: center !important;
        }}
        &::before {{
            content: '' !important;
            position: absolute !important;
            top: -50% !important;
            right: -20% !important;
            width: 70% !important;
            height: 200% !important;
            background: radial-gradient(ellipse, {a}15 0%, transparent 70%) !important;
            pointer-events: none !important;
        }}
        & h1 {{
            font-size: clamp(2.8rem, 6vw, 4.8rem) !important;
            font-weight: {'300' if style == 'luxury' else '800'} !important;
            color: {bg} !important;
            text-shadow: 0 2px 40px rgba(0,0,0,0.2) !important;
            letter-spacing: {'-1px' if style == 'minimalist' else '0'} !important;
            line-height: 1.1 !important;
            font-family: {font} !important;
            position: relative !important;
            z-index: 1 !important;
        }}
        & em {{
            color: {a} !important;
            font-style: italic !important;
        }}
        & .intro-context-box {{
            background: rgba(0,0,0,0.25) !important;
            backdrop-filter: blur(16px) !important;
            border: 1px solid {a}40 !important;
            border-radius: {radius} !important;
            padding: 40px !important;
            position: relative !important;
            z-index: 1 !important;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15) !important;
        }}
        & h3 {{
            color: {a} !important;
            font-size: 1.6rem !important;
            font-weight: {'300' if style == 'luxury' else '700'} !important;
            font-family: {font} !important;
        }}
        & p {{
            color: {bg}cc !important;
            font-size: 1.15rem !important;
            line-height: 1.8 !important;
            font-family: {font} !important;
        }}
        """
        
        for section_id in ['11', '12', '13', '14', '15']:
            style_customizations[section_id] = {
                'background_color': p,
                'text_color': bg,
                'font_family': font,
                'padding': '0px',
                'custom_css': hero_css
            }

        # 3. Products Section CSS
        products_section_css = f"""
        & .chambers-grid-title {{
            color: {p} !important;
            font-size: clamp(2.2rem, 3.5vw, 3.2rem) !important;
            font-weight: {'300' if style == 'luxury' else '700'} !important;
            text-align: center !important;
            margin: 60px 0 40px !important;
            letter-spacing: {'4px' if style == 'luxury' else '1px'} !important;
            text-transform: {'none' if style == 'organic' else 'uppercase'} !important;
            font-family: {font} !important;
        }}
        & .chambers-grid-title::after {{
            content: '' !important;
            display: block !important;
            width: 60px !important;
            height: 3px !important;
            background: {a} !important;
            margin: 20px auto !important;
            border-radius: 2px !important;
        }}
        """
        
        for section_id in ['16', '17', '18', '19', '20', '21', '22', '23', '24']:
            style_customizations[section_id] = {
                'background_color': bg,
                'text_color': t,
                'font_family': font,
                'padding': '0px',
                'custom_css': products_section_css
            }

        # 4. Product Cards CSS
        product_card_css = f"""
        & .chamber-card-node {{
            background: {bg} !important;
            border: 1px solid {border} !important;
            border-radius: {radius} !important;
            padding: 24px !important;
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.02) !important;
        }}
        & .chamber-card-node:hover {{
            transform: translateY(-8px) !important;
            border-color: {a} !important;
            box-shadow: 0 20px 48px rgba(0,0,0,0.06) !important;
        }}
        & .chamber-portal-circle {{
            width: 100% !important;
            height: 240px !important;
            border-radius: {radius} !important;
            overflow: hidden !important;
            margin-bottom: 20px !important;
            border: 1px solid {border} !important;
        }}
        & .chamber-portal-circle img {{
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
            transition: transform 0.6s ease !important;
        }}
        & .chamber-card-node:hover .chamber-portal-circle img {{
            transform: scale(1.05) !important;
        }}
        & .chamber-tag {{
            color: {a} !important;
            font-weight: 600 !important;
            font-size: 0.65rem !important;
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
            padding: 4px 12px !important;
            border-radius: 20px !important;
            border: 1px solid {a}40 !important;
            font-family: {font} !important;
            display: inline-block !important;
        }}
        & .chamber-title {{
            color: {t} !important;
            font-size: 1.3rem !important;
            font-weight: {'300' if style == 'luxury' else '600'} !important;
            margin: 12px 0 8px !important;
            font-family: {font} !important;
        }}
        & .chamber-price {{
            color: {a} !important;
            font-size: 1.5rem !important;
            font-weight: {'300' if style == 'luxury' else '700'} !important;
            font-family: {font} !important;
        }}
        & .chamber-save-bookmark {{
            background: {bg} !important;
            border: 1px solid {border} !important;
            color: {t} !important;
            transition: all 0.3s ease !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
        }}
        & .chamber-save-bookmark:hover {{
            background: {a} !important;
            color: {bg} !important;
            border-color: {a} !important;
        }}
        """
        
        for section_id in ['100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111']:
            style_customizations[section_id] = {
                'background_color': bg,
                'text_color': t,
                'font_family': font,
                'padding': '0px',
                'custom_css': product_card_css
            }

        # 5. FAQ CSS
        faq_css = f"""
        & .reassurance-header-btn {{
            color: {p} !important;
            font-size: 1.2rem !important;
            font-weight: 500 !important;
            padding: 20px 0 !important;
            border-bottom: 1px solid {border} !important;
            transition: all 0.3s ease !important;
            font-family: {font} !important;
            background: none !important;
            width: 100% !important;
            text-align: left !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
        }}
        & .reassurance-header-btn:hover {{
            color: {a} !important;
            border-bottom-color: {a} !important;
        }}
        & .reassurance-header-btn i {{
            transition: transform 0.3s ease !important;
            color: {a} !important;
        }}
        & .reassurance-body-drawer {{
            color: {t} !important;
            font-size: 1rem !important;
            line-height: 1.8 !important;
            padding: 20px 0 !important;
            font-family: {font} !important;
        }}
        & .reassurance-body-drawer p {{
            background: {bg_alt} !important;
            padding: 20px !important;
            border-radius: {radius} !important;
            border-left: 3px solid {a} !important;
        }}
        """
        
        for section_id in ['25', '26', '27', '28', '29', '30', '31', '32']:
            style_customizations[section_id] = {
                'background_color': bg,
                'text_color': t,
                'font_family': font,
                'padding': '0px',
                'custom_css': faq_css
            }

        # 6. Drawers CSS
        drawer_css = f"""
        & .chambers-drawer {{
            background: {bg} !important;
            border-left: 1px solid {border} !important;
            padding: 40px !important;
            box-shadow: -20px 0 60px rgba(0,0,0,0.04) !important;
        }}
        & .drawer-title-row {{
            color: {t} !important;
            font-size: 1.8rem !important;
            font-weight: {'300' if style == 'luxury' else '600'} !important;
            border-bottom: 1px solid {border} !important;
            padding-bottom: 20px !important;
            font-family: {font} !important;
        }}
        & .drawer-item-node {{
            background: {bg_alt} !important;
            border-radius: {radius} !important;
            padding: 16px !important;
            border: 1px solid {border} !important;
            transition: all 0.3s ease !important;
        }}
        & .drawer-item-node:hover {{
            border-color: {a} !important;
            transform: translateX(4px) !important;
        }}
        """
        
        for section_id in ['33', '34', '35', '36']:
            style_customizations[section_id] = {
                'background_color': bg,
                'text_color': t,
                'font_family': font,
                'padding': '0px',
                'custom_css': drawer_css
            }

        # 7. Sticky Cart CSS
        sticky_css = f"""
        & .sticky-cart-bar {{
            background: {bg}dd !important;
            backdrop-filter: blur(12px) !important;
            border-top: 1px solid {border} !important;
            padding: 14px 5% !important;
            box-shadow: 0 -4px 24px rgba(0,0,0,0.04) !important;
        }}
        & .sticky-cart-total {{
            color: {a} !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            font-family: {font} !important;
        }}
        & .sticky-view-bag-btn {{
            border: 1px solid {t} !important;
            color: {t} !important;
            font-weight: 500 !important;
            font-size: 0.8rem !important;
            padding: 10px 24px !important;
            border-radius: {radius} !important;
            transition: all 0.3s ease !important;
            font-family: {font} !important;
        }}
        & .sticky-view-bag-btn:hover {{
            background: {t} !important;
            color: {bg} !important;
        }}
        & .sticky-checkout-btn {{
            background: {a} !important;
            color: {bg} !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            padding: 10px 28px !important;
            border-radius: {radius} !important;
            transition: all 0.3s ease !important;
            font-family: {font} !important;
            border: none !important;
        }}
        & .sticky-checkout-btn:hover {{
            background: {p} !important;
            transform: scale(1.02) !important;
        }}
        """
        
        for section_id in ['37', '38']:
            style_customizations[section_id] = {
                'background_color': bg,
                'text_color': t,
                'font_family': font,
                'padding': '0px',
                'custom_css': sticky_css
            }

        # 8. Contact CSS
        contact_css = f"""
        & .contact-card-box {{
            border: 1px solid {border} !important;
            border-radius: {radius} !important;
            background: {bg} !important;
            overflow: hidden !important;
            box-shadow: 0 8px 40px rgba(0,0,0,0.03) !important;
        }}
        & .contact-aesthetic-sidebar {{
            background: {p} !important;
            padding: 50px !important;
            color: {bg} !important;
        }}
        & .contact-aesthetic-sidebar h3 {{
            color: {bg} !important;
            font-size: 2.2rem !important;
            font-weight: {'300' if style == 'luxury' else '700'} !important;
            font-family: {font} !important;
        }}
        & .studio-coordinates {{
            color: {bg}cc !important;
            font-size: 0.95rem !important;
            line-height: 2.2 !important;
            font-family: {font} !important;
        }}
        & .studio-coordinates span {{
            color: {a} !important;
        }}
        & .art-form-group input,
        & .art-form-group textarea {{
            border-bottom: 2px solid {border} !important;
            font-size: 1rem !important;
            padding: 12px 0 !important;
            font-family: {font} !important;
            transition: all 0.3s ease !important;
        }}
        & .art-form-group input:focus,
        & .art-form-group textarea:focus {{
            border-bottom-color: {a} !important;
        }}
        & .art-form-group label {{
            color: {t}80 !important;
            font-weight: 500 !important;
            font-size: 0.8rem !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            font-family: {font} !important;
        }}
        & .art-submit-btn {{
            background: {p} !important;
            color: {bg} !important;
            border-radius: {radius} !important;
            padding: 16px 40px !important;
            font-weight: 600 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            transition: all 0.3s ease !important;
            font-family: {font} !important;
            border: none !important;
            cursor: pointer !important;
        }}
        & .art-submit-btn:hover {{
            background: {a} !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 32px {a}40 !important;
        }}
        """
        
        for section_id in ['40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53']:
            style_customizations[section_id] = {
                'background_color': bg,
                'text_color': t,
                'font_family': font,
                'padding': '0px',
                'custom_css': contact_css
            }

        # 9. Footer CSS
        footer_css = f"""
        & {{
            background: {p} !important;
            color: {bg} !important;
            padding: 60px 5% 30px !important;
            border-top: 1px solid {bg}20 !important;
        }}
        & .footer-logo {{
            color: {bg} !important;
            font-size: 1.8rem !important;
            font-weight: {'300' if style == 'luxury' else '700'} !important;
            font-family: {font} !important;
            letter-spacing: 2px !important;
        }}
        & a {{
            color: {bg}cc !important;
            opacity: 0.7 !important;
            transition: all 0.3s ease !important;
            text-decoration: none !important;
            font-family: {font} !important;
        }}
        & a:hover {{
            opacity: 1 !important;
            color: {a} !important;
        }}
        & h4 {{
            color: {bg} !important;
            font-weight: 500 !important;
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
            font-size: 0.8rem !important;
            font-family: {font} !important;
        }}
        """
        
        for section_id in ['54', '55', '56', '57', '58', '59', '60', '61', '62']:
            style_customizations[section_id] = {
                'background_color': p,
                'text_color': bg,
                'font_family': font,
                'padding': '0px',
                'custom_css': footer_css
            }

        return {
            'home': {
                'text_contents': text_contents,
                'style_customizations': style_customizations
            }
        }

    def _get_industry_content(self, store_name, industry):
        content = {
            'fashion': {
                'headline': 'Timeless Elegance. Modern Luxury.',
                'subheadline': f'Welcome to {store_name}',
                'description': 'Discover our curated collection of premium fashion pieces, designed for those who appreciate the finer things in life.',
                'products_title': 'The Collection',
                'faq1_q': 'What makes your pieces unique?',
                'faq1_a': 'Every piece is crafted from premium materials with attention to detail that ensures lasting quality and timeless style.',
                'faq2_q': 'What is your shipping policy?',
                'faq2_a': 'We offer express shipping on all orders. Delivery typically takes 3-5 business days.',
                'footer_tagline': 'Redefining fashion excellence with curated collections.',
                'product1_name': 'Signature Blazer',
                'product1_price': '$450',
                'product2_name': 'Classic Trench',
                'product2_price': '$350',
                'product3_name': 'Essential Shirt',
                'product3_price': '$150',
            },
            'technology': {
                'headline': 'Innovation. Simplified.',
                'subheadline': f'The Future of {store_name}',
                'description': 'Experience cutting-edge technology with products that blend form, function, and forward-thinking design.',
                'products_title': 'Explore Innovation',
                'faq1_q': 'What makes your products innovative?',
                'faq1_a': 'We combine the latest technology with user-centered design to create products that are powerful yet intuitive.',
                'faq2_q': 'Do you offer tech support?',
                'faq2_a': 'Yes, our dedicated support team is available 24/7 to help with any questions or issues.',
                'footer_tagline': 'Pushing the boundaries of what\'s possible.',
                'product1_name': 'Nova Pro Laptop',
                'product1_price': '$1,299',
                'product2_name': 'Nova Air Tablet',
                'product2_price': '$799',
                'product3_name': 'Nova Mini Speaker',
                'product3_price': '$299',
            },
            'home_decor': {
                'headline': 'Beautiful Spaces. Natural Living.',
                'subheadline': f'Welcome to {store_name}',
                'description': 'Transform your home with sustainable, handcrafted pieces that bring warmth and character to every room.',
                'products_title': 'Curated Collection',
                'faq1_q': 'Are your products sustainable?',
                'faq1_a': 'Yes, we source only sustainable materials and work with artisans who share our commitment to the environment.',
                'faq2_q': 'What is your return policy?',
                'faq2_a': 'We offer a 30-day return policy on all items. Customer satisfaction is our priority.',
                'footer_tagline': 'Quality craftsmanship for beautiful homes.',
                'product1_name': 'Handwoven Rug',
                'product1_price': '$380',
                'product2_name': 'Ceramic Vase',
                'product2_price': '$145',
                'product3_name': 'Organic Cotton Throw',
                'product3_price': '$95',
            },
            'food_beverage': {
                'headline': 'Craft. Flavor. Passion.',
                'subheadline': f'Welcome to {store_name}',
                'description': 'Artisanal food and beverages crafted with love and the finest ingredients from around the world.',
                'products_title': 'Our Specialties',
                'faq1_q': 'Where do you source your ingredients?',
                'faq1_a': 'We work directly with farmers and producers who share our commitment to quality and sustainability.',
                'faq2_q': 'Do you offer international shipping?',
                'faq2_a': 'Yes, we ship to most countries. Delivery times vary by destination.',
                'footer_tagline': 'Celebrating the art of food.',
                'product1_name': 'Artisan Coffee',
                'product1_price': '$28',
                'product2_name': 'Craft Chocolate',
                'product2_price': '$35',
                'product3_name': 'Cold Pressed Juice',
                'product3_price': '$18',
            },
        }
        
        return content.get(industry, content['fashion'])