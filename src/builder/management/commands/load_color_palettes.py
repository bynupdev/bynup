# builder/management/commands/load_color_palettes.py

from django.core.management.base import BaseCommand
from builder.models import ColorPalette, ColorPaletteColor

class Command(BaseCommand):
    help = 'Load 30+ professional, polished color palettes with proper contrast'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Loading professional color palettes...')
        
        palettes = self.get_palette_data()
        valid_count = 0

        for palette_data in palettes:
            palette, created = ColorPalette.objects.get_or_create(
                name=palette_data['name'],
                defaults={
                    'category': palette_data['category'],
                    'mood': palette_data['mood'],
                    'slug': palette_data['name'].lower().replace(' ', '-').replace('&', 'and').replace("'", "").replace('(', '').replace(')', ''),
                    'is_active': True,
                }
            )

            if created:
                for order, (color_type, name, var_name, hex_val, rgb_val) in enumerate(palette_data['colors']):
                    ColorPaletteColor.objects.get_or_create(
                        palette=palette,
                        variable_name=var_name.lstrip('--'),
                        defaults={
                            'name': name,
                            'color_type': color_type,
                            'hex_value': hex_val,
                            'rgb_value': rgb_val,
                            'display_order': order,
                        }
                    )
                valid_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {palette.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'• Skipped (exists): {palette.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully loaded {valid_count} professional palettes!'))

    def get_palette_data(self):
        return [
            # ============================================
            # CATEGORY 1: SOPHISTICATED NEUTRALS
            # ============================================
            {
                'name': 'Warm Stone',
                'category': 'neutral',
                'mood': 'warm',
                'colors': [
                    ('background', 'Warm White', '--background', '#F8F5F0', '248, 245, 240'),
                    ('text', 'Charcoal', '--text', '#3A3530', '58, 53, 48'),
                    ('heading', 'Dark Charcoal', '--heading', '#2A2520', '42, 37, 32'),
                    ('primary', 'Stone', '--primary', '#8C7355', '140, 115, 85'),
                    ('secondary', 'Warm Taupe', '--secondary', '#A6907A', '166, 144, 122'),
                    ('accent', 'Warm Gold', '--accent', '#C49A6C', '196, 154, 108'),
                    ('border', 'Soft Sand', '--border', '#E5DDD4', '229, 221, 212'),
                    ('success', 'Muted Green', '--success', '#6B8F71', '107, 143, 113'),
                    ('warning', 'Golden', '--warning', '#D4A373', '212, 163, 115'),
                    ('error', 'Warm Red', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },
            {
                'name': 'Cool Slate',
                'category': 'neutral',
                'mood': 'cool',
                'colors': [
                    ('background', 'Slate White', '--background', '#F5F7FA', '245, 247, 250'),
                    ('text', 'Deep Slate', '--text', '#3A414A', '58, 65, 74'),
                    ('heading', 'Dark Slate', '--heading', '#2A313A', '42, 49, 58'),
                    ('primary', 'Steel', '--primary', '#5A6C7A', '90, 108, 122'),
                    ('secondary', 'Gray Blue', '--secondary', '#7A8A9A', '122, 138, 154'),
                    ('accent', 'Teal', '--accent', '#4A9E8A', '74, 158, 138'),
                    ('border', 'Cool Border', '--border', '#E1E5EA', '225, 229, 234'),
                    ('success', 'Mint', '--success', '#5A8A6A', '90, 138, 106'),
                    ('warning', 'Warm Gold', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Cool Red', '--error', '#C46A6A', '196, 106, 106'),
                ]
            },
            {
                'name': 'Polished Charcoal',
                'category': 'neutral',
                'mood': 'dark',
                'colors': [
                    ('background', 'Light Gray', '--background', '#F2F2F2', '242, 242, 242'),
                    ('text', 'Deep Charcoal', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'Black', '--heading', '#0D0D0D', '13, 13, 13'),
                    ('primary', 'Charcoal', '--primary', '#2A2A2A', '42, 42, 42'),
                    ('secondary', 'Mid Gray', '--secondary', '#4A4A4A', '74, 74, 74'),
                    ('accent', 'Gold', '--accent', '#C4A44A', '196, 164, 74'),
                    ('border', 'Light Border', '--border', '#D8D8D8', '216, 216, 216'),
                    ('success', 'Deep Green', '--success', '#3A7A5A', '58, 122, 90'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Dark Red', '--error', '#B03A3A', '176, 58, 58'),
                ]
            },

            # ============================================
            # CATEGORY 2: CONFIDENT COLOR
            # ============================================
            {
                'name': 'Brand Navy',
                'category': 'corporate',
                'mood': 'trustworthy',
                'colors': [
                    ('background', 'Navy White', '--background', '#F4F6FA', '244, 246, 250'),
                    ('text', 'Dark Navy', '--text', '#2A3440', '42, 52, 64'),
                    ('heading', 'Deep Navy', '--heading', '#1A2430', '26, 36, 48'),
                    ('primary', 'Navy Blue', '--primary', '#2A4A7A', '42, 74, 122'),
                    ('secondary', 'Steel Blue', '--secondary', '#4A6A8A', '74, 106, 138'),
                    ('accent', 'Warm Gold', '--accent', '#E5B84A', '229, 184, 74'),
                    ('border', 'Light Blue', '--border', '#D8DEE8', '216, 222, 232'),
                    ('success', 'Forest Green', '--success', '#4A8A6A', '74, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Soft Red', '--error', '#C46A6A', '196, 106, 106'),
                ]
            },
            {
                'name': 'Brand Forest',
                'category': 'corporate',
                'mood': 'trustworthy',
                'colors': [
                    ('background', 'Forest White', '--background', '#F4F7F2', '244, 247, 242'),
                    ('text', 'Deep Forest', '--text', '#2A3A2A', '42, 58, 42'),
                    ('heading', 'Dark Forest', '--heading', '#1A2A1A', '26, 42, 26'),
                    ('primary', 'Forest Green', '--primary', '#3A6B3A', '58, 107, 58'),
                    ('secondary', 'Sage', '--secondary', '#6A8A6A', '106, 138, 106'),
                    ('accent', 'Wheat', '--accent', '#C49A5A', '196, 154, 90'),
                    ('border', 'Soft Green', '--border', '#DDE4D8', '221, 228, 216'),
                    ('success', 'Deep Green', '--success', '#4A8A5A', '74, 138, 90'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Rust', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },
            {
                'name': 'Brand Terracotta',
                'category': 'corporate',
                'mood': 'warm',
                'colors': [
                    ('background', 'Terracotta White', '--background', '#F8F4F0', '248, 244, 240'),
                    ('text', 'Dark Brown', '--text', '#3A322A', '58, 50, 42'),
                    ('heading', 'Deep Brown', '--heading', '#2A221A', '42, 34, 26'),
                    ('primary', 'Terracotta', '--primary', '#A86A4A', '168, 106, 74'),
                    ('secondary', 'Warm Clay', '--secondary', '#C48A6A', '196, 138, 106'),
                    ('accent', 'Golden', '--accent', '#E5B84A', '229, 184, 74'),
                    ('border', 'Warm Border', '--border', '#E8DDD4', '232, 221, 212'),
                    ('success', 'Sage', '--success', '#5A8A6A', '90, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Deep Rust', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },

            # ============================================
            # CATEGORY 3: MODERN MINIMALIST
            # ============================================
            {
                'name': 'Modern Light',
                'category': 'neutral',
                'mood': 'modern',
                'colors': [
                    ('background', 'Pure White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'Dark Gray', '--text', '#1C1C1E', '28, 28, 30'),
                    ('heading', 'Black', '--heading', '#000000', '0, 0, 0'),
                    ('primary', 'System Blue', '--primary', '#007AFF', '0, 122, 255'),
                    ('secondary', 'System Purple', '--secondary', '#5856D6', '88, 86, 214'),
                    ('accent', 'System Red', '--accent', '#FF2D55', '255, 45, 85'),
                    ('border', 'Light Border', '--border', '#E5E5EA', '229, 229, 234'),
                    ('success', 'System Green', '--success', '#34C759', '52, 199, 89'),
                    ('warning', 'System Orange', '--warning', '#FF9500', '255, 149, 0'),
                    ('error', 'System Red', '--error', '#FF3B30', '255, 59, 48'),
                ]
            },
            {
                'name': 'Modern Dark',
                'category': 'neutral',
                'mood': 'dark',
                'colors': [
                    ('background', 'Dark Gray', '--background', '#1C1C1E', '28, 28, 30'),
                    ('text', 'Light Gray', '--text', '#EBEBF0', '235, 235, 240'),
                    ('heading', 'White', '--heading', '#FFFFFF', '255, 255, 255'),
                    ('primary', 'System Blue', '--primary', '#0A84FF', '10, 132, 255'),
                    ('secondary', 'System Purple', '--secondary', '#5E5CE6', '94, 92, 230'),
                    ('accent', 'System Pink', '--accent', '#FF375F', '255, 55, 95'),
                    ('border', 'Dark Border', '--border', '#38383A', '56, 56, 58'),
                    ('success', 'System Green', '--success', '#30D158', '48, 209, 88'),
                    ('warning', 'System Orange', '--warning', '#FF9F0A', '255, 159, 10'),
                    ('error', 'System Red', '--error', '#FF453A', '255, 69, 58'),
                ]
            },

            # ============================================
            # CATEGORY 4: E-COMMERCE OPTIMIZED
            # ============================================
            {
                'name': 'Ecom Trust',
                'category': 'ecommerce',
                'mood': 'professional',
                'colors': [
                    ('background', 'Clean White', '--background', '#FAFAFA', '250, 250, 250'),
                    ('text', 'Dark Gray', '--text', '#232323', '35, 35, 35'),
                    ('heading', 'Black', '--heading', '#111111', '17, 17, 17'),
                    ('primary', 'Deep Green', '--primary', '#2A7A5A', '42, 122, 90'),
                    ('secondary', 'Mint Green', '--secondary', '#4A9A7A', '74, 154, 122'),
                    ('accent', 'Warm Gold', '--accent', '#E5B84A', '229, 184, 74'),
                    ('border', 'Light Border', '--border', '#E0E0E0', '224, 224, 224'),
                    ('success', 'Deep Green', '--success', '#2A7A5A', '42, 122, 90'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Soft Red', '--error', '#C46A5A', '196, 106, 90'),
                ]
            },
            {
                'name': 'Ecom Luxury',
                'category': 'ecommerce',
                'mood': 'luxurious',
                'colors': [
                    ('background', 'Luxury White', '--background', '#FDFCFA', '253, 252, 250'),
                    ('text', 'Dark Gray', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Black', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Warm Taupe', '--primary', '#8A7A6A', '138, 122, 106'),
                    ('secondary', 'Light Taupe', '--secondary', '#A09080', '160, 144, 128'),
                    ('accent', 'Gold', '--accent', '#C4A44A', '196, 164, 74'),
                    ('border', 'Champagne Border', '--border', '#E8E4DE', '232, 228, 222'),
                    ('success', 'Sage', '--success', '#5A8A6A', '90, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Deep Rust', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },

            # ============================================
            # CATEGORY 5: BOLD & EDITORIAL
            # ============================================
            {
                'name': 'Editorial Vibrant',
                'category': 'creative',
                'mood': 'energetic',
                'colors': [
                    ('background', 'Clean White', '--background', '#FAFAFA', '250, 250, 250'),
                    ('text', 'Dark Gray', '--text', '#1C1C1E', '28, 28, 30'),
                    ('heading', 'Black', '--heading', '#000000', '0, 0, 0'),
                    ('primary', 'Magenta', '--primary', '#E84393', '232, 67, 147'),
                    ('secondary', 'Purple', '--secondary', '#6C5CE7', '108, 92, 231'),
                    ('accent', 'Cyan', '--accent', '#00CEC9', '0, 206, 201'),
                    ('border', 'Light Border', '--border', '#E5E5EA', '229, 229, 234'),
                    ('success', 'Emerald', '--success', '#00B894', '0, 184, 148'),
                    ('warning', 'Amber', '--warning', '#FDCB6E', '253, 203, 110'),
                    ('error', 'Ruby', '--error', '#D63031', '214, 48, 49'),
                ]
            },
            {
                'name': 'Editorial Classic',
                'category': 'creative',
                'mood': 'professional',
                'colors': [
                    ('background', 'Classic White', '--background', '#FCFCFA', '252, 252, 250'),
                    ('text', 'Dark Gray', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'Black', '--heading', '#0D0D0D', '13, 13, 13'),
                    ('primary', 'Crimson', '--primary', '#C0392B', '192, 57, 43'),
                    ('secondary', 'Navy', '--secondary', '#2C3E50', '44, 62, 80'),
                    ('accent', 'Orange', '--accent', '#E67E22', '230, 126, 34'),
                    ('border', 'Light Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'Green', '--success', '#27AE60', '39, 174, 96'),
                    ('warning', 'Yellow', '--warning', '#F1C40F', '241, 196, 15'),
                    ('error', 'Red', '--error', '#E74C3C', '231, 76, 60'),
                ]
            },

            # ============================================
            # CATEGORY 6: WARM & WELCOMING
            # ============================================
            {
                'name': 'Warm Blush',
                'category': 'creative',
                'mood': 'warm',
                'colors': [
                    ('background', 'Blush White', '--background', '#FDF8F5', '253, 248, 245'),
                    ('text', 'Rose Brown', '--text', '#4A3A3A', '74, 58, 58'),
                    ('heading', 'Deep Rose', '--heading', '#3A2A2A', '58, 42, 42'),
                    ('primary', 'Coral', '--primary', '#D47A7A', '212, 122, 122'),
                    ('secondary', 'Soft Pink', '--secondary', '#E8B8B8', '232, 184, 184'),
                    ('accent', 'Warm Peach', '--accent', '#D4A88A', '212, 168, 138'),
                    ('border', 'Soft Blush', '--border', '#F0E0D8', '240, 224, 216'),
                    ('success', 'Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Golden', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Deep Coral', '--error', '#C46B6B', '196, 107, 107'),
                ]
            },
            {
                'name': 'Warm Sand',
                'category': 'neutral',
                'mood': 'warm',
                'colors': [
                    ('background', 'Sand White', '--background', '#FDFAF5', '253, 250, 245'),
                    ('text', 'Warm Brown', '--text', '#3A3530', '58, 53, 48'),
                    ('heading', 'Deep Brown', '--heading', '#2A2520', '42, 37, 32'),
                    ('primary', 'Sand', '--primary', '#C49A6C', '196, 154, 108'),
                    ('secondary', 'Warm Taupe', '--secondary', '#A6907A', '166, 144, 122'),
                    ('accent', 'Golden', '--accent', '#E5B84A', '229, 184, 74'),
                    ('border', 'Soft Sand', '--border', '#E8E0D8', '232, 224, 216'),
                    ('success', 'Sage', '--success', '#6B8F71', '107, 143, 113'),
                    ('warning', 'Warm Gold', '--warning', '#D4A373', '212, 163, 115'),
                    ('error', 'Warm Red', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },

            # ============================================
            # CATEGORY 7: COOL & CALM
            # ============================================
            {
                'name': 'Cool Mint',
                'category': 'creative',
                'mood': 'cool',
                'colors': [
                    ('background', 'Mint White', '--background', '#F5FAFA', '245, 250, 250'),
                    ('text', 'Deep Teal', '--text', '#2A3A3A', '42, 58, 58'),
                    ('heading', 'Dark Teal', '--heading', '#1A2A2A', '26, 42, 42'),
                    ('primary', 'Teal', '--primary', '#4A9A8A', '74, 154, 138'),
                    ('secondary', 'Mint', '--secondary', '#6AB8A8', '106, 184, 168'),
                    ('accent', 'Golden', '--accent', '#E5B84A', '229, 184, 74'),
                    ('border', 'Soft Mint', '--border', '#D8E8E4', '216, 232, 228'),
                    ('success', 'Deep Green', '--success', '#4A8A6A', '74, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Soft Red', '--error', '#C46A6A', '196, 106, 106'),
                ]
            },
            {
                'name': 'Cool Sky',
                'category': 'creative',
                'mood': 'cool',
                'colors': [
                    ('background', 'Sky White', '--background', '#F5F8FA', '245, 248, 250'),
                    ('text', 'Deep Blue', '--text', '#2A3A4A', '42, 58, 74'),
                    ('heading', 'Dark Blue', '--heading', '#1A2A3A', '26, 42, 58'),
                    ('primary', 'Sky Blue', '--primary', '#4A7A9A', '74, 122, 154'),
                    ('secondary', 'Light Blue', '--secondary', '#6A9AB8', '106, 154, 184'),
                    ('accent', 'Golden', '--accent', '#E5B84A', '229, 184, 74'),
                    ('border', 'Soft Blue', '--border', '#D8E4EC', '216, 228, 236'),
                    ('success', 'Teal', '--success', '#4A8A6A', '74, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Soft Red', '--error', '#C46A6A', '196, 106, 106'),
                ]
            },

            # ============================================
            # CATEGORY 8: EARTHY & ORGANIC
            # ============================================
            {
                'name': 'Earth Forest',
                'category': 'nature',
                'mood': 'natural',
                'colors': [
                    ('background', 'Forest White', '--background', '#F4F7F2', '244, 247, 242'),
                    ('text', 'Deep Forest', '--text', '#2A3A2A', '42, 58, 42'),
                    ('heading', 'Dark Forest', '--heading', '#1A2A1A', '26, 42, 26'),
                    ('primary', 'Forest Green', '--primary', '#3A6B3A', '58, 107, 58'),
                    ('secondary', 'Sage', '--secondary', '#6A8A6A', '106, 138, 106'),
                    ('accent', 'Wheat', '--accent', '#C49A5A', '196, 154, 90'),
                    ('border', 'Soft Green', '--border', '#DDE4D8', '221, 228, 216'),
                    ('success', 'Deep Green', '--success', '#4A8A5A', '74, 138, 90'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Rust', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },
            {
                'name': 'Earth Clay',
                'category': 'nature',
                'mood': 'warm',
                'colors': [
                    ('background', 'Clay White', '--background', '#F8F4F0', '248, 244, 240'),
                    ('text', 'Clay Brown', '--text', '#3A322A', '58, 50, 42'),
                    ('heading', 'Deep Clay', '--heading', '#2A221A', '42, 34, 26'),
                    ('primary', 'Terracotta', '--primary', '#A86A4A', '168, 106, 74'),
                    ('secondary', 'Warm Clay', '--secondary', '#C48A6A', '196, 138, 106'),
                    ('accent', 'Golden', '--accent', '#E5B84A', '229, 184, 74'),
                    ('border', 'Warm Border', '--border', '#E8DDD4', '232, 221, 212'),
                    ('success', 'Sage', '--success', '#5A8A6A', '90, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Deep Rust', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },

            # ============================================
            # CATEGORY 9: LUXURY & HIGH-END
            # ============================================
            {
                'name': 'Lux Champagne',
                'category': 'luxury',
                'mood': 'luxurious',
                'colors': [
                    ('background', 'Champagne White', '--background', '#FDFCF8', '253, 252, 248'),
                    ('text', 'Dark Charcoal', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Black', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Gold', '--primary', '#C4A44A', '196, 164, 74'),
                    ('secondary', 'Warm Taupe', '--secondary', '#A09080', '160, 144, 128'),
                    ('accent', 'Champagne', '--accent', '#E8D8C0', '232, 216, 192'),
                    ('border', 'Champagne Border', '--border', '#E8E4DE', '232, 228, 222'),
                    ('success', 'Sage', '--success', '#5A8A6A', '90, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Deep Rust', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },
            {
                'name': 'Lux Noir',
                'category': 'luxury',
                'mood': 'elegant',
                'colors': [
                    ('background', 'Noir White', '--background', '#F8F8F8', '248, 248, 248'),
                    ('text', 'Noir Black', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'Black', '--heading', '#0D0D0D', '13, 13, 13'),
                    ('primary', 'Dark Gray', '--primary', '#3A3A3A', '58, 58, 58'),
                    ('secondary', 'Mid Gray', '--secondary', '#5A5A5A', '90, 90, 90'),
                    ('accent', 'Gold', '--accent', '#C4A44A', '196, 164, 74'),
                    ('border', 'Light Gray', '--border', '#E0E0E0', '224, 224, 224'),
                    ('success', 'Deep Green', '--success', '#3A7A5A', '58, 122, 90'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Dark Red', '--error', '#B03A3A', '176, 58, 58'),
                ]
            },

            # ============================================
            # CATEGORY 10: ARTS & CULTURE
            # ============================================
            {
                'name': 'Art Muted',
                'category': 'creative',
                'mood': 'elegant',
                'colors': [
                    ('background', 'Muted White', '--background', '#FCFAF8', '252, 250, 248'),
                    ('text', 'Muted Gray', '--text', '#3A3A3A', '58, 58, 58'),
                    ('heading', 'Dark Gray', '--heading', '#2A2A2A', '42, 42, 42'),
                    ('primary', 'Muted Mauve', '--primary', '#8A7A8A', '138, 122, 138'),
                    ('secondary', 'Muted Lavender', '--secondary', '#A090A0', '160, 144, 160'),
                    ('accent', 'Warm Gold', '--accent', '#C49A6C', '196, 154, 108'),
                    ('border', 'Muted Border', '--border', '#E8E4E0', '232, 228, 224'),
                    ('success', 'Sage', '--success', '#5A8A6A', '90, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Deep Rust', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },
            {
                'name': 'Art Gallery',
                'category': 'creative',
                'mood': 'modern',
                'colors': [
                    ('background', 'Gallery White', '--background', '#FAFAFA', '250, 250, 250'),
                    ('text', 'Gallery Gray', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Black', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Deep Blue', '--primary', '#2A4A7A', '42, 74, 122'),
                    ('secondary', 'Slate Blue', '--secondary', '#4A6A8A', '74, 106, 138'),
                    ('accent', 'Warm Gold', '--accent', '#C49A6C', '196, 154, 108'),
                    ('border', 'Light Border', '--border', '#E0E0E0', '224, 224, 224'),
                    ('success', 'Teal', '--success', '#4A8A6A', '74, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Soft Red', '--error', '#C46A6A', '196, 106, 106'),
                ]
            },

            # ============================================
            # CATEGORY 11: WELLNESS & HEALTH
            # ============================================
            {
                'name': 'Wellness Calm',
                'category': 'health',
                'mood': 'calm',
                'colors': [
                    ('background', 'Calm White', '--background', '#F5FAF5', '245, 250, 245'),
                    ('text', 'Deep Green', '--text', '#2A3A2A', '42, 58, 42'),
                    ('heading', 'Dark Green', '--heading', '#1A2A1A', '26, 42, 26'),
                    ('primary', 'Calm Green', '--primary', '#5A8A6A', '90, 138, 106'),
                    ('secondary', 'Soft Sage', '--secondary', '#7AAA8A', '122, 170, 138'),
                    ('accent', 'Wheat', '--accent', '#C49A5A', '196, 154, 90'),
                    ('border', 'Soft Green', '--border', '#DDE8DE', '221, 232, 222'),
                    ('success', 'Deep Green', '--success', '#4A8A5A', '74, 138, 90'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Rust', '--error', '#B05A4A', '176, 90, 74'),
                ]
            },
            {
                'name': 'Wellness Spa',
                'category': 'health',
                'mood': 'calm',
                'colors': [
                    ('background', 'Spa White', '--background', '#F8FAF8', '248, 250, 248'),
                    ('text', 'Spa Gray', '--text', '#3A3A3A', '58, 58, 58'),
                    ('heading', 'Dark Gray', '--heading', '#2A2A2A', '42, 42, 42'),
                    ('primary', 'Mint', '--primary', '#4A9A8A', '74, 154, 138'),
                    ('secondary', 'Soft Mint', '--secondary', '#6AB8A8', '106, 184, 168'),
                    ('accent', 'Warm Gold', '--accent', '#C49A6C', '196, 154, 108'),
                    ('border', 'Soft Mint Border', '--border', '#E0E8E4', '224, 232, 228'),
                    ('success', 'Teal', '--success', '#4A8A6A', '74, 138, 106'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Soft Red', '--error', '#C46A6A', '196, 106, 106'),
                ]
            },

            # ============================================
            # CATEGORY 12: SOCIAL MEDIA
            # ============================================
            {
                'name': 'Social Clean',
                'category': 'social-media',
                'mood': 'modern',
                'colors': [
                    ('background', 'Clean White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'Dark Gray', '--text', '#262626', '38, 38, 38'),
                    ('heading', 'Black', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Instagram Blue', '--primary', '#0095F6', '0, 149, 246'),
                    ('secondary', 'Soft Gray', '--secondary', '#8E8E8E', '142, 142, 142'),
                    ('accent', 'Instagram Pink', '--accent', '#E4405F', '228, 64, 95'),
                    ('border', 'Light Border', '--border', '#DBDBDB', '219, 219, 219'),
                    ('success', 'Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'Orange', '--warning', '#FF9500', '255, 149, 0'),
                    ('error', 'Red', '--error', '#ED4956', '237, 73, 86'),
                ]
            },
            {
                'name': 'Social Dark',
                'category': 'social-media',
                'mood': 'dark',
                'colors': [
                    ('background', 'Dark', '--background', '#000000', '0, 0, 0'),
                    ('text', 'Light Gray', '--text', '#F5F5F5', '245, 245, 245'),
                    ('heading', 'White', '--heading', '#FFFFFF', '255, 255, 255'),
                    ('primary', 'Instagram Blue', '--primary', '#0095F6', '0, 149, 246'),
                    ('secondary', 'Dark Gray', '--secondary', '#A8A8A8', '168, 168, 168'),
                    ('accent', 'Instagram Pink', '--accent', '#E4405F', '228, 64, 95'),
                    ('border', 'Dark Border', '--border', '#262626', '38, 38, 38'),
                    ('success', 'Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'Orange', '--warning', '#FF9500', '255, 149, 0'),
                    ('error', 'Red', '--error', '#ED4956', '237, 73, 86'),
                ]
            },
            {
                'name': 'Social Facebook',
                'category': 'social-media',
                'mood': 'professional',
                'colors': [
                    ('background', 'Facebook White', '--background', '#F0F2F5', '240, 242, 245'),
                    ('text', 'Facebook Dark', '--text', '#1C1E21', '28, 30, 33'),
                    ('heading', 'Black', '--heading', '#0D0D0D', '13, 13, 13'),
                    ('primary', 'Facebook Blue', '--primary', '#1877F2', '24, 119, 242'),
                    ('secondary', 'Facebook Gray', '--secondary', '#65676B', '101, 103, 107'),
                    ('accent', 'Facebook Green', '--accent', '#42B72A', '66, 183, 42'),
                    ('border', 'Facebook Border', '--border', '#CED0D4', '206, 208, 212'),
                    ('success', 'Green', '--success', '#31A24C', '49, 162, 76'),
                    ('warning', 'Yellow', '--warning', '#F7B928', '247, 185, 40'),
                    ('error', 'Red', '--error', '#E41E3F', '228, 30, 63'),
                ]
            },
            {
                'name': 'Social Twitter',
                'category': 'social-media',
                'mood': 'modern',
                'colors': [
                    ('background', 'Twitter White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'Twitter Dark', '--text', '#0F1419', '15, 20, 25'),
                    ('heading', 'Black', '--heading', '#000000', '0, 0, 0'),
                    ('primary', 'Twitter Blue', '--primary', '#1D9BF0', '29, 155, 240'),
                    ('secondary', 'Twitter Gray', '--secondary', '#536471', '83, 100, 113'),
                    ('accent', 'Twitter Blue', '--accent', '#1D9BF0', '29, 155, 240'),
                    ('border', 'Twitter Border', '--border', '#EFF3F4', '239, 243, 244'),
                    ('success', 'Green', '--success', '#00BA7C', '0, 186, 124'),
                    ('warning', 'Yellow', '--warning', '#FFD400', '255, 212, 0'),
                    ('error', 'Red', '--error', '#F4212E', '244, 33, 46'),
                ]
            },
            {
                'name': 'Social YouTube',
                'category': 'social-media',
                'mood': 'professional',
                'colors': [
                    ('background', 'YouTube White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'YouTube Dark', '--text', '#0D0D0D', '13, 13, 13'),
                    ('heading', 'Black', '--heading', '#000000', '0, 0, 0'),
                    ('primary', 'YouTube Red', '--primary', '#FF0000', '255, 0, 0'),
                    ('secondary', 'YouTube Gray', '--secondary', '#606060', '96, 96, 96'),
                    ('accent', 'YouTube Red', '--accent', '#FF0000', '255, 0, 0'),
                    ('border', 'YouTube Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'Red', '--error', '#FF0000', '255, 0, 0'),
                ]
            },
            {
                'name': 'Social LinkedIn',
                'category': 'social-media',
                'mood': 'professional',
                'colors': [
                    ('background', 'LinkedIn White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'LinkedIn Dark', '--text', '#191919', '25, 25, 25'),
                    ('heading', 'Black', '--heading', '#0D0D0D', '13, 13, 13'),
                    ('primary', 'LinkedIn Blue', '--primary', '#0A66C2', '10, 102, 194'),
                    ('secondary', 'LinkedIn Gray', '--secondary', '#666666', '102, 102, 102'),
                    ('accent', 'LinkedIn Blue', '--accent', '#0A66C2', '10, 102, 194'),
                    ('border', 'LinkedIn Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'Red', '--error', '#E53935', '229, 57, 53'),
                ]
            },
            {
                'name': 'Social TikTok',
                'category': 'social-media',
                'mood': 'energetic',
                'colors': [
                    ('background', 'TikTok White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'TikTok Dark', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'Black', '--heading', '#000000', '0, 0, 0'),
                    ('primary', 'TikTok Black', '--primary', '#000000', '0, 0, 0'),
                    ('secondary', 'TikTok Gray', '--secondary', '#8A8A8A', '138, 138, 138'),
                    ('accent', 'TikTok Cyan', '--accent', '#00F2EA', '0, 242, 234'),
                    ('border', 'TikTok Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'Red', '--error', '#FF3B30', '255, 59, 48'),
                ]
            },
        ]