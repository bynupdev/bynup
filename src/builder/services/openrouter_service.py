# builder/services/openrouter_service.py - FINAL FIXED VERSION

import json
import os
import re
import ast
from openai import OpenAI
from django.conf import settings


# ============================================
# COLOR PALETTES
# ============================================

COLOR_PALETTES = {
    'beauty_pink': {'primary': '#2d1a2a', 'secondary': '#4a2a4a', 'accent': '#e8a0b0', 'bg': '#f5f0f5', 'text': '#2a1a2a', 'bg_alt': '#e8dde8'},
    'beauty_glow': {'primary': '#2d1a1a', 'secondary': '#4a2a2a', 'accent': '#f0c0a0', 'bg': '#faf5f0', 'text': '#2d1a1a', 'bg_alt': '#f0ebe5'},
    'beauty_clean': {'primary': '#1a2a2a', 'secondary': '#2d4a4a', 'accent': '#a0d4d4', 'bg': '#f0f5f5', 'text': '#1a2a2a', 'bg_alt': '#e8eef2'},
    'fashion_luxury': {'primary': '#0a0a0a', 'secondary': '#1a1a1a', 'accent': '#c9a959', 'bg': '#f5f0e8', 'text': '#0a0a0a', 'bg_alt': '#e8e0d5'},
    'fashion_modern': {'primary': '#1a1a2e', 'secondary': '#16213e', 'accent': '#e94560', 'bg': '#ffffff', 'text': '#1a1a2e', 'bg_alt': '#f0f0f0'},
    'tech_dark': {'primary': '#0a0a0a', 'secondary': '#1a1a2e', 'accent': '#4cc9f0', 'bg': '#0d0d0d', 'text': '#ffffff', 'bg_alt': '#1a1a2e'},
    'tech_modern': {'primary': '#1e3a5f', 'secondary': '#2d5a7a', 'accent': '#4a7a9a', 'bg': '#f5f8fa', 'text': '#1a2a3a', 'bg_alt': '#e8eef2'},
    'decor_organic': {'primary': '#2d5a27', 'secondary': '#4a7a44', 'accent': '#c9b99a', 'bg': '#f5f0e8', 'text': '#2d3a2d', 'bg_alt': '#e8e5d5'},
    'decor_warm': {'primary': '#8B5A2B', 'secondary': '#A67B5B', 'accent': '#D4A373', 'bg': '#F5EDE4', 'text': '#3D2B1F', 'bg_alt': '#E8DDD0'},
    'wellness_calm': {'primary': '#2d5a27', 'secondary': '#4a7a44', 'accent': '#8fa89b', 'bg': '#f5f0e8', 'text': '#2d3a2d', 'bg_alt': '#e8e5d5'},
    'food_warm': {'primary': '#8B4513', 'secondary': '#D2691E', 'accent': '#F4A460', 'bg': '#FFF8F0', 'text': '#3D1F0A', 'bg_alt': '#F5EDE0'},
    'food_coffee': {'primary': '#3D1F0A', 'secondary': '#6B3A1A', 'accent': '#C49A6C', 'bg': '#FFF5E6', 'text': '#1A0A05', 'bg_alt': '#F5EDE0'},
    'food_fresh': {'primary': '#2E7D32', 'secondary': '#43A047', 'accent': '#FFD54F', 'bg': '#FFFDE7', 'text': '#1A2E1A', 'bg_alt': '#F0F5E8'},
    'sports_energetic': {'primary': '#1a1a2e', 'secondary': '#2d1a2e', 'accent': '#ff6b35', 'bg': '#f5f0f5', 'text': '#1a1a2e', 'bg_alt': '#f0e8f0'},
    'edu_classic': {'primary': '#1a2a3a', 'secondary': '#2d4a5a', 'accent': '#c9a959', 'bg': '#f5f0e8', 'text': '#1a2a3a', 'bg_alt': '#e8e5d5'},
    'default_modern': {'primary': '#1a1a2e', 'secondary': '#16213e', 'accent': '#e94560', 'bg': '#ffffff', 'text': '#1a1a2e', 'bg_alt': '#f0f0f0'},
}


# ============================================
# INDUSTRY CONTENT
# ============================================

INDUSTRY_CONTENT = {
    'food_beverage': {
        'subtitle': 'Crafted with Love. Served with Passion.',
        'desc': 'Artisanal creations where quality ingredients meet expert craftsmanship.',
        'p1': 'ARTISAN|Artisan Blend|$65|Small-batch crafted for exceptional flavor',
        'p2': 'PURE|Pure Tea|$45|Single-origin tea with depth and character',
        'p3': 'CRAFT|Craft Gift Set|$85|Curated selection of artisanal favorites',
        'f1': 'What makes your products special?|Finest ingredients from trusted growers worldwide.',
        'f2': 'Do you offer gift options?|Curated gift collections for any occasion.',
        'footer': 'Redefining food with artisanal quality and exceptional taste.',
        'collection': '✦ Offerings',
        'voice': 'artisanal, warm, authentic'
    },
    'beauty': {
        'subtitle': 'Radiant Beauty. Confident You.',
        'desc': 'Premium beauty essentials crafted for your unique glow. Clean ingredients. Visible results.',
        'p1': 'LUXE|Luxe Collection|$320|Complete skincare ritual for radiant skin',
        'p2': 'GLOW|Glow Serum|$180|Vitamin C booster for instant radiance',
        'p3': 'PURE|Pure Essentials|$95|Minimalist skincare for sensitive skin',
        'f1': 'Are your products cruelty-free?|100% cruelty-free, never tested on animals.',
        'f2': 'What skin types do you cater to?|Formulated for all skin types with gentle, effective ingredients.',
        'footer': 'Redefining beauty with clean ingredients and radiant results.',
        'collection': '✦ Collections',
        'voice': 'luxurious, empowering, clean'
    },
    'technology': {
        'subtitle': 'Innovation. Simplified.',
        'desc': 'Cutting-edge technology with thoughtfully designed products for the future.',
        'p1': 'PRO|Pro Series|$1,299|Professional-grade performance for creators',
        'p2': 'AIR|Air Edition|$799|Lightweight, powerful, and sleek',
        'p3': 'MINI|Mini Compact|$299|Big features in a compact design',
        'f1': 'What makes your products innovative?|Cutting-edge technology meets intuitive design.',
        'f2': 'Do you offer warranties?|Comprehensive warranty and dedicated support team.',
        'footer': 'Redefining technology with innovative products and smart design.',
        'collection': '✦ Products',
        'voice': 'innovative, sleek, professional'
    },
    'fashion': {
        'subtitle': 'Timeless Elegance. Modern Style.',
        'desc': 'Curated collection of premium fashion where quality meets craftsmanship.',
        'p1': 'SIGNATURE|Signature Collection|$450|Iconic pieces for the modern wardrobe',
        'p2': 'ESSENTIAL|Classic Essential|$350|Timeless staples that never go out of style',
        'p3': 'BASIC|Everyday Basic|$150|Effortless style for everyday wear',
        'f1': 'What makes your brand unique?|Premium materials and exceptional attention to detail.',
        'f2': 'How do I find my size?|Detailed size guides and free returns for the perfect fit.',
        'footer': 'Redefining fashion with timeless pieces and uncompromising quality.',
        'collection': '✦ Collections',
        'voice': 'elegant, sophisticated, premium'
    },
    'sports': {
        'subtitle': 'Push Beyond Limits.',
        'desc': 'Engineered for performance. Designed for champions. Built to last.',
        'p1': 'PRO|Pro Performance|$520|Elite gear for peak performance',
        'p2': 'TRAIN|Train Essential|$280|Versatile gear for every workout',
        'p3': 'CORE|Core Basics|$150|Foundation pieces for daily training',
        'f1': 'What makes your gear different?|Engineered with athletes using premium materials.',
        'f2': 'How does your sizing run?|Performance-fit sizing with detailed guides.',
        'footer': 'Redefining sports with performance-driven design and quality.',
        'collection': '✦ Gear',
        'voice': 'powerful, confident, performance-driven'
    },
    'home_decor': {
        'subtitle': 'Beautiful Spaces. Inspired Living.',
        'desc': 'Handcrafted pieces that bring warmth and character to your home.',
        'p1': 'HERITAGE|Heritage Collection|$380|Handcrafted pieces with storied craftsmanship',
        'p2': 'EARTH|Earth Essential|$245|Organic materials for mindful living',
        'p3': 'PURE|Pure Classic|$195|Clean design for modern spaces',
        'f1': 'Are your products sustainable?|Eco-friendly materials and ethical practices.',
        'f2': 'How do I care for my items?|Care instructions designed for longevity.',
        'footer': 'Redefining home decor with sustainable design and timeless beauty.',
        'collection': '✦ Collections',
        'voice': 'warm, organic, sophisticated'
    },
    'education': {
        'subtitle': 'Knowledge. Growth. Future.',
        'desc': 'Empowering minds with innovative learning solutions for every stage of life.',
        'p1': 'PRO|Pro Learning Kit|$240|Advanced tools for serious learners',
        'p2': 'ESSENTIAL|Essential Set|$150|Core resources for foundational learning',
        'p3': 'BASIC|Basic Bundle|$85|Essential materials for starting the journey',
        'f1': 'What age groups do you serve?|All ages, from early learners to professionals.',
        'f2': 'Are there ongoing resources?|Continuous learning resources and community support.',
        'footer': 'Redefining education with innovative tools and lifelong learning.',
        'collection': '✦ Resources',
        'voice': 'trustworthy, inspiring, empowering'
    },
    'other': {
        'subtitle': 'Excellence in Everything.',
        'desc': 'Curated collection where quality meets innovation. Discover the difference.',
        'p1': 'PREMIUM|Premium Collection|$299|Premium quality for discerning customers',
        'p2': 'ESSENTIAL|Essential Set|$199|Everything you need, nothing you don\'t',
        'p3': 'BASIC|Basic Essentials|$99|Simple solutions that just work',
        'f1': 'What makes your products unique?|Premium materials and exceptional attention to detail.',
        'f2': 'How does shipping work?|Fast, tracked shipping in 3-5 business days.',
        'footer': 'Redefining quality with style and innovation.',
        'collection': '✦ Collections',
        'voice': 'premium, reliable, innovative'
    }
}


# ============================================
# OPENROUTER MODELS
# ============================================

OPENROUTER_MODELS = [
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "meta-llama/llama-3.3-70b-instruct",
    "meta-llama/llama-4-scout",
    "mistralai/mistral-large",
    "deepseek/deepseek-chat",
    "qwen/qwen-2.5-72b-instruct",
    "microsoft/phi-4-mini-instruct",
    "cohere/command-r-plus",
    "anthropic/claude-3-haiku",
]


# ============================================
# MAIN OPENROUTER SERVICE CLASS
# ============================================

class OpenRouterDesignService:

    def __init__(self, template_name='modernecommerce33'):
        self.template_name = template_name
        
        try:
            api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
            if not api_key:
                print("⚠️ OPENROUTER_API_KEY not found in settings")
                self.client = None
            else:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                    default_headers={
                        "HTTP-Referer": getattr(settings, 'SITE_URL', 'http://localhost:8000'),
                        "X-Title": "AI Website Builder"
                    }
                )
                self.models = OPENROUTER_MODELS
                print(f"🤖 Using OpenRouter with {len(self.models)} models (failover enabled)")
                print(f"   - Primary: {self.models[0]}")
                print(f"   - Fallback: {self.models[1]}, {self.models[2]}")
                print(f"   - Status: ✅ Connected")
        except Exception as e:
            print(f"❌ Failed to initialize OpenRouter: {e}")
            self.client = None
        
        self.template_structure = self._get_template_structure()
        self.editable_elements = self._extract_editable_elements()

        print(f"🚀 OpenRouter Design Service initialized")
        print(f"  - Template: {self.template_name}")
        print(f"  - AI Available: {self.client is not None}")
        print(f"  - Text elements: {len(self.editable_elements['text_keys'])}")
        print(f"  - Sections: {len(self.editable_elements['section_keys'])}")

    def _get_template_structure(self):
        return {
            'pages': ['home'],
            'sections': {str(i): {'id': str(i)} for i in range(1, 73)},
            'text_elements': {str(i): {'id': str(i)} for i in range(1, 56)}
        }

    def _extract_editable_elements(self):
        return {
            'text_keys': list(self.template_structure['text_elements'].keys()),
            'section_keys': list(self.template_structure['sections'].keys()),
        }

    def _get_color_palette_from_selection(self, palette_id):
        return COLOR_PALETTES.get(palette_id, COLOR_PALETTES['default_modern'])

    def _get_industry_content(self, industry):
        return INDUSTRY_CONTENT.get(industry, INDUSTRY_CONTENT['other'])

    def _call_model_with_failover(self, messages, max_tokens=6000, temperature=0.9):
        if not self.client:
            return None, "No client available"
        
        last_error = None
        
        for model in self.models:
            try:
                print(f"🔄 Trying model: {model}")
                
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9,
                )
                
                response_text = completion.choices[0].message.content
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
                elif "402" in error_msg or "credits" in error_msg:
                    print(f"💰 Model {model} needs credits, trying next...")
                    last_error = error_msg
                    continue
                    
                last_error = error_msg
                continue
        
        return None, f"All models failed. Last error: {last_error}"

    def generate_customizations(self, store_name, industry, style, palette_id, chat_context=""):
        colors = self._get_color_palette_from_selection(palette_id)
        industry_content = self._get_industry_content(industry)

        print(f"🎨 Using palette: {palette_id}")
        print(f"🎨 Colors: {colors}")
        print(f"📝 Industry: {industry}")

        if not self.client:
            raise Exception("OpenRouter client not available. Please check your API key.")

        try:
            # Build the creative prompt
            prompt = self._build_creative_prompt(store_name, industry, colors, industry_content)
            
            print(f"📝 Prompt size: ~{len(prompt)} chars")
            
            messages = [
                {"role": "system", "content": """You are a creative web designer. Create unique, stunning websites. Output valid JSON. Be extremely creative with CSS animations, gradients, and modern design patterns. Make every section unique."""},
                {"role": "user", "content": prompt}
            ]
            
            # Use 6000 max_tokens to ensure complete JSON
            response_text, used_model = self._call_model_with_failover(messages, max_tokens=6000, temperature=0.95)
            
            if not response_text or not used_model:
                raise Exception("No model could generate a response.")
            
            print(f"✅ OpenRouter response from {used_model} ({len(response_text)} chars)")
            
            # Parse the response with our robust parser
            customizations = self._parse_response(response_text)
            
            if not customizations:
                print(f"❌ Could not parse JSON. Response preview: {response_text[:500]}...")
                # Try to save the raw response for debugging
                with open('debug_response.txt', 'w') as f:
                    f.write(response_text)
                print("📁 Saved raw response to debug_response.txt")
                raise Exception("Failed to parse AI response into valid JSON.")
            
            return self._validate_customizations(customizations, store_name, industry, colors, industry_content)
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg}")
            raise Exception(f"AI generation failed: {error_msg}")

    def _build_creative_prompt(self, store_name, industry, colors, industry_content):
        """Build a concise but creative prompt"""
        p1 = industry_content['p1'].split('|')
        p2 = industry_content['p2'].split('|')
        p3 = industry_content['p3'].split('|')
        f1 = industry_content['f1'].split('|')
        f2 = industry_content['f2'].split('|')
        
        return f"""Create a unique {industry} website for "{store_name}".

EXACT COLORS:
Primary:{colors['primary']} Accent:{colors['accent']} BG:{colors['bg']} Text:{colors['text']} BG Alt:{colors['bg_alt']}

CONTENT:
Hero:"{industry_content['subtitle']}"|"{industry_content['desc']}"
Products:
  {p1[0]}|{p1[1]}|{p1[2]}|{p1[3]}
  {p2[0]}|{p2[1]}|{p2[2]}|{p2[3]}
  {p3[0]}|{p3[1]}|{p3[2]}|{p3[3]}
FAQ:
  "{f1[0]}"|"{f1[1]}"
  "{f2[0]}"|"{f2[1]}"
Footer:"{industry_content['footer']}"

DESIGN: Be extremely creative. Use CSS animations, gradients, unique shapes, glass-morphism, hover effects. Every section must have unique styling.

Return JSON with text_contents and style_customizations for ALL sections.

Format: {{"home":{{"text_contents":{{"1":"{store_name.upper()}","8":"{store_name.upper()}","9":"{industry_content['subtitle']}","10":"{industry_content['desc']}","100":"{p1[0]}","101":"{p1[1]}","102":"{p1[2]}","103":"{p2[0]}","104":"{p2[1]}","105":"{p2[2]}","106":"{p3[0]}","107":"{p3[1]}","108":"{p3[2]}","21":"{f1[0]}","22":"{f1[1]}","23":"{f2[0]}","24":"{f2[1]}","32":"{industry_content['footer']}"}},"style_customizations":{{"1":{{"background_color":"{colors['primary']}","text_color":"{colors['bg']}","font_family":"'Inter', sans-serif","padding":"0px","custom_css":"/* CREATIVE CSS */"}},...}}}}}}
"""

    def _parse_response(self, text):
        """Parse response with aggressive recovery"""
        if not text:
            return None
        
        text = text.strip()
        
        # Remove markdown code blocks
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        # If the response is cut off, try to complete it
        if text.endswith('...') or text.endswith(',') or text.endswith('"') and text.count('{') > text.count('}'):
            # Try to close the JSON
            open_braces = text.count('{')
            close_braces = text.count('}')
            open_brackets = text.count('[')
            close_brackets = text.count(']')
            
            if open_braces > close_braces:
                # Remove trailing comma if present
                text = re.sub(r',\s*$', '', text)
                text += '}' * (open_braces - close_braces)
            
            if open_brackets > close_brackets:
                text = re.sub(r',\s*$', '', text)
                text += ']' * (open_brackets - close_brackets)
        
        # Find the JSON object
        json_match = re.search(r'\{[\s\S]*\}', text)
        if not json_match:
            return None
        
        json_str = json_match.group()
        
        # Try multiple parse strategies
        strategies = [
            # Strategy 1: Direct parse
            lambda s: json.loads(s),
            # Strategy 2: Fix trailing commas
            lambda s: json.loads(re.sub(r',\s*}', '}', re.sub(r',\s*]', ']', s))),
            # Strategy 3: Fix unquoted keys
            lambda s: json.loads(re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', s)),
            # Strategy 4: Fix single quotes
            lambda s: json.loads(s.replace("'", '"')),
            # Strategy 5: Combine all fixes
            lambda s: json.loads(re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', 
                                        re.sub(r',\s*}', '}', 
                                        re.sub(r',\s*]', ']', 
                                        s.replace("'", '"'))))),
            # Strategy 6: ast.literal_eval
            lambda s: json.loads(json.dumps(ast.literal_eval(s.replace('true', 'True').replace('false', 'False').replace('null', 'None')))),
        ]
        
        for strategy in strategies:
            try:
                result = strategy(json_str)
                if result and isinstance(result, dict) and 'home' in result:
                    return result
            except:
                continue
        
        # Strategy 7: Try to extract partial JSON
        try:
            # Try to extract what we can
            result = {}
            # Look for key-value pairs
            pairs = re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', json_str)
            for key, value in pairs:
                if key not in result:
                    result[key] = value
            
            # Look for nested objects
            nested = re.findall(r'"([^"]+)"\s*:\s*\{([^{}]*)\}', json_str)
            for key, value in nested:
                if key not in result:
                    result[key] = {}
                    inner_pairs = re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', value)
                    for inner_key, inner_value in inner_pairs:
                        result[key][inner_key] = inner_value
            
            if result:
                # Try to build a valid structure
                customizations = {'home': {'text_contents': {}, 'style_customizations': {}}}
                if 'text_contents' in result:
                    customizations['home']['text_contents'] = result['text_contents']
                if 'style_customizations' in result:
                    customizations['home']['style_customizations'] = result['style_customizations']
                return customizations
        except:
            pass
        
        return None

    def _validate_customizations(self, customizations, store_name, industry, colors, industry_content):
        """Validate and fill missing sections"""
        if 'home' not in customizations:
            customizations = {'home': customizations}

        if 'text_contents' not in customizations['home']:
            customizations['home']['text_contents'] = {}

        if 'style_customizations' not in customizations['home']:
            customizations['home']['style_customizations'] = {}

        # Fill text contents
        p1 = industry_content['p1'].split('|')
        p2 = industry_content['p2'].split('|')
        p3 = industry_content['p3'].split('|')
        f1 = industry_content['f1'].split('|')
        f2 = industry_content['f2'].split('|')

        required_texts = {
            '1': store_name.upper(),
            '8': store_name.upper(),
            '9': industry_content['subtitle'],
            '10': industry_content['desc'],
            '100': p1[0], '101': p1[1], '102': p1[2],
            '103': p2[0], '104': p2[1], '105': p2[2],
            '106': p3[0], '107': p3[1], '108': p3[2],
            '21': f1[0], '22': f1[1],
            '23': f2[0], '24': f2[1],
            '32': industry_content['footer'],
        }
        
        for key, value in required_texts.items():
            if key not in customizations['home']['text_contents'] or not customizations['home']['text_contents'][key]:
                customizations['home']['text_contents'][key] = value

        # Fill missing sections
        for section_id in self.editable_elements['section_keys']:
            if section_id not in customizations['home']['style_customizations']:
                customizations['home']['style_customizations'][section_id] = {
                    'background_color': colors['bg'],
                    'text_color': colors['text'],
                    'font_family': "'Inter', sans-serif",
                    'padding': '0px',
                    'custom_css': ''
                }
            elif not isinstance(customizations['home']['style_customizations'][section_id], dict):
                customizations['home']['style_customizations'][section_id] = {
                    'background_color': colors['bg'],
                    'text_color': colors['text'],
                    'font_family': "'Inter', sans-serif",
                    'padding': '0px',
                    'custom_css': ''
                }
            else:
                if 'background_color' not in customizations['home']['style_customizations'][section_id]:
                    customizations['home']['style_customizations'][section_id]['background_color'] = colors['bg']
                if 'text_color' not in customizations['home']['style_customizations'][section_id]:
                    customizations['home']['style_customizations'][section_id]['text_color'] = colors['text']
                if 'font_family' not in customizations['home']['style_customizations'][section_id]:
                    customizations['home']['style_customizations'][section_id]['font_family'] = "'Inter', sans-serif"
                if 'padding' not in customizations['home']['style_customizations'][section_id]:
                    customizations['home']['style_customizations'][section_id]['padding'] = '0px'
                if 'custom_css' not in customizations['home']['style_customizations'][section_id]:
                    customizations['home']['style_customizations'][section_id]['custom_css'] = ''

        print(f"✅ Validated: {len(customizations['home']['text_contents'])} text fields, {len(customizations['home']['style_customizations'])} sections")
        return customizations