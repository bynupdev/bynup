# builder/management/commands/load_color_palettes.py

from django.core.management.base import BaseCommand
from builder.models import ColorPalette, ColorPaletteColor

class Command(BaseCommand):
    help = 'Load premium color palettes with brand-colored headers'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Loading premium color palettes with brand headers...')
        
        palettes = self.get_palette_data()
        
        valid_count = 0
        
        for palette_data in palettes:
            # Ensure header uses brand color, not black
            colors = self.ensure_brand_headers(palette_data['colors'])
            
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
                for order, (color_type, name, var_name, hex_val, rgb_val) in enumerate(colors):
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
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully loaded {valid_count} palettes with brand-colored headers!'))

    def ensure_brand_headers(self, colors):
        """Ensure headers use brand colors, never black/dark"""
        color_dict = {}
        for color_type, name, var_name, hex_val, rgb_val in colors:
            color_dict[color_type] = {
                'name': name,
                'var_name': var_name,
                'hex': hex_val,
                'rgb': rgb_val
            }
        
        # Get background color
        bg_hex = color_dict['background']['hex']
        bg_is_light = self.is_light_color(bg_hex)
        
        # HEADER SHOULD USE PRIMARY/BRAND COLOR - NOT BLACK!
        # Only use the primary color as header if it has good contrast
        primary_hex = color_dict['primary']['hex']
        contrast_with_bg = self.get_contrast_ratio(bg_hex, primary_hex)
        
        if contrast_with_bg >= 4.5:
            # Primary has good contrast, use it for headers
            color_dict['heading']['hex'] = primary_hex
            color_dict['heading']['name'] = f"{color_dict['primary']['name']} (Brand)"
        else:
            # Primary is too low contrast, use a darkened/lightened version
            if bg_is_light:
                # Darken the primary for light backgrounds
                darkened = self.darken_color(primary_hex, 0.5)
                color_dict['heading']['hex'] = darkened
                color_dict['heading']['name'] = f"{color_dict['primary']['name']} Dark"
            else:
                # Lighten the primary for dark backgrounds
                lightened = self.lighten_color(primary_hex, 0.5)
                color_dict['heading']['hex'] = lightened
                color_dict['heading']['name'] = f"{color_dict['primary']['name']} Light"
        
        # Ensure text has good contrast
        text_hex = color_dict['text']['hex']
        if self.get_contrast_ratio(bg_hex, text_hex) < 4.5:
            if bg_is_light:
                color_dict['text']['hex'] = '#1A1A1A'
            else:
                color_dict['text']['hex'] = '#EAEAEA'
            color_dict['text']['name'] = 'Readable Text'
        
        # Rebuild the color list
        validated_colors = []
        for color_type, data in color_dict.items():
            validated_colors.append((
                color_type,
                data['name'],
                data['var_name'],
                data['hex'],
                self.hex_to_rgb_string(data['hex'])
            ))
        
        return validated_colors

    def hex_to_rgb(self, hex_color):
        """Convert hex to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def hex_to_rgb_string(self, hex_color):
        """Convert hex to RGB string format"""
        r, g, b = self.hex_to_rgb(hex_color)
        return f"{r}, {g}, {b}"

    def get_luminance(self, hex_color):
        """Calculate relative luminance"""
        r, g, b = self.hex_to_rgb(hex_color)
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def get_contrast_ratio(self, color1, color2):
        """Calculate WCAG contrast ratio"""
        lum1 = self.get_luminance(color1)
        lum2 = self.get_luminance(color2)
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        return (lighter + 0.05) / (darker + 0.05)

    def is_light_color(self, hex_color):
        """Determine if a color is light or dark"""
        return self.get_luminance(hex_color) > 0.5

    def darken_color(self, hex_color, factor):
        """Darken a color by factor (0-1, lower = darker)"""
        r, g, b = self.hex_to_rgb(hex_color)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        r = max(10, min(255, r))
        g = max(10, min(255, g))
        b = max(10, min(255, b))
        return f"#{r:02x}{g:02x}{b:02x}"

    def lighten_color(self, hex_color, factor):
        """Lighten a color by factor (0-1, higher = lighter)"""
        r, g, b = self.hex_to_rgb(hex_color)
        r = int(r + (255 - r) * (1 - factor))
        g = int(g + (255 - g) * (1 - factor))
        b = int(b + (255 - b) * (1 - factor))
        r = min(245, max(0, r))
        g = min(245, max(0, g))
        b = min(245, max(0, b))
        return f"#{r:02x}{g:02x}{b:02x}"

    # ============================================
    # ALL PALETTES WITH BRAND-COLORED HEADERS
    # ============================================

    def get_palette_data(self):
        return [
            # ============================================
            # SOCIAL MEDIA PALETTES - PERFECT MIRRORS
            # ============================================
            {
                'name': 'Instagram Light',
                'category': 'social-media',
                'mood': 'modern',
                'colors': [
                    ('background', 'IG White', '--background', '#FAFAFA', '250, 250, 250'),
                    ('text', 'IG Dark', '--text', '#262626', '38, 38, 38'),
                    ('heading', 'IG Blue', '--heading', '#0095F6', '0, 149, 246'),
                    ('primary', 'IG Blue', '--primary', '#0095F6', '0, 149, 246'),
                    ('secondary', 'IG Gray', '--secondary', '#8E8E8E', '142, 142, 142'),
                    ('accent', 'IG Pink', '--accent', '#E4405F', '228, 64, 95'),
                    ('border', 'IG Border', '--border', '#DBDBDB', '219, 219, 219'),
                    ('success', 'IG Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'IG Orange', '--warning', '#FF9500', '255, 149, 0'),
                    ('error', 'IG Red', '--error', '#ED4956', '237, 73, 86'),
                ]
            },
            {
                'name': 'Instagram Dark',
                'category': 'social-media',
                'mood': 'dark',
                'colors': [
                    ('background', 'IG Dark BG', '--background', '#000000', '0, 0, 0'),
                    ('text', 'IG Light', '--text', '#F5F5F5', '245, 245, 245'),
                    ('heading', 'IG Blue', '--heading', '#0095F6', '0, 149, 246'),
                    ('primary', 'IG Blue', '--primary', '#0095F6', '0, 149, 246'),
                    ('secondary', 'IG Dark Gray', '--secondary', '#A8A8A8', '168, 168, 168'),
                    ('accent', 'IG Pink', '--accent', '#E4405F', '228, 64, 95'),
                    ('border', 'IG Dark Border', '--border', '#262626', '38, 38, 38'),
                    ('success', 'IG Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'IG Orange', '--warning', '#FF9500', '255, 149, 0'),
                    ('error', 'IG Red', '--error', '#ED4956', '237, 73, 86'),
                ]
            },
            {
                'name': 'Facebook Light',
                'category': 'social-media',
                'mood': 'professional',
                'colors': [
                    ('background', 'FB White', '--background', '#F0F2F5', '240, 242, 245'),
                    ('text', 'FB Dark', '--text', '#1C1E21', '28, 30, 33'),
                    ('heading', 'FB Blue', '--heading', '#1877F2', '24, 119, 242'),
                    ('primary', 'FB Blue', '--primary', '#1877F2', '24, 119, 242'),
                    ('secondary', 'FB Gray', '--secondary', '#65676B', '101, 103, 107'),
                    ('accent', 'FB Green', '--accent', '#42B72A', '66, 183, 42'),
                    ('border', 'FB Border', '--border', '#CED0D4', '206, 208, 212'),
                    ('success', 'FB Success', '--success', '#31A24C', '49, 162, 76'),
                    ('warning', 'FB Warning', '--warning', '#F7B928', '247, 185, 40'),
                    ('error', 'FB Error', '--error', '#E41E3F', '228, 30, 63'),
                ]
            },
            {
                'name': 'Facebook Dark',
                'category': 'social-media',
                'mood': 'dark',
                'colors': [
                    ('background', 'FB Dark BG', '--background', '#18191A', '24, 25, 26'),
                    ('text', 'FB Light', '--text', '#E4E6EB', '228, 230, 235'),
                    ('heading', 'FB Blue', '--heading', '#1877F2', '24, 119, 242'),
                    ('primary', 'FB Blue', '--primary', '#1877F2', '24, 119, 242'),
                    ('secondary', 'FB Dark Gray', '--secondary', '#8A8D91', '138, 141, 145'),
                    ('accent', 'FB Green', '--accent', '#42B72A', '66, 183, 42'),
                    ('border', 'FB Dark Border', '--border', '#3E4042', '62, 64, 66'),
                    ('success', 'FB Success', '--success', '#31A24C', '49, 162, 76'),
                    ('warning', 'FB Warning', '--warning', '#F7B928', '247, 185, 40'),
                    ('error', 'FB Error', '--error', '#E41E3F', '228, 30, 63'),
                ]
            },
            {
                'name': 'Twitter Light',
                'category': 'social-media',
                'mood': 'modern',
                'colors': [
                    ('background', 'TW White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'TW Dark', '--text', '#0F1419', '15, 20, 25'),
                    ('heading', 'TW Blue', '--heading', '#1D9BF0', '29, 155, 240'),
                    ('primary', 'TW Blue', '--primary', '#1D9BF0', '29, 155, 240'),
                    ('secondary', 'TW Gray', '--secondary', '#536471', '83, 100, 113'),
                    ('accent', 'TW Accent', '--accent', '#1D9BF0', '29, 155, 240'),
                    ('border', 'TW Border', '--border', '#EFF3F4', '239, 243, 244'),
                    ('success', 'TW Green', '--success', '#00BA7C', '0, 186, 124'),
                    ('warning', 'TW Yellow', '--warning', '#FFD400', '255, 212, 0'),
                    ('error', 'TW Red', '--error', '#F4212E', '244, 33, 46'),
                ]
            },
            {
                'name': 'Twitter Dark (X)',
                'category': 'social-media',
                'mood': 'dark',
                'colors': [
                    ('background', 'X Dark', '--background', '#000000', '0, 0, 0'),
                    ('text', 'X Light', '--text', '#E7E9EA', '231, 233, 234'),
                    ('heading', 'X Blue', '--heading', '#1D9BF0', '29, 155, 240'),
                    ('primary', 'X Blue', '--primary', '#1D9BF0', '29, 155, 240'),
                    ('secondary', 'X Gray', '--secondary', '#71767B', '113, 118, 123'),
                    ('accent', 'X Accent', '--accent', '#1D9BF0', '29, 155, 240'),
                    ('border', 'X Border', '--border', '#2F3336', '47, 51, 54'),
                    ('success', 'X Green', '--success', '#00BA7C', '0, 186, 124'),
                    ('warning', 'X Yellow', '--warning', '#FFD400', '255, 212, 0'),
                    ('error', 'X Red', '--error', '#F4212E', '244, 33, 46'),
                ]
            },
            {
                'name': 'Snapchat',
                'category': 'social-media',
                'mood': 'playful',
                'colors': [
                    ('background', 'SC White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'SC Dark', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'SC Yellow', '--heading', '#FFFC00', '255, 252, 0'),
                    ('primary', 'SC Yellow', '--primary', '#FFFC00', '255, 252, 0'),
                    ('secondary', 'SC Gray', '--secondary', '#7B7B7B', '123, 123, 123'),
                    ('accent', 'SC Ghost', '--accent', '#FFFC00', '255, 252, 0'),
                    ('border', 'SC Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'SC Green', '--success', '#00D084', '0, 208, 132'),
                    ('warning', 'SC Orange', '--warning', '#FF9500', '255, 149, 0'),
                    ('error', 'SC Red', '--error', '#FF3B30', '255, 59, 48'),
                ]
            },
            {
                'name': 'Telegram Light',
                'category': 'social-media',
                'mood': 'clean',
                'colors': [
                    ('background', 'TG White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'TG Dark', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'TG Blue', '--heading', '#0088CC', '0, 136, 204'),
                    ('primary', 'TG Blue', '--primary', '#0088CC', '0, 136, 204'),
                    ('secondary', 'TG Gray', '--secondary', '#8D8D8D', '141, 141, 141'),
                    ('accent', 'TG Accent', '--accent', '#0088CC', '0, 136, 204'),
                    ('border', 'TG Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'TG Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'TG Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'TG Red', '--error', '#E53935', '229, 57, 53'),
                ]
            },
            {
                'name': 'Telegram Dark',
                'category': 'social-media',
                'mood': 'clean',
                'colors': [
                    ('background', 'TG Dark BG', '--background', '#1E1E1E', '30, 30, 30'),
                    ('text', 'TG Light', '--text', '#E5E5E5', '229, 229, 229'),
                    ('heading', 'TG Blue', '--heading', '#0088CC', '0, 136, 204'),
                    ('primary', 'TG Blue', '--primary', '#0088CC', '0, 136, 204'),
                    ('secondary', 'TG Dark Gray', '--secondary', '#8D8D8D', '141, 141, 141'),
                    ('accent', 'TG Accent', '--accent', '#0088CC', '0, 136, 204'),
                    ('border', 'TG Dark Border', '--border', '#2D2D2D', '45, 45, 45'),
                    ('success', 'TG Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'TG Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'TG Red', '--error', '#E53935', '229, 57, 53'),
                ]
            },
            {
                'name': 'TikTok Light',
                'category': 'social-media',
                'mood': 'energetic',
                'colors': [
                    ('background', 'TT White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'TT Dark', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'TT Cyan', '--heading', '#00F2EA', '0, 242, 234'),
                    ('primary', 'TT Black', '--primary', '#000000', '0, 0, 0'),
                    ('secondary', 'TT Gray', '--secondary', '#8A8A8A', '138, 138, 138'),
                    ('accent', 'TT Cyan', '--accent', '#00F2EA', '0, 242, 234'),
                    ('border', 'TT Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'TT Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'TT Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'TT Red', '--error', '#FF3B30', '255, 59, 48'),
                ]
            },
            {
                'name': 'TikTok Dark',
                'category': 'social-media',
                'mood': 'energetic',
                'colors': [
                    ('background', 'TT Dark BG', '--background', '#121212', '18, 18, 18'),
                    ('text', 'TT Light', '--text', '#E5E5E5', '229, 229, 229'),
                    ('heading', 'TT Cyan', '--heading', '#00F2EA', '0, 242, 234'),
                    ('primary', 'TT White', '--primary', '#FFFFFF', '255, 255, 255'),
                    ('secondary', 'TT Dark Gray', '--secondary', '#8A8A8A', '138, 138, 138'),
                    ('accent', 'TT Cyan', '--accent', '#00F2EA', '0, 242, 234'),
                    ('border', 'TT Dark Border', '--border', '#2D2D2D', '45, 45, 45'),
                    ('success', 'TT Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'TT Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'TT Red', '--error', '#FF3B30', '255, 59, 48'),
                ]
            },
            {
                'name': 'YouTube Light',
                'category': 'social-media',
                'mood': 'professional',
                'colors': [
                    ('background', 'YT White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'YT Dark', '--text', '#0D0D0D', '13, 13, 13'),
                    ('heading', 'YT Red', '--heading', '#FF0000', '255, 0, 0'),
                    ('primary', 'YT Red', '--primary', '#FF0000', '255, 0, 0'),
                    ('secondary', 'YT Gray', '--secondary', '#606060', '96, 96, 96'),
                    ('accent', 'YT Red', '--accent', '#FF0000', '255, 0, 0'),
                    ('border', 'YT Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'YT Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'YT Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'YT Red', '--error', '#FF0000', '255, 0, 0'),
                ]
            },
            {
                'name': 'YouTube Dark',
                'category': 'social-media',
                'mood': 'dark',
                'colors': [
                    ('background', 'YT Dark BG', '--background', '#0F0F0F', '15, 15, 15'),
                    ('text', 'YT Light', '--text', '#F1F1F1', '241, 241, 241'),
                    ('heading', 'YT Red', '--heading', '#FF0000', '255, 0, 0'),
                    ('primary', 'YT Red', '--primary', '#FF0000', '255, 0, 0'),
                    ('secondary', 'YT Dark Gray', '--secondary', '#AAAAAA', '170, 170, 170'),
                    ('accent', 'YT Red', '--accent', '#FF0000', '255, 0, 0'),
                    ('border', 'YT Dark Border', '--border', '#272727', '39, 39, 39'),
                    ('success', 'YT Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'YT Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'YT Red', '--error', '#FF0000', '255, 0, 0'),
                ]
            },
            {
                'name': 'WhatsApp Light',
                'category': 'social-media',
                'mood': 'clean',
                'colors': [
                    ('background', 'WA White', '--background', '#F5F5F5', '245, 245, 245'),
                    ('text', 'WA Dark', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'WA Green', '--heading', '#25D366', '37, 211, 102'),
                    ('primary', 'WA Green', '--primary', '#25D366', '37, 211, 102'),
                    ('secondary', 'WA Gray', '--secondary', '#8D8D8D', '141, 141, 141'),
                    ('accent', 'WA Teal', '--accent', '#128C7E', '18, 140, 126'),
                    ('border', 'WA Border', '--border', '#E0E0E0', '224, 224, 224'),
                    ('success', 'WA Green', '--success', '#25D366', '37, 211, 102'),
                    ('warning', 'WA Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'WA Red', '--error', '#E53935', '229, 57, 53'),
                ]
            },
            {
                'name': 'WhatsApp Dark',
                'category': 'social-media',
                'mood': 'clean',
                'colors': [
                    ('background', 'WA Dark BG', '--background', '#1A1A1A', '26, 26, 26'),
                    ('text', 'WA Light', '--text', '#E5E5E5', '229, 229, 229'),
                    ('heading', 'WA Green', '--heading', '#25D366', '37, 211, 102'),
                    ('primary', 'WA Green', '--primary', '#25D366', '37, 211, 102'),
                    ('secondary', 'WA Dark Gray', '--secondary', '#8D8D8D', '141, 141, 141'),
                    ('accent', 'WA Teal', '--accent', '#128C7E', '18, 140, 126'),
                    ('border', 'WA Dark Border', '--border', '#2D2D2D', '45, 45, 45'),
                    ('success', 'WA Green', '--success', '#25D366', '37, 211, 102'),
                    ('warning', 'WA Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'WA Red', '--error', '#E53935', '229, 57, 53'),
                ]
            },
            {
                'name': 'Discord Light',
                'category': 'social-media',
                'mood': 'modern',
                'colors': [
                    ('background', 'DC White', '--background', '#F8F9FA', '248, 249, 250'),
                    ('text', 'DC Dark', '--text', '#1A1A2E', '26, 26, 46'),
                    ('heading', 'DC Blurple', '--heading', '#5865F2', '88, 101, 242'),
                    ('primary', 'DC Blurple', '--primary', '#5865F2', '88, 101, 242'),
                    ('secondary', 'DC Gray', '--secondary', '#8A8FA3', '138, 143, 163'),
                    ('accent', 'DC Green', '--accent', '#57F287', '87, 242, 135'),
                    ('border', 'DC Border', '--border', '#D9DCE4', '217, 220, 228'),
                    ('success', 'DC Green', '--success', '#57F287', '87, 242, 135'),
                    ('warning', 'DC Yellow', '--warning', '#FEE75C', '254, 231, 92'),
                    ('error', 'DC Red', '--error', '#ED4245', '237, 66, 69'),
                ]
            },
            {
                'name': 'Discord Dark',
                'category': 'social-media',
                'mood': 'dark',
                'colors': [
                    ('background', 'DC Dark BG', '--background', '#1E1F22', '30, 31, 34'),
                    ('text', 'DC Light', '--text', '#DBDEE1', '219, 222, 225'),
                    ('heading', 'DC Blurple', '--heading', '#5865F2', '88, 101, 242'),
                    ('primary', 'DC Blurple', '--primary', '#5865F2', '88, 101, 242'),
                    ('secondary', 'DC Dark Gray', '--secondary', '#8A8FA3', '138, 143, 163'),
                    ('accent', 'DC Green', '--accent', '#57F287', '87, 242, 135'),
                    ('border', 'DC Dark Border', '--border', '#2E2F33', '46, 47, 51'),
                    ('success', 'DC Green', '--success', '#57F287', '87, 242, 135'),
                    ('warning', 'DC Yellow', '--warning', '#FEE75C', '254, 231, 92'),
                    ('error', 'DC Red', '--error', '#ED4245', '237, 66, 69'),
                ]
            },
            {
                'name': 'Reddit Light',
                'category': 'social-media',
                'mood': 'community',
                'colors': [
                    ('background', 'RD White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'RD Dark', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'RD Orange', '--heading', '#FF4500', '255, 69, 0'),
                    ('primary', 'RD Orange', '--primary', '#FF4500', '255, 69, 0'),
                    ('secondary', 'RD Gray', '--secondary', '#7C7C7C', '124, 124, 124'),
                    ('accent', 'RD Blue', '--accent', '#0079D3', '0, 121, 211'),
                    ('border', 'RD Border', '--border', '#CCCCCC', '204, 204, 204'),
                    ('success', 'RD Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'RD Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'RD Red', '--error', '#FF3B30', '255, 59, 48'),
                ]
            },
            {
                'name': 'Reddit Dark',
                'category': 'social-media',
                'mood': 'dark',
                'colors': [
                    ('background', 'RD Dark BG', '--background', '#1A1A1B', '26, 26, 27'),
                    ('text', 'RD Light', '--text', '#D7DADC', '215, 218, 220'),
                    ('heading', 'RD Orange', '--heading', '#FF4500', '255, 69, 0'),
                    ('primary', 'RD Orange', '--primary', '#FF4500', '255, 69, 0'),
                    ('secondary', 'RD Dark Gray', '--secondary', '#818384', '129, 131, 132'),
                    ('accent', 'RD Blue', '--accent', '#0079D3', '0, 121, 211'),
                    ('border', 'RD Dark Border', '--border', '#343536', '52, 53, 54'),
                    ('success', 'RD Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'RD Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'RD Red', '--error', '#FF3B30', '255, 59, 48'),
                ]
            },
            {
                'name': 'Pinterest Light',
                'category': 'social-media',
                'mood': 'creative',
                'colors': [
                    ('background', 'PI White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'PI Dark', '--text', '#211922', '33, 25, 34'),
                    ('heading', 'PI Red', '--heading', '#E60023', '230, 0, 35'),
                    ('primary', 'PI Red', '--primary', '#E60023', '230, 0, 35'),
                    ('secondary', 'PI Gray', '--secondary', '#767676', '118, 118, 118'),
                    ('accent', 'PI Red', '--accent', '#E60023', '230, 0, 35'),
                    ('border', 'PI Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'PI Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'PI Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'PI Red', '--error', '#E60023', '230, 0, 35'),
                ]
            },
            {
                'name': 'Pinterest Dark',
                'category': 'social-media',
                'mood': 'dark',
                'colors': [
                    ('background', 'PI Dark BG', '--background', '#111111', '17, 17, 17'),
                    ('text', 'PI Light', '--text', '#E5E5E5', '229, 229, 229'),
                    ('heading', 'PI Red', '--heading', '#E60023', '230, 0, 35'),
                    ('primary', 'PI Red', '--primary', '#E60023', '230, 0, 35'),
                    ('secondary', 'PI Dark Gray', '--secondary', '#767676', '118, 118, 118'),
                    ('accent', 'PI Red', '--accent', '#E60023', '230, 0, 35'),
                    ('border', 'PI Dark Border', '--border', '#2D2D2D', '45, 45, 45'),
                    ('success', 'PI Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'PI Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'PI Red', '--error', '#E60023', '230, 0, 35'),
                ]
            },
            {
                'name': 'LinkedIn Light',
                'category': 'social-media',
                'mood': 'professional',
                'colors': [
                    ('background', 'LI White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'LI Dark', '--text', '#191919', '25, 25, 25'),
                    ('heading', 'LI Blue', '--heading', '#0A66C2', '10, 102, 194'),
                    ('primary', 'LI Blue', '--primary', '#0A66C2', '10, 102, 194'),
                    ('secondary', 'LI Gray', '--secondary', '#666666', '102, 102, 102'),
                    ('accent', 'LI Blue', '--accent', '#0A66C2', '10, 102, 194'),
                    ('border', 'LI Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'LI Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'LI Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'LI Red', '--error', '#E53935', '229, 57, 53'),
                ]
            },
            {
                'name': 'LinkedIn Dark',
                'category': 'social-media',
                'mood': 'professional',
                'colors': [
                    ('background', 'LI Dark BG', '--background', '#1A1A1A', '26, 26, 26'),
                    ('text', 'LI Light', '--text', '#E5E5E5', '229, 229, 229'),
                    ('heading', 'LI Blue', '--heading', '#0A66C2', '10, 102, 194'),
                    ('primary', 'LI Blue', '--primary', '#0A66C2', '10, 102, 194'),
                    ('secondary', 'LI Dark Gray', '--secondary', '#666666', '102, 102, 102'),
                    ('accent', 'LI Blue', '--accent', '#0A66C2', '10, 102, 194'),
                    ('border', 'LI Dark Border', '--border', '#2D2D2D', '45, 45, 45'),
                    ('success', 'LI Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'LI Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'LI Red', '--error', '#E53935', '229, 57, 53'),
                ]
            },
            {
                'name': 'Signal Light',
                'category': 'social-media',
                'mood': 'clean',
                'colors': [
                    ('background', 'SG White', '--background', '#FFFFFF', '255, 255, 255'),
                    ('text', 'SG Dark', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'SG Blue', '--heading', '#3A76F0', '58, 118, 240'),
                    ('primary', 'SG Blue', '--primary', '#3A76F0', '58, 118, 240'),
                    ('secondary', 'SG Gray', '--secondary', '#8D8D8D', '141, 141, 141'),
                    ('accent', 'SG Green', '--accent', '#00C853', '0, 200, 83'),
                    ('border', 'SG Border', '--border', '#E5E5E5', '229, 229, 229'),
                    ('success', 'SG Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'SG Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'SG Red', '--error', '#E53935', '229, 57, 53'),
                ]
            },
            {
                'name': 'Signal Dark',
                'category': 'social-media',
                'mood': 'clean',
                'colors': [
                    ('background', 'SG Dark BG', '--background', '#1A1A1A', '26, 26, 26'),
                    ('text', 'SG Light', '--text', '#E5E5E5', '229, 229, 229'),
                    ('heading', 'SG Blue', '--heading', '#3A76F0', '58, 118, 240'),
                    ('primary', 'SG Blue', '--primary', '#3A76F0', '58, 118, 240'),
                    ('secondary', 'SG Dark Gray', '--secondary', '#8D8D8D', '141, 141, 141'),
                    ('accent', 'SG Green', '--accent', '#00C853', '0, 200, 83'),
                    ('border', 'SG Dark Border', '--border', '#2D2D2D', '45, 45, 45'),
                    ('success', 'SG Green', '--success', '#00C853', '0, 200, 83'),
                    ('warning', 'SG Yellow', '--warning', '#FFB300', '255, 179, 0'),
                    ('error', 'SG Red', '--error', '#E53935', '229, 57, 53'),
                ]
            },

            # ============================================
            # WARM MINIMAL PALETTES
            # ============================================
            {
                'name': 'Warm Studio',
                'category': 'warm-minimal',
                'mood': 'warm',
                'colors': [
                    ('background', 'Studio White', '--background', '#FAF6F2', '250, 246, 242'),
                    ('text', 'Warm Charcoal', '--text', '#3D362E', '61, 54, 46'),
                    ('heading', 'Burnt Orange', '--heading', '#CC6D3C', '204, 109, 60'),
                    ('primary', 'Burnt Orange', '--primary', '#CC6D3C', '204, 109, 60'),
                    ('secondary', 'Warm Taupe', '--secondary', '#A08974', '160, 137, 116'),
                    ('accent', 'Rust', '--accent', '#B85D3A', '184, 93, 58'),
                    ('border', 'Warm Border', '--border', '#EBE3DA', '235, 227, 218'),
                    ('success', 'Olive', '--success', '#7A8C5E', '122, 140, 94'),
                    ('warning', 'Goldenrod', '--warning', '#C99B3B', '201, 155, 59'),
                    ('error', 'Deep Rust', '--error', '#A84A35', '168, 74, 53'),
                ]
            },
            {
                'name': 'Cream & Cocoa',
                'category': 'warm-minimal',
                'mood': 'warm',
                'colors': [
                    ('background', 'Heavy Cream', '--background', '#FDF9F5', '253, 249, 245'),
                    ('text', 'Cocoa Brown', '--text', '#4A3C35', '74, 60, 53'),
                    ('heading', 'Caramel', '--heading', '#B8864E', '184, 134, 78'),
                    ('primary', 'Caramel', '--primary', '#B8864E', '184, 134, 78'),
                    ('secondary', 'Warm Gray', '--secondary', '#8F8279', '143, 130, 121'),
                    ('accent', 'Copper', '--accent', '#C67A4A', '198, 122, 74'),
                    ('border', 'Cream Border', '--border', '#F0E8E0', '240, 232, 224'),
                    ('success', 'Moss', '--success', '#7A8F6C', '122, 143, 108'),
                    ('warning', 'Honey', '--warning', '#D4A04A', '212, 160, 74'),
                    ('error', 'Mahogany', '--error', '#9E4A3A', '158, 74, 58'),
                ]
            },
            {
                'name': 'Terracotta Clay',
                'category': 'warm-minimal',
                'mood': 'earthy',
                'colors': [
                    ('background', 'Soft Clay', '--background', '#F7F0EA', '247, 240, 234'),
                    ('text', 'Clay Brown', '--text', '#5A4A3E', '90, 74, 62'),
                    ('heading', 'Burnt Sienna', '--heading', '#B86E4E', '184, 110, 78'),
                    ('primary', 'Burnt Sienna', '--primary', '#B86E4E', '184, 110, 78'),
                    ('secondary', 'Warm Sand', '--secondary', '#9E8A74', '158, 138, 116'),
                    ('accent', 'Coral Clay', '--accent', '#C46E5E', '196, 110, 94'),
                    ('border', 'Clay Border', '--border', '#E8DCD0', '232, 220, 208'),
                    ('success', 'Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Golden Clay', '--warning', '#C49A5A', '196, 154, 90'),
                    ('error', 'Deep Coral', '--error', '#B85A4E', '184, 90, 78'),
                ]
            },

            # ============================================
            # COOL MINIMAL PALETTES
            # ============================================
            {
                'name': 'Nordic Light',
                'category': 'cool-minimal',
                'mood': 'cool',
                'colors': [
                    ('background', 'Nordic White', '--background', '#F2F5F8', '242, 245, 248'),
                    ('text', 'Fjord Gray', '--text', '#3A4450', '58, 68, 80'),
                    ('heading', 'Nordic Blue', '--heading', '#5A7A9E', '90, 122, 158'),
                    ('primary', 'Nordic Blue', '--primary', '#5A7A9E', '90, 122, 158'),
                    ('secondary', 'Stone Gray', '--secondary', '#8A9AA8', '138, 154, 168'),
                    ('accent', 'Glacier', '--accent', '#6BA5CE', '107, 165, 206'),
                    ('border', 'Nordic Border', '--border', '#D8E0E8', '216, 224, 232'),
                    ('success', 'Pine', '--success', '#5A9E7A', '90, 158, 122'),
                    ('warning', 'Birch', '--warning', '#CEB06B', '206, 176, 107'),
                    ('error', 'Berry', '--error', '#C46B7A', '196, 107, 122'),
                ]
            },
            {
                'name': 'Cool Editorial',
                'category': 'cool-minimal',
                'mood': 'cool',
                'colors': [
                    ('background', 'Cool Paper', '--background', '#F5F7FA', '245, 247, 250'),
                    ('text', 'Cool Slate', '--text', '#2C3440', '44, 52, 64'),
                    ('heading', 'Steel Blue', '--heading', '#5A7A9E', '90, 122, 158'),
                    ('primary', 'Steel Blue', '--primary', '#5A7A9E', '90, 122, 158'),
                    ('secondary', 'Cool Gray', '--secondary', '#7A8A9E', '122, 138, 158'),
                    ('accent', 'Cornflower', '--accent', '#6B8FCE', '107, 143, 206'),
                    ('border', 'Cool Border', '--border', '#DCE2EA', '220, 226, 234'),
                    ('success', 'Teal', '--success', '#4A9E8F', '74, 158, 143'),
                    ('warning', 'Marigold', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Cool Red', '--error', '#CE6B6B', '206, 107, 107'),
                ]
            },

            # ============================================
            # BOLD EDITORIAL PALETTES
            # ============================================
            {
                'name': 'Magazine Cover',
                'category': 'bold-editorial',
                'mood': 'dramatic',
                'colors': [
                    ('background', 'Magazine White', '--background', '#FCFCFA', '252, 252, 250'),
                    ('text', 'Magazine Black', '--text', '#1E1E20', '30, 30, 32'),
                    ('heading', 'Magenta Pop', '--heading', '#E84393', '232, 67, 147'),
                    ('primary', 'Magenta Pop', '--primary', '#E84393', '232, 67, 147'),
                    ('secondary', 'Deep Purple', '--secondary', '#6C5CE7', '108, 92, 231'),
                    ('accent', 'Cyan', '--accent', '#00CEC9', '0, 206, 201'),
                    ('border', 'Magazine Border', '--border', '#D8D8DA', '216, 216, 218'),
                    ('success', 'Emerald', '--success', '#00B894', '0, 184, 148'),
                    ('warning', 'Amber', '--warning', '#FDCB6E', '253, 203, 110'),
                    ('error', 'Ruby', '--error', '#D63031', '214, 48, 49'),
                ]
            },
            {
                'name': 'Bold Statement',
                'category': 'bold-editorial',
                'mood': 'bold',
                'colors': [
                    ('background', 'Crisp White', '--background', '#FAFAFA', '250, 250, 250'),
                    ('text', 'Bold Black', '--text', '#1C1C1E', '28, 28, 30'),
                    ('heading', 'Vermilion', '--heading', '#E74C3C', '231, 76, 60'),
                    ('primary', 'Vermilion', '--primary', '#E74C3C', '231, 76, 60'),
                    ('secondary', 'Slate', '--secondary', '#5A6C7A', '90, 108, 122'),
                    ('accent', 'Turquoise', '--accent', '#1ABC9C', '26, 188, 156'),
                    ('border', 'Bold Border', '--border', '#D5D5D8', '213, 213, 216'),
                    ('success', 'Shamrock', '--success', '#27AE60', '39, 174, 96'),
                    ('warning', 'Marigold', '--warning', '#F39C12', '243, 156, 18'),
                    ('error', 'Alizarin', '--error', '#C0392B', '192, 57, 43'),
                ]
            },

            # ============================================
            # ELEGANT LUXURY PALETTES
            # ============================================
            {
                'name': 'Champagne Gold',
                'category': 'elegant-luxury',
                'mood': 'luxurious',
                'colors': [
                    ('background', 'Champagne', '--background', '#FDF8F0', '253, 248, 240'),
                    ('text', 'Rich Espresso', '--text', '#3A2A2A', '58, 42, 42'),
                    ('heading', 'Burnished Gold', '--heading', '#C4A44A', '196, 164, 74'),
                    ('primary', 'Burnished Gold', '--primary', '#C4A44A', '196, 164, 74'),
                    ('secondary', 'Warm Taupe', '--secondary', '#A8907A', '168, 144, 122'),
                    ('accent', 'Pearl', '--accent', '#F0E8D8', '240, 232, 216'),
                    ('border', 'Gold Border', '--border', '#E8DCC0', '232, 220, 192'),
                    ('success', 'Jade', '--success', '#4A9E7A', '74, 158, 122'),
                    ('warning', 'Topaz', '--warning', '#D4B06B', '212, 176, 107'),
                    ('error', 'Garnet', '--error', '#A84A4A', '168, 74, 74'),
                ]
            },
            {
                'name': 'Bone & Bronze',
                'category': 'elegant-luxury',
                'mood': 'elegant',
                'colors': [
                    ('background', 'Bone White', '--background', '#F8F4EF', '248, 244, 239'),
                    ('text', 'Bronze Brown', '--text', '#4E433A', '78, 67, 58'),
                    ('heading', 'Burnished Bronze', '--heading', '#A87A5E', '168, 122, 94'),
                    ('primary', 'Burnished Bronze', '--primary', '#A87A5E', '168, 122, 94'),
                    ('secondary', 'Warm Pewter', '--secondary', '#8B7D72', '139, 125, 114'),
                    ('accent', 'Patina', '--accent', '#6B8F7C', '107, 143, 124'),
                    ('border', 'Bone Border', '--border', '#E5DDD4', '229, 221, 212'),
                    ('success', 'Verdigris', '--success', '#5A8F7A', '90, 143, 122'),
                    ('warning', 'Ochre', '--warning', '#C49A4A', '196, 154, 74'),
                    ('error', 'Aged Red', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },

            # ============================================
            # EARTHY ORGANIC PALETTES
            # ============================================
            {
                'name': 'Forest Bath',
                'category': 'earthy-organic',
                'mood': 'natural',
                'colors': [
                    ('background', 'Forest Mist', '--background', '#F2F5F0', '242, 245, 240'),
                    ('text', 'Deep Forest', '--text', '#2A3A2A', '42, 58, 42'),
                    ('heading', 'Forest Green', '--heading', '#4A7A4A', '74, 122, 74'),
                    ('primary', 'Forest Green', '--primary', '#4A7A4A', '74, 122, 74'),
                    ('secondary', 'Moss', '--secondary', '#7A9E6B', '122, 158, 107'),
                    ('accent', 'Wild Berry', '--accent', '#9E4A6B', '158, 74, 107'),
                    ('border', 'Forest Border', '--border', '#D8E2D0', '216, 226, 208'),
                    ('success', 'Meadow', '--success', '#5AAA5A', '90, 170, 90'),
                    ('warning', 'Golden Leaf', '--warning', '#C4A44A', '196, 164, 74'),
                    ('error', 'Rust', '--error', '#B85A3A', '184, 90, 58'),
                ]
            },
            {
                'name': 'Botanical Garden',
                'category': 'earthy-organic',
                'mood': 'fresh',
                'colors': [
                    ('background', 'Garden White', '--background', '#F5F8F0', '245, 248, 240'),
                    ('text', 'Rich Soil', '--text', '#3A3A2A', '58, 58, 42'),
                    ('heading', 'Herb Green', '--heading', '#5A8A4A', '90, 138, 74'),
                    ('primary', 'Herb Green', '--primary', '#5A8A4A', '90, 138, 74'),
                    ('secondary', 'Sage', '--secondary', '#8AAA7A', '138, 170, 122'),
                    ('accent', 'Lavender', '--accent', '#9E7AB8', '158, 122, 184'),
                    ('border', 'Garden Border', '--border', '#D8E2CC', '216, 226, 204'),
                    ('success', 'Fresh Leaf', '--success', '#4AA86B', '74, 168, 107'),
                    ('warning', 'Honey', '--warning', '#D4B04A', '212, 176, 74'),
                    ('error', 'Rose Hip', '--error', '#C45A5A', '196, 90, 90'),
                ]
            },

            # ============================================
            # URBAN MODERN PALETTES
            # ============================================
            {
                'name': 'Urban Concrete',
                'category': 'urban-modern',
                'mood': 'urban',
                'colors': [
                    ('background', 'Concrete White', '--background', '#F2F0EE', '242, 240, 238'),
                    ('text', 'Urban Charcoal', '--text', '#3A3A38', '58, 58, 56'),
                    ('heading', 'Graffiti Blue', '--heading', '#4A8ACE', '74, 138, 206'),
                    ('primary', 'Concrete', '--primary', '#8A8A84', '138, 138, 132'),
                    ('secondary', 'Warm Cement', '--secondary', '#A8A49E', '168, 164, 158'),
                    ('accent', 'Graffiti Blue', '--accent', '#4A8ACE', '74, 138, 206'),
                    ('border', 'Concrete Border', '--border', '#D8D6D2', '216, 214, 210'),
                    ('success', 'Urban Green', '--success', '#5A9E5A', '90, 158, 90'),
                    ('warning', 'Taxi Yellow', '--warning', '#D4B44A', '212, 180, 74'),
                    ('error', 'Stop Red', '--error', '#CE5A5A', '206, 90, 90'),
                ]
            },
            {
                'name': 'Industrial Loft',
                'category': 'urban-modern',
                'mood': 'industrial',
                'colors': [
                    ('background', 'Loft White', '--background', '#F5F3F0', '245, 243, 240'),
                    ('text', 'Iron Gray', '--text', '#3A3A3A', '58, 58, 58'),
                    ('heading', 'Rust', '--heading', '#B86A4A', '184, 106, 74'),
                    ('primary', 'Rust', '--primary', '#B86A4A', '184, 106, 74'),
                    ('secondary', 'Steel', '--secondary', '#7A8A9E', '122, 138, 158'),
                    ('accent', 'Copper Pipe', '--accent', '#C48A5A', '196, 138, 90'),
                    ('border', 'Industrial Border', '--border', '#D0CEC8', '208, 206, 200'),
                    ('success', 'Safety Green', '--success', '#5AAA5A', '90, 170, 90'),
                    ('warning', 'Caution Yellow', '--warning', '#D4C04A', '212, 192, 74'),
                    ('error', 'Warning Red', '--error', '#C44A4A', '196, 74, 74'),
                ]
            },

            # ============================================
            # SOFT ROMANTIC PALETTES
            # ============================================
            {
                'name': 'Blush & Cream',
                'category': 'soft-romantic',
                'mood': 'gentle',
                'colors': [
                    ('background', 'Blush White', '--background', '#FDF8F5', '253, 248, 245'),
                    ('text', 'Rose Brown', '--text', '#4A3A3A', '74, 58, 58'),
                    ('heading', 'Coral', '--heading', '#D47A7A', '212, 122, 122'),
                    ('primary', 'Blush', '--primary', '#D4A0A0', '212, 160, 160'),
                    ('secondary', 'Warm Cream', '--secondary', '#E8D0C8', '232, 208, 200'),
                    ('accent', 'Coral', '--accent', '#D47A7A', '212, 122, 122'),
                    ('border', 'Blush Border', '--border', '#E8D8D4', '232, 216, 212'),
                    ('success', 'Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Peach', '--warning', '#D4A88A', '212, 168, 138'),
                    ('error', 'Deep Coral', '--error', '#C46B6B', '196, 107, 107'),
                ]
            },
            {
                'name': 'Lavender Fields',
                'category': 'soft-romantic',
                'mood': 'dreamy',
                'colors': [
                    ('background', 'Lavender White', '--background', '#F8F5FA', '248, 245, 250'),
                    ('text', 'Lavender Gray', '--text', '#4A4450', '74, 68, 80'),
                    ('heading', 'Lavender', '--heading', '#9E8AB8', '158, 138, 184'),
                    ('primary', 'Lavender', '--primary', '#9E8AB8', '158, 138, 184'),
                    ('secondary', 'Wispy Purple', '--secondary', '#C4B8D4', '196, 184, 212'),
                    ('accent', 'Wild Lilac', '--accent', '#B87AA8', '184, 122, 168'),
                    ('border', 'Lavender Border', '--border', '#E0D8E8', '224, 216, 232'),
                    ('success', 'Mint', '--success', '#6BBA8A', '107, 186, 138'),
                    ('warning', 'Honey', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Berry', '--error', '#B86B8A', '184, 107, 138'),
                ]
            },

            # ============================================
            # DARK MOODY PALETTES
            # ============================================
            {
                'name': 'Midnight Study',
                'category': 'dark-moody',
                'mood': 'dark',
                'colors': [
                    ('background', 'Deep Navy', '--background', '#1A2430', '26, 36, 48'),
                    ('text', 'Pale Gray', '--text', '#C8D0D8', '200, 208, 216'),
                    ('heading', 'Brass', '--heading', '#C4A44A', '196, 164, 74'),
                    ('primary', 'Brass', '--primary', '#C4A44A', '196, 164, 74'),
                    ('secondary', 'Slate', '--secondary', '#5A6A7A', '90, 106, 122'),
                    ('accent', 'Burgundy', '--accent', '#8B3A4A', '139, 58, 74'),
                    ('border', 'Dark Border', '--border', '#2A3440', '42, 52, 64'),
                    ('success', 'Forest', '--success', '#2E6B3A', '46, 107, 58'),
                    ('warning', 'Amber', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Crimson', '--error', '#A83A3A', '168, 58, 58'),
                ]
            },
            {
                'name': 'Obsidian',
                'category': 'dark-moody',
                'mood': 'dark',
                'colors': [
                    ('background', 'Obsidian', '--background', '#1A1A1C', '26, 26, 28'),
                    ('text', 'Light Gray', '--text', '#C0C0C4', '192, 192, 196'),
                    ('heading', 'Gold', '--heading', '#C4A44A', '196, 164, 74'),
                    ('primary', 'Gold', '--primary', '#C4A44A', '196, 164, 74'),
                    ('secondary', 'Dark Gray', '--secondary', '#4A4A50', '74, 74, 80'),
                    ('accent', 'Ruby', '--accent', '#C44A5A', '196, 74, 90'),
                    ('border', 'Obsidian Border', '--border', '#2A2A2E', '42, 42, 46'),
                    ('success', 'Emerald', '--success', '#2A8A4A', '42, 138, 74'),
                    ('warning', 'Topaz', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Garnet', '--error', '#B84A4A', '184, 74, 74'),
                ]
            },

            # ============================================
            # VIBRANT POP PALETTES
            # ============================================
            {
                'name': 'Citrus Splash',
                'category': 'vibrant-pop',
                'mood': 'energetic',
                'colors': [
                    ('background', 'Citrus White', '--background', '#FDF8F0', '253, 248, 240'),
                    ('text', 'Citrus Black', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Orange', '--heading', '#E56B2A', '229, 107, 42'),
                    ('primary', 'Orange', '--primary', '#E56B2A', '229, 107, 42'),
                    ('secondary', 'Lemon', '--secondary', '#E5C42A', '229, 196, 42'),
                    ('accent', 'Lime', '--accent', '#6BC42A', '107, 196, 42'),
                    ('border', 'Citrus Border', '--border', '#E0D8C8', '224, 216, 200'),
                    ('success', 'Green Apple', '--success', '#4AC42A', '74, 196, 42'),
                    ('warning', 'Grapefruit', '--warning', '#E58A4A', '229, 138, 74'),
                    ('error', 'Blood Orange', '--error', '#D43A2A', '212, 58, 42'),
                ]
            },
            {
                'name': 'Candy Shop',
                'category': 'vibrant-pop',
                'mood': 'playful',
                'colors': [
                    ('background', 'Candy White', '--background', '#FDF5F8', '253, 245, 248'),
                    ('text', 'Licorice', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Bubblegum', '--heading', '#E56BA8', '229, 107, 168'),
                    ('primary', 'Bubblegum', '--primary', '#E56BA8', '229, 107, 168'),
                    ('secondary', 'Cotton Candy', '--secondary', '#8AC4E5', '138, 196, 229'),
                    ('accent', 'Lemon Drop', '--accent', '#E5D44A', '229, 212, 74'),
                    ('border', 'Candy Border', '--border', '#E8D0D8', '232, 208, 216'),
                    ('success', 'Sour Apple', '--success', '#6BE54A', '107, 229, 74'),
                    ('warning', 'Butterscotch', '--warning', '#E5B44A', '229, 180, 74'),
                    ('error', 'Cherry', '--error', '#E54A5A', '229, 74, 90'),
                ]
            },

            # ============================================
            # LUXURY PALETTES
            # ============================================
            {
                'name': 'Midnight Sapphire',
                'category': 'luxury',
                'mood': 'elegant',
                'colors': [
                    ('background', 'Pearl White', '--background', '#FAFAF8', '250, 250, 248'),
                    ('text', 'Sapphire Ink', '--text', '#1A2436', '26, 36, 54'),
                    ('heading', 'Royal Sapphire', '--heading', '#1A3A6B', '26, 58, 107'),
                    ('primary', 'Royal Sapphire', '--primary', '#1A3A6B', '26, 58, 107'),
                    ('secondary', 'Platinum', '--secondary', '#A8B0C0', '168, 176, 192'),
                    ('accent', 'Rose Gold', '--accent', '#C48A7A', '196, 138, 122'),
                    ('border', 'Silver Mist', '--border', '#D8DCE4', '216, 220, 228'),
                    ('success', 'Jade', '--success', '#1A6B4A', '26, 107, 74'),
                    ('warning', 'Amber', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Burgundy', '--error', '#8B2A3A', '139, 42, 58'),
                ]
            },
            {
                'name': 'Champagne & Caviar',
                'category': 'luxury',
                'mood': 'sophisticated',
                'colors': [
                    ('background', 'Champagne Cream', '--background', '#FCF9F2', '252, 249, 242'),
                    ('text', 'Caviar Black', '--text', '#1E1A18', '30, 26, 24'),
                    ('heading', 'Burnished Gold', '--heading', '#C49A4A', '196, 154, 74'),
                    ('primary', 'Burnished Gold', '--primary', '#C49A4A', '196, 154, 74'),
                    ('secondary', 'Warm Taupe', '--secondary', '#A8907A', '168, 144, 122'),
                    ('accent', 'Pearl', '--accent', '#F0E8D8', '240, 232, 216'),
                    ('border', 'Champagne Border', '--border', '#E8DCC8', '232, 220, 200'),
                    ('success', 'Emerald', '--success', '#1A6B3A', '26, 107, 58'),
                    ('warning', 'Topaz', '--warning', '#D4B06B', '212, 176, 107'),
                    ('error', 'Garnet', '--error', '#9E2A3A', '158, 42, 58'),
                ]
            },

            # ============================================
            # FASHION PALETTES
            # ============================================
            {
                'name': 'Runway Edit',
                'category': 'fashion',
                'mood': 'chic',
                'colors': [
                    ('background', 'Porcelain', '--background', '#F7F5F2', '247, 245, 242'),
                    ('text', 'Runway Black', '--text', '#222222', '34, 34, 34'),
                    ('heading', 'Couture Pink', '--heading', '#D47A8A', '212, 122, 138'),
                    ('primary', 'Couture Pink', '--primary', '#D47A8A', '212, 122, 138'),
                    ('secondary', 'Heather Gray', '--secondary', '#8A8A8A', '138, 138, 138'),
                    ('accent', 'Gold Accent', '--accent', '#C4A44A', '196, 164, 74'),
                    ('border', 'Fashion Border', '--border', '#E0DCD8', '224, 220, 216'),
                    ('success', 'Jade', '--success', '#5AAA7A', '90, 170, 122'),
                    ('warning', 'Topaz', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Garnet', '--error', '#B85A5A', '184, 90, 90'),
                ]
            },
            {
                'name': 'Street Style',
                'category': 'fashion',
                'mood': 'edgy',
                'colors': [
                    ('background', 'Street White', '--background', '#F5F3F0', '245, 243, 240'),
                    ('text', 'Urban Black', '--text', '#1E1E1E', '30, 30, 30'),
                    ('heading', 'Neon Orange', '--heading', '#E56B2A', '229, 107, 42'),
                    ('primary', 'Concrete', '--primary', '#7A7A7A', '122, 122, 122'),
                    ('secondary', 'Denim Blue', '--secondary', '#4A6B8A', '74, 107, 138'),
                    ('accent', 'Neon Orange', '--accent', '#E56B2A', '229, 107, 42'),
                    ('border', 'Street Border', '--border', '#D0CEC8', '208, 206, 200'),
                    ('success', 'Lime', '--success', '#5AC42A', '90, 196, 42'),
                    ('warning', 'Yellow', '--warning', '#D4C02A', '212, 192, 42'),
                    ('error', 'Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },

            # ============================================
            # BEAUTY PALETTES
            # ============================================
            {
                'name': 'Rose Gold Glow',
                'category': 'beauty',
                'mood': 'glamorous',
                'colors': [
                    ('background', 'Blush Cream', '--background', '#FDF5F2', '253, 245, 242'),
                    ('text', 'Rose Brown', '--text', '#4A3535', '74, 53, 53'),
                    ('heading', 'Rose Gold', '--heading', '#C48A7A', '196, 138, 122'),
                    ('primary', 'Rose Gold', '--primary', '#C48A7A', '196, 138, 122'),
                    ('secondary', 'Champagne', '--secondary', '#E8D4C4', '232, 212, 196'),
                    ('accent', 'Coral', '--accent', '#D46B5A', '212, 107, 90'),
                    ('border', 'Rose Border', '--border', '#E8D8D4', '232, 216, 212'),
                    ('success', 'Mint', '--success', '#6BBA8A', '107, 186, 138'),
                    ('warning', 'Peach', '--warning', '#D4A07A', '212, 160, 122'),
                    ('error', 'Berry', '--error', '#B85A6B', '184, 90, 107'),
                ]
            },
            {
                'name': 'Clean Beauty',
                'category': 'beauty',
                'mood': 'natural',
                'colors': [
                    ('background', 'Pure White', '--background', '#FAFAF8', '250, 250, 248'),
                    ('text', 'Botanical Gray', '--text', '#3A4A3A', '58, 74, 58'),
                    ('heading', 'Lavender', '--heading', '#B89EC4', '184, 158, 196'),
                    ('primary', 'Sage', '--primary', '#7A9E7A', '122, 158, 122'),
                    ('secondary', 'Aloe', '--secondary', '#9EC4A0', '158, 196, 160'),
                    ('accent', 'Lavender', '--accent', '#B89EC4', '184, 158, 196'),
                    ('border', 'Clean Border', '--border', '#D8E0D4', '216, 224, 212'),
                    ('success', 'Fresh Mint', '--success', '#5ABA7A', '90, 186, 122'),
                    ('warning', 'Honey', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Rose', '--error', '#C46B7A', '196, 107, 122'),
                ]
            },

            # ============================================
            # TECH PALETTES
            # ============================================
            {
                'name': 'Cyber Tech',
                'category': 'tech',
                'mood': 'futuristic',
                'colors': [
                    ('background', 'Terminal White', '--background', '#F8FAFC', '248, 250, 252'),
                    ('text', 'Code Gray', '--text', '#1E2430', '30, 36, 48'),
                    ('heading', 'Electric Blue', '--heading', '#2A6BC4', '42, 107, 196'),
                    ('primary', 'Electric Blue', '--primary', '#2A6BC4', '42, 107, 196'),
                    ('secondary', 'Dark Matter', '--secondary', '#3A4A6B', '58, 74, 107'),
                    ('accent', 'Neon Cyan', '--accent', '#2AC4C4', '42, 196, 196'),
                    ('border', 'Cyber Border', '--border', '#D0D8E8', '208, 216, 232'),
                    ('success', 'Success Green', '--success', '#2AC46B', '42, 196, 107'),
                    ('warning', 'Alert Orange', '--warning', '#E58A2A', '229, 138, 42'),
                    ('error', 'Error Red', '--error', '#E52A2A', '229, 42, 42'),
                ]
            },
            {
                'name': 'Space Gray',
                'category': 'tech',
                'mood': 'sleek',
                'colors': [
                    ('background', 'Aluminum White', '--background', '#F5F5F5', '245, 245, 245'),
                    ('text', 'Space Gray', '--text', '#2C2C30', '44, 44, 48'),
                    ('heading', 'Apple Blue', '--heading', '#2A6BC4', '42, 107, 196'),
                    ('primary', 'Apple Blue', '--primary', '#2A6BC4', '42, 107, 196'),
                    ('secondary', 'Silver', '--secondary', '#A8ACB4', '168, 172, 180'),
                    ('accent', 'Product Red', '--accent', '#D42A3A', '212, 42, 58'),
                    ('border', 'Space Border', '--border', '#D0D0D4', '208, 208, 212'),
                    ('success', 'Mint', '--success', '#2AC47A', '42, 196, 122'),
                    ('warning', 'Amber', '--warning', '#D49E2A', '212, 158, 42'),
                    ('error', 'Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },

            # ============================================
            # HOME PALETTES
            # ============================================
            {
                'name': 'Modern Living',
                'category': 'home',
                'mood': 'modern',
                'colors': [
                    ('background', 'Living White', '--background', '#F5F3F0', '245, 243, 240'),
                    ('text', 'Charcoal', '--text', '#2C2A28', '44, 42, 40'),
                    ('heading', 'Brass', '--heading', '#C4A44A', '196, 164, 74'),
                    ('primary', 'Walnut', '--primary', '#8A6B4E', '138, 107, 78'),
                    ('secondary', 'Warm Stone', '--secondary', '#9E9284', '158, 146, 132'),
                    ('accent', 'Brass', '--accent', '#C4A44A', '196, 164, 74'),
                    ('border', 'Living Border', '--border', '#D8D4CC', '216, 212, 204'),
                    ('success', 'Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Terracotta', '--warning', '#C46B4A', '196, 107, 74'),
                    ('error', 'Brick', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },
            {
                'name': 'Scandinavian Hygge',
                'category': 'home',
                'mood': 'cozy',
                'colors': [
                    ('background', 'Nordic White', '--background', '#F8F6F2', '248, 246, 242'),
                    ('text', 'Warm Gray', '--text', '#4A4640', '74, 70, 64'),
                    ('heading', 'Dusty Blue', '--heading', '#7A9AB8', '122, 154, 184'),
                    ('primary', 'Dusty Blue', '--primary', '#7A9AB8', '122, 154, 184'),
                    ('secondary', 'Pale Pink', '--secondary', '#D4B8B8', '212, 184, 184'),
                    ('accent', 'Mustard', '--accent', '#D4B44A', '212, 180, 74'),
                    ('border', 'Hygge Border', '--border', '#E0DCD4', '224, 220, 212'),
                    ('success', 'Mint', '--success', '#7AB89E', '122, 184, 158'),
                    ('warning', 'Sand', '--warning', '#D4B88A', '212, 184, 138'),
                    ('error', 'Coral', '--error', '#C47A7A', '196, 122, 122'),
                ]
            },

            # ============================================
            # FOOD PALETTES
            # ============================================
            {
                'name': 'Artisan Coffee',
                'category': 'food',
                'mood': 'warm',
                'colors': [
                    ('background', 'Cream', '--background', '#FDF8F0', '253, 248, 240'),
                    ('text', 'Espresso', '--text', '#3A2A1E', '58, 42, 30'),
                    ('heading', 'Caramel', '--heading', '#D49E5A', '212, 158, 90'),
                    ('primary', 'Coffee', '--primary', '#6B4A3A', '107, 74, 58'),
                    ('secondary', 'Latte', '--secondary', '#C4A484', '196, 164, 132'),
                    ('accent', 'Caramel', '--accent', '#D49E5A', '212, 158, 90'),
                    ('border', 'Coffee Border', '--border', '#E0D4C4', '224, 212, 196'),
                    ('success', 'Matcha', '--success', '#5A9E5A', '90, 158, 90'),
                    ('warning', 'Honey', '--warning', '#D4B44A', '212, 180, 74'),
                    ('error', 'Berry', '--error', '#B85A6B', '184, 90, 107'),
                ]
            },
            {
                'name': 'Organic Grocery',
                'category': 'food',
                'mood': 'fresh',
                'colors': [
                    ('background', 'Fresh White', '--background', '#F5F8F0', '245, 248, 240'),
                    ('text', 'Forest', '--text', '#2A3A2A', '42, 58, 42'),
                    ('heading', 'Fresh Green', '--heading', '#5A9E4A', '90, 158, 74'),
                    ('primary', 'Fresh Green', '--primary', '#5A9E4A', '90, 158, 74'),
                    ('secondary', 'Earth', '--secondary', '#8A6B4A', '138, 107, 74'),
                    ('accent', 'Carrot', '--accent', '#D47A3A', '212, 122, 58'),
                    ('border', 'Grocery Border', '--border', '#D8E0C8', '216, 224, 200'),
                    ('success', 'Lime', '--success', '#6BC42A', '107, 196, 42'),
                    ('warning', 'Lemon', '--warning', '#D4C42A', '212, 196, 42'),
                    ('error', 'Tomato', '--error', '#D44A3A', '212, 74, 58'),
                ]
            },

            # ============================================
            # PET PALETTES
            # ============================================
            {
                'name': 'Pet Paradise',
                'category': 'pet',
                'mood': 'playful',
                'colors': [
                    ('background', 'Paradise White', '--background', '#F5F8F5', '245, 248, 245'),
                    ('text', 'Forest Brown', '--text', '#3A3A2A', '58, 58, 42'),
                    ('heading', 'Sky Blue', '--heading', '#6BA5C4', '107, 165, 196'),
                    ('primary', 'Sky Blue', '--primary', '#6BA5C4', '107, 165, 196'),
                    ('secondary', 'Grass Green', '--secondary', '#6B9E4A', '107, 158, 74'),
                    ('accent', 'Bone', '--accent', '#E8DCC4', '232, 220, 196'),
                    ('border', 'Pet Border', '--border', '#D0D8D0', '208, 216, 208'),
                    ('success', 'Fresh Grass', '--success', '#5AC45A', '90, 196, 90'),
                    ('warning', 'Tennis Ball', '--warning', '#D4C42A', '212, 196, 42'),
                    ('error', 'Collar Red', '--error', '#D44A4A', '212, 74, 74'),
                ]
            },
            {
                'name': 'Cat & Cozy',
                'category': 'pet',
                'mood': 'cozy',
                'colors': [
                    ('background', 'Cozy Cream', '--background', '#FDF8F2', '253, 248, 242'),
                    ('text', 'Whisker Gray', '--text', '#4A4440', '74, 68, 64'),
                    ('heading', 'Lavender', '--heading', '#B89EC4', '184, 158, 196'),
                    ('primary', 'Lavender', '--primary', '#B89EC4', '184, 158, 196'),
                    ('secondary', 'Mauve', '--secondary', '#C4A0B8', '196, 160, 184'),
                    ('accent', 'Peach', '--accent', '#D4A88A', '212, 168, 138'),
                    ('border', 'Cozy Border', '--border', '#E0D8D4', '224, 216, 212'),
                    ('success', 'Catnip Green', '--success', '#6BBA7A', '107, 186, 122'),
                    ('warning', 'Tuna', '--warning', '#D4B06B', '212, 176, 107'),
                    ('error', 'Scratch Red', '--error', '#C46B6B', '196, 107, 107'),
                ]
            },

            # ============================================
            # SPORTS PALETTES
            # ============================================
            {
                'name': 'Athletic Performance',
                'category': 'sports',
                'mood': 'energetic',
                'colors': [
                    ('background', 'Performance White', '--background', '#F5F7F8', '245, 247, 248'),
                    ('text', 'Navy', '--text', '#1A2436', '26, 36, 54'),
                    ('heading', 'Energy Red', '--heading', '#D42A3A', '212, 42, 58'),
                    ('primary', 'Team Navy', '--primary', '#1A3A6B', '26, 58, 107'),
                    ('secondary', 'Silver', '--secondary', '#A8B0C0', '168, 176, 192'),
                    ('accent', 'Energy Red', '--accent', '#D42A3A', '212, 42, 58'),
                    ('border', 'Performance Border', '--border', '#D0D8E0', '208, 216, 224'),
                    ('success', 'Finish Green', '--success', '#2AC45A', '42, 196, 90'),
                    ('warning', 'Caution Orange', '--warning', '#E58A2A', '229, 138, 42'),
                    ('error', 'Stop Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },
            {
                'name': 'Outdoor Adventure',
                'category': 'sports',
                'mood': 'adventurous',
                'colors': [
                    ('background', 'Trail White', '--background', '#F5F2EA', '245, 242, 234'),
                    ('text', 'Forest', '--text', '#2A3A2A', '42, 58, 42'),
                    ('heading', 'Sunset Orange', '--heading', '#D47A3A', '212, 122, 58'),
                    ('primary', 'Pine Green', '--primary', '#3A6B3A', '58, 107, 58'),
                    ('secondary', 'Trail Brown', '--secondary', '#7A5A3A', '122, 90, 58'),
                    ('accent', 'Sunset Orange', '--accent', '#D47A3A', '212, 122, 58'),
                    ('border', 'Trail Border', '--border', '#D8D4C4', '216, 212, 196'),
                    ('success', 'Meadow', '--success', '#4A9E4A', '74, 158, 74'),
                    ('warning', 'Signal Yellow', '--warning', '#D4C42A', '212, 196, 42'),
                    ('error', 'Emergency Red', '--error', '#C44A4A', '196, 74, 74'),
                ]
            },

            # ============================================
            # TOYS PALETTES
            # ============================================
            {
                'name': 'Rainbow Fun',
                'category': 'toys',
                'mood': 'playful',
                'colors': [
                    ('background', 'Cloud White', '--background', '#F8FAFC', '248, 250, 252'),
                    ('text', 'Playful Navy', '--text', '#2A3A5A', '42, 58, 90'),
                    ('heading', 'Toy Red', '--heading', '#E54A5A', '229, 74, 90'),
                    ('primary', 'Toy Red', '--primary', '#E54A5A', '229, 74, 90'),
                    ('secondary', 'Block Blue', '--secondary', '#4A8AE5', '74, 138, 229'),
                    ('accent', 'Crayon Yellow', '--accent', '#E5C44A', '229, 196, 74'),
                    ('border', 'Toy Border', '--border', '#D8D8E0', '216, 216, 224'),
                    ('success', 'Green Crayon', '--success', '#4AE56B', '74, 229, 107'),
                    ('warning', 'Orange Crayon', '--warning', '#E58A4A', '229, 138, 74'),
                    ('error', 'Red Crayon', '--error', '#E54A4A', '229, 74, 74'),
                ]
            },
            {
                'name': 'Baby Store',
                'category': 'toys',
                'mood': 'gentle',
                'colors': [
                    ('background', 'Baby White', '--background', '#FDF8F8', '253, 248, 248'),
                    ('text', 'Soft Gray', '--text', '#4A4444', '74, 68, 68'),
                    ('heading', 'Baby Blue', '--heading', '#8AC4E5', '138, 196, 229'),
                    ('primary', 'Baby Blue', '--primary', '#8AC4E5', '138, 196, 229'),
                    ('secondary', 'Baby Pink', '--secondary', '#E5B8C4', '229, 184, 196'),
                    ('accent', 'Mint', '--accent', '#7AE5B8', '122, 229, 184'),
                    ('border', 'Baby Border', '--border', '#E0D8D8', '224, 216, 216'),
                    ('success', 'Soft Green', '--success', '#7AC47A', '122, 196, 122'),
                    ('warning', 'Soft Yellow', '--warning', '#E5D47A', '229, 212, 122'),
                    ('error', 'Soft Coral', '--error', '#E58A8A', '229, 138, 138'),
                ]
            },

            # ============================================
            # HEALTH PALETTES
            # ============================================
            {
                'name': 'Pharmacy',
                'category': 'health',
                'mood': 'trustworthy',
                'colors': [
                    ('background', 'Pharmacy White', '--background', '#F5F8FA', '245, 248, 250'),
                    ('text', 'Medical Navy', '--text', '#1A2A4A', '26, 42, 74'),
                    ('heading', 'Medical Blue', '--heading', '#2A6BC4', '42, 107, 196'),
                    ('primary', 'Medical Blue', '--primary', '#2A6BC4', '42, 107, 196'),
                    ('secondary', 'Sterile White', '--secondary', '#FAFAFA', '250, 250, 250'),
                    ('accent', 'Healing Green', '--accent', '#2A9E5A', '42, 158, 90'),
                    ('border', 'Pharmacy Border', '--border', '#D0D8E8', '208, 216, 232'),
                    ('success', 'Recovery Green', '--success', '#2AC45A', '42, 196, 90'),
                    ('warning', 'Caution Orange', '--warning', '#E58A2A', '229, 138, 42'),
                    ('error', 'Emergency Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },
            {
                'name': 'Natural Supplements',
                'category': 'health',
                'mood': 'organic',
                'colors': [
                    ('background', 'Natural White', '--background', '#F5F5EE', '245, 245, 238'),
                    ('text', 'Herbal Brown', '--text', '#3A3A2A', '58, 58, 42'),
                    ('heading', 'Sage', '--heading', '#7A9E7A', '122, 158, 122'),
                    ('primary', 'Sage', '--primary', '#7A9E7A', '122, 158, 122'),
                    ('secondary', 'Earth', '--secondary', '#8A6B4A', '138, 107, 74'),
                    ('accent', 'Botanical Orange', '--accent', '#D47A3A', '212, 122, 58'),
                    ('border', 'Natural Border', '--border', '#D8D8C8', '216, 216, 200'),
                    ('success', 'Leaf Green', '--success', '#5A9E4A', '90, 158, 74'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Berry Red', '--error', '#C45A5A', '196, 90, 90'),
                ]
            },
        ]