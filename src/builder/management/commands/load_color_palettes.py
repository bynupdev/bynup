# builder/management/commands/load_color_palettes.py

from django.core.management.base import BaseCommand
from builder.models import ColorPalette, ColorPaletteColor

class Command(BaseCommand):
    help = 'Load 70 premium editorial/app-style color palettes'

    def handle(self, *args, **options):
        self.stdout.write('Loading premium color palettes...')
        
        # Clear existing palettes (optional - uncomment if needed)
        # ColorPalette.objects.all().delete()
        # ColorPaletteColor.objects.all().delete()

        # ============================================
        # PREMIUM PALETTES - Organized by Filterable Categories
        # Order: background, text, heading, primary, secondary, accent, border, success, warning, error
        # ============================================
        
        palettes = [
            # ============================================
            # CATEGORY: warm-minimal (8 palettes)
            # Warm neutrals with terracotta, sand, clay tones
            # ============================================
            {
                'name': 'Warm Studio',
                'category': 'warm-minimal',
                'mood': 'warm',
                'colors': [
                    ('background', 'Studio White', '--background', '#FAF6F2', '250, 246, 242'),
                    ('text', 'Warm Charcoal', '--text', '#3D362E', '61, 54, 46'),
                    ('heading', 'Roasted Brown', '--heading', '#2B231C', '43, 35, 28'),
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
                    ('heading', 'Dark Cocoa', '--heading', '#352A24', '53, 42, 36'),
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
                    ('heading', 'Deep Clay', '--heading', '#45382E', '69, 56, 46'),
                    ('primary', 'Burnt Sienna', '--primary', '#B86E4E', '184, 110, 78'),
                    ('secondary', 'Warm Sand', '--secondary', '#9E8A74', '158, 138, 116'),
                    ('accent', 'Coral Clay', '--accent', '#C46E5E', '196, 110, 94'),
                    ('border', 'Clay Border', '--border', '#E8DCD0', '232, 220, 208'),
                    ('success', 'Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Golden Clay', '--warning', '#C49A5A', '196, 154, 90'),
                    ('error', 'Deep Coral', '--error', '#B85A4E', '184, 90, 78'),
                ]
            },
            {
                'name': 'Sand Dune',
                'category': 'warm-minimal',
                'mood': 'warm',
                'colors': [
                    ('background', 'Dune White', '--background', '#F8F4EE', '248, 244, 238'),
                    ('text', 'Dune Brown', '--text', '#5A4D42', '90, 77, 66'),
                    ('heading', 'Deep Dune', '--heading', '#453A30', '69, 58, 48'),
                    ('primary', 'Sandstone', '--primary', '#B88A6A', '184, 138, 106'),
                    ('secondary', 'Warm Beige', '--secondary', '#A89884', '168, 152, 132'),
                    ('accent', 'Desert Rose', '--accent', '#C47A6A', '196, 122, 106'),
                    ('border', 'Dune Border', '--border', '#E8DED4', '232, 222, 212'),
                    ('success', 'Desert Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Desert Gold', '--warning', '#C49A5A', '196, 154, 90'),
                    ('error', 'Desert Red', '--error', '#B86A5A', '184, 106, 90'),
                ]
            },
            {
                'name': 'Warm Parchment',
                'category': 'warm-minimal',
                'mood': 'classic',
                'colors': [
                    ('background', 'Aged Parchment', '--background', '#F5EFE6', '245, 239, 230'),
                    ('text', 'Sepia Ink', '--text', '#4A4035', '74, 64, 53'),
                    ('heading', 'Deep Sepia', '--heading', '#3A3025', '58, 48, 37'),
                    ('primary', 'Vintage Copper', '--primary', '#A86E4E', '168, 110, 78'),
                    ('secondary', 'Warm Gray', '--secondary', '#8A7E72', '138, 126, 114'),
                    ('accent', 'Aged Gold', '--accent', '#B8985E', '184, 152, 94'),
                    ('border', 'Parchment Border', '--border', '#E0D8CC', '224, 216, 204'),
                    ('success', 'Olive', '--success', '#6B8A5E', '107, 138, 94'),
                    ('warning', 'Amber', '--warning', '#C49A4E', '196, 154, 78'),
                    ('error', 'Crimson', '--error', '#A84E4A', '168, 78, 74'),
                ]
            },
            {
                'name': 'Linen & Leather',
                'category': 'warm-minimal',
                'mood': 'textured',
                'colors': [
                    ('background', 'Natural Linen', '--background', '#F6F2EA', '246, 242, 234'),
                    ('text', 'Leather Brown', '--text', '#4A3F35', '74, 63, 53'),
                    ('heading', 'Dark Leather', '--heading', '#362C23', '54, 44, 35'),
                    ('primary', 'Cognac', '--primary', '#9E6E4E', '158, 110, 78'),
                    ('secondary', 'Warm Khaki', '--secondary', '#8A826E', '138, 130, 110'),
                    ('accent', 'Auburn', '--accent', '#A55A4A', '165, 90, 74'),
                    ('border', 'Linen Border', '--border', '#E0D8CC', '224, 216, 204'),
                    ('success', 'Herb Green', '--success', '#6B8A5E', '107, 138, 94'),
                    ('warning', 'Golden Brown', '--warning', '#B88A4E', '184, 138, 78'),
                    ('error', 'Rust Red', '--error', '#A54A3E', '165, 74, 62'),
                ]
            },
            {
                'name': 'Tuscan Earth',
                'category': 'warm-minimal',
                'mood': 'rustic',
                'colors': [
                    ('background', 'Tuscan Cream', '--background', '#F8F2E8', '248, 242, 232'),
                    ('text', 'Earth Brown', '--text', '#5A4A38', '90, 74, 56'),
                    ('heading', 'Rich Earth', '--heading', '#453828', '69, 56, 40'),
                    ('primary', 'Tuscan Red', '--primary', '#A85E4E', '168, 94, 78'),
                    ('secondary', 'Warm Olive', '--secondary', '#7A8A5E', '122, 138, 94'),
                    ('accent', 'Sunflower', '--accent', '#C49A4A', '196, 154, 74'),
                    ('border', 'Tuscan Border', '--border', '#E8DCC8', '232, 220, 200'),
                    ('success', 'Herb', '--success', '#6B9E6B', '107, 158, 107'),
                    ('warning', 'Golden', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Tomato', '--error', '#B85A4A', '184, 90, 74'),
                ]
            },
            {
                'name': 'Warm Gallery',
                'category': 'warm-minimal',
                'mood': 'minimal',
                'colors': [
                    ('background', 'Gallery White', '--background', '#FAFAF8', '250, 250, 248'),
                    ('text', 'Soft Black', '--text', '#2A2A28', '42, 42, 40'),
                    ('heading', 'Deep Charcoal', '--heading', '#1F1F1D', '31, 31, 29'),
                    ('primary', 'Faded Terracotta', '--primary', '#B88A7A', '184, 138, 122'),
                    ('secondary', 'Warm Stone', '--secondary', '#9E928A', '158, 146, 138'),
                    ('accent', 'Dusty Rose', '--accent', '#C4807A', '196, 128, 122'),
                    ('border', 'Gallery Border', '--border', '#E5E5E0', '229, 229, 224'),
                    ('success', 'Sage Green', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Warm Ochre', '--warning', '#C49A5A', '196, 154, 90'),
                    ('error', 'Muted Red', '--error', '#B86A5E', '184, 106, 94'),
                ]
            },

            # ============================================
            # CATEGORY: cool-minimal (8 palettes)
            # Cool neutrals with slate, mist, nordic tones
            # ============================================
            {
                'name': 'Nordic Light',
                'category': 'cool-minimal',
                'mood': 'cool',
                'colors': [
                    ('background', 'Nordic White', '--background', '#F2F5F8', '242, 245, 248'),
                    ('text', 'Fjord Gray', '--text', '#3A4450', '58, 68, 80'),
                    ('heading', 'Deep Fjord', '--heading', '#2A3440', '42, 52, 64'),
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
                    ('heading', 'Deep Navy', '--heading', '#1A2430', '26, 36, 48'),
                    ('primary', 'Steel Blue', '--primary', '#5A7A9E', '90, 122, 158'),
                    ('secondary', 'Cool Gray', '--secondary', '#7A8A9E', '122, 138, 158'),
                    ('accent', 'Cornflower', '--accent', '#6B8FCE', '107, 143, 206'),
                    ('border', 'Cool Border', '--border', '#DCE2EA', '220, 226, 234'),
                    ('success', 'Teal', '--success', '#4A9E8F', '74, 158, 143'),
                    ('warning', 'Marigold', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Cool Red', '--error', '#CE6B6B', '206, 107, 107'),
                ]
            },
            {
                'name': 'Mist & Stone',
                'category': 'cool-minimal',
                'mood': 'calm',
                'colors': [
                    ('background', 'Morning Mist', '--background', '#F0F4F8', '240, 244, 248'),
                    ('text', 'Stone Gray', '--text', '#4A5664', '74, 86, 100'),
                    ('heading', 'Deep Stone', '--heading', '#384454', '56, 68, 84'),
                    ('primary', 'Slate Blue', '--primary', '#6B8AA8', '107, 138, 168'),
                    ('secondary', 'Mist Gray', '--secondary', '#9EACBC', '158, 172, 188'),
                    ('accent', 'Sky Blue', '--accent', '#7AAFCE', '122, 175, 206'),
                    ('border', 'Mist Border', '--border', '#D8E2EC', '216, 226, 236'),
                    ('success', 'Seafoam', '--success', '#6BBA9E', '107, 186, 158'),
                    ('warning', 'Sand', '--warning', '#CEB47A', '206, 180, 122'),
                    ('error', 'Muted Coral', '--error', '#CE8A8A', '206, 138, 138'),
                ]
            },
            {
                'name': 'Clean Slate',
                'category': 'cool-minimal',
                'mood': 'clean',
                'colors': [
                    ('background', 'Clean White', '--background', '#F8FAFC', '248, 250, 252'),
                    ('text', 'Slate Text', '--text', '#344054', '52, 64, 84'),
                    ('heading', 'Deep Slate', '--heading', '#1E293B', '30, 41, 59'),
                    ('primary', 'Slate Blue', '--primary', '#475569', '71, 85, 105'),
                    ('secondary', 'Light Slate', '--secondary', '#94A3B8', '148, 163, 184'),
                    ('accent', 'Accent Blue', '--accent', '#3B82F6', '59, 130, 246'),
                    ('border', 'Slate Border', '--border', '#CBD5E1', '203, 213, 225'),
                    ('success', 'Emerald', '--success', '#10B981', '16, 185, 129'),
                    ('warning', 'Amber', '--warning', '#F59E0B', '245, 158, 11'),
                    ('error', 'Rose', '--error', '#EF4444', '239, 68, 68'),
                ]
            },
            {
                'name': 'Coastal Mist',
                'category': 'cool-minimal',
                'mood': 'calm',
                'colors': [
                    ('background', 'Sea Mist', '--background', '#F0F5F8', '240, 245, 248'),
                    ('text', 'Coastal Gray', '--text', '#4A5A68', '74, 90, 104'),
                    ('heading', 'Deep Water', '--heading', '#2A4050', '42, 64, 80'),
                    ('primary', 'Ocean Blue', '--primary', '#3A7A9E', '58, 122, 158'),
                    ('secondary', 'Driftwood', '--secondary', '#8A9AA8', '138, 154, 168'),
                    ('accent', 'Coral', '--accent', '#CE7A7A', '206, 122, 122'),
                    ('border', 'Coastal Border', '--border', '#D0DEE8', '208, 222, 232'),
                    ('success', 'Kelp', '--success', '#4A9E7A', '74, 158, 122'),
                    ('warning', 'Sand Dollar', '--warning', '#D4B87A', '212, 184, 122'),
                    ('error', 'Starfish', '--error', '#CE7A5A', '206, 122, 90'),
                ]
            },
            {
                'name': 'Alpine Fresh',
                'category': 'cool-minimal',
                'mood': 'fresh',
                'colors': [
                    ('background', 'Alpine Snow', '--background', '#F5F8FA', '245, 248, 250'),
                    ('text', 'Alpine Rock', '--text', '#3A4A5A', '58, 74, 90'),
                    ('heading', 'Deep Alpine', '--heading', '#2A3A4A', '42, 58, 74'),
                    ('primary', 'Alpine Lake', '--primary', '#4A7A8A', '74, 122, 138'),
                    ('secondary', 'Mountain Gray', '--secondary', '#7A8A9A', '122, 138, 154'),
                    ('accent', 'Wildflower', '--accent', '#9E6B8A', '158, 107, 138'),
                    ('border', 'Alpine Border', '--border', '#D8E2EA', '216, 226, 234'),
                    ('success', 'Meadow', '--success', '#5A9E6B', '90, 158, 107'),
                    ('warning', 'Sunlight', '--warning', '#D4B45A', '212, 180, 90'),
                    ('error', 'Alpine Berry', '--error', '#C46B6B', '196, 107, 107'),
                ]
            },
            {
                'name': 'Modernist Gray',
                'category': 'cool-minimal',
                'mood': 'minimal',
                'colors': [
                    ('background', 'Modernist White', '--background', '#F6F8F9', '246, 248, 249'),
                    ('text', 'Modernist Charcoal', '--text', '#3A424A', '58, 66, 74'),
                    ('heading', 'Deep Modernist', '--heading', '#2A323A', '42, 50, 58'),
                    ('primary', 'Architectural Gray', '--primary', '#6A7A8A', '106, 122, 138'),
                    ('secondary', 'Concrete', '--secondary', '#9AACBC', '154, 172, 188'),
                    ('accent', 'Design Blue', '--accent', '#4A8ACE', '74, 138, 206'),
                    ('border', 'Modernist Border', '--border', '#D8E0E6', '216, 224, 230'),
                    ('success', 'Minimal Green', '--success', '#5AAA7A', '90, 170, 122'),
                    ('warning', 'Minimal Gold', '--warning', '#D4B86A', '212, 184, 106'),
                    ('error', 'Minimal Red', '--error', '#CE6A6A', '206, 106, 106'),
                ]
            },
            {
                'name': 'Frost & Shadow',
                'category': 'cool-minimal',
                'mood': 'crisp',
                'colors': [
                    ('background', 'Frost White', '--background', '#F0F4F8', '240, 244, 248'),
                    ('text', 'Shadow Gray', '--text', '#3A4858', '58, 72, 88'),
                    ('heading', 'Deep Shadow', '--heading', '#2A3848', '42, 56, 72'),
                    ('primary', 'Glacier Blue', '--primary', '#4A7A9E', '74, 122, 158'),
                    ('secondary', 'Frost Gray', '--secondary', '#8AA0B4', '138, 160, 180'),
                    ('accent', 'Ice Blue', '--accent', '#5AAFCE', '90, 175, 206'),
                    ('border', 'Frost Border', '--border', '#D0DCE8', '208, 220, 232'),
                    ('success', 'Evergreen', '--success', '#4A9E6B', '74, 158, 107'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Crimson', '--error', '#CE5A5A', '206, 90, 90'),
                ]
            },

            # ============================================
            # CATEGORY: bold-editorial (8 palettes)
            # High contrast, magazine-style, dramatic
            # ============================================
            {
                'name': 'Magazine Cover',
                'category': 'bold-editorial',
                'mood': 'dramatic',
                'colors': [
                    ('background', 'Magazine White', '--background', '#FCFCFA', '252, 252, 250'),
                    ('text', 'Magazine Black', '--text', '#1E1E20', '30, 30, 32'),
                    ('heading', 'Cover Black', '--heading', '#141416', '20, 20, 22'),
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
                    ('heading', 'Absolute Black', '--heading', '#121214', '18, 18, 20'),
                    ('primary', 'Vermilion', '--primary', '#E74C3C', '231, 76, 60'),
                    ('secondary', 'Slate', '--secondary', '#5A6C7A', '90, 108, 122'),
                    ('accent', 'Turquoise', '--accent', '#1ABC9C', '26, 188, 156'),
                    ('border', 'Bold Border', '--border', '#D5D5D8', '213, 213, 216'),
                    ('success', 'Shamrock', '--success', '#27AE60', '39, 174, 96'),
                    ('warning', 'Marigold', '--warning', '#F39C12', '243, 156, 18'),
                    ('error', 'Alizarin', '--error', '#C0392B', '192, 57, 43'),
                ]
            },
            {
                'name': 'Editorial Pop',
                'category': 'bold-editorial',
                'mood': 'vibrant',
                'colors': [
                    ('background', 'Bright Paper', '--background', '#FDFBF7', '253, 251, 247'),
                    ('text', 'Rich Black', '--text', '#1A1A1A', '26, 26, 26'),
                    ('heading', 'Deepest Black', '--heading', '#0F0F0F', '15, 15, 15'),
                    ('primary', 'Vibrant Coral', '--primary', '#FF6B6B', '255, 107, 107'),
                    ('secondary', 'Warm Gray', '--secondary', '#6B7B8B', '107, 123, 139'),
                    ('accent', 'Electric Blue', '--accent', '#4ECDC4', '78, 205, 196'),
                    ('border', 'Pop Border', '--border', '#E0E0E0', '224, 224, 224'),
                    ('success', 'Fresh Green', '--success', '#2ECC71', '46, 204, 113'),
                    ('warning', 'Sunflower', '--warning', '#F1C40F', '241, 196, 15'),
                    ('error', 'Vibrant Red', '--error', '#E74C3C', '231, 76, 60'),
                ]
            },
            {
                'name': 'Art Direction',
                'category': 'bold-editorial',
                'mood': 'creative',
                'colors': [
                    ('background', 'Studio Paper', '--background', '#F9F8F6', '249, 248, 246'),
                    ('text', 'Artist Black', '--text', '#232323', '35, 35, 35'),
                    ('heading', 'Canvas Black', '--heading', '#181818', '24, 24, 24'),
                    ('primary', 'Cadmium Red', '--primary', '#E74C3C', '231, 76, 60'),
                    ('secondary', 'Payne\'s Gray', '--secondary', '#536878', '83, 104, 120'),
                    ('accent', 'Cerulean', '--accent', '#3498DB', '52, 152, 219'),
                    ('border', 'Art Border', '--border', '#D4D4D2', '212, 212, 210'),
                    ('success', 'Viridian', '--success', '#2ECC71', '46, 204, 113'),
                    ('warning', 'Yellow Ochre', '--warning', '#F1C40F', '241, 196, 15'),
                    ('error', 'Alizarin Crimson', '--error', '#E74C3C', '231, 76, 60'),
                ]
            },
            {
                'name': 'Fashion Editorial',
                'category': 'bold-editorial',
                'mood': 'chic',
                'colors': [
                    ('background', 'Porcelain', '--background', '#F7F5F2', '247, 245, 242'),
                    ('text', 'Chic Black', '--text', '#252525', '37, 37, 37'),
                    ('heading', 'Runway Black', '--heading', '#1A1A1A', '26, 26, 26'),
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
                'name': 'Monochrome Drama',
                'category': 'bold-editorial',
                'mood': 'dramatic',
                'colors': [
                    ('background', 'Pure White', '--background', '#FAFAFA', '250, 250, 250'),
                    ('text', 'Rich Black', '--text', '#1A1A1C', '26, 26, 28'),
                    ('heading', 'Deepest Black', '--heading', '#0D0D0F', '13, 13, 15'),
                    ('primary', 'Graphite', '--primary', '#4A4A50', '74, 74, 80'),
                    ('secondary', 'Silver', '--secondary', '#A0A0A8', '160, 160, 168'),
                    ('accent', 'Neon Yellow', '--accent', '#E5E04A', '229, 224, 74'),
                    ('border', 'Mono Border', '--border', '#D0D0D4', '208, 208, 212'),
                    ('success', 'Forest', '--success', '#2E7D32', '46, 125, 50'),
                    ('warning', 'Amber', '--warning', '#FF8F00', '255, 143, 0'),
                    ('error', 'Crimson', '--error', '#C62828', '198, 40, 40'),
                ]
            },
            {
                'name': 'Digital Native',
                'category': 'bold-editorial',
                'mood': 'modern',
                'colors': [
                    ('background', 'Screen White', '--background', '#FCFCFC', '252, 252, 252'),
                    ('text', 'Digital Black', '--text', '#1E1E24', '30, 30, 36'),
                    ('heading', 'App Black', '--heading', '#14141A', '20, 20, 26'),
                    ('primary', 'App Blue', '--primary', '#3B82F6', '59, 130, 246'),
                    ('secondary', 'Interface Gray', '--secondary', '#6B7280', '107, 114, 128'),
                    ('accent', 'Notification Red', '--accent', '#EF4444', '239, 68, 68'),
                    ('border', 'Digital Border', '--border', '#E5E7EB', '229, 231, 235'),
                    ('success', 'Success Green', '--success', '#10B981', '16, 185, 129'),
                    ('warning', 'Warning Orange', '--warning', '#F59E0B', '245, 158, 11'),
                    ('error', 'Error Red', '--error', '#EF4444', '239, 68, 68'),
                ]
            },
            {
                'name': 'SaaS Modern',
                'category': 'bold-editorial',
                'mood': 'professional',
                'colors': [
                    ('background', 'SaaS White', '--background', '#F9FAFB', '249, 250, 251'),
                    ('text', 'SaaS Slate', '--text', '#1F2937', '31, 41, 55'),
                    ('heading', 'Deep Slate', '--heading', '#111827', '17, 24, 39'),
                    ('primary', 'Indigo', '--primary', '#4F46E5', '79, 70, 229'),
                    ('secondary', 'Cool Gray', '--secondary', '#6B7280', '107, 114, 128'),
                    ('accent', 'Sky Blue', '--accent', '#0EA5E9', '14, 165, 233'),
                    ('border', 'SaaS Border', '--border', '#E5E7EB', '229, 231, 235'),
                    ('success', 'Emerald', '--success', '#059669', '5, 150, 105'),
                    ('warning', 'Amber', '--warning', '#D97706', '217, 119, 6'),
                    ('error', 'Rose', '--error', '#E11D48', '225, 29, 72'),
                ]
            },

            # ============================================
            # CATEGORY: elegant-luxury (8 palettes)
            # Gold, bone, champagne, sophisticated
            # ============================================
            {
                'name': 'Champagne Gold',
                'category': 'elegant-luxury',
                'mood': 'luxurious',
                'colors': [
                    ('background', 'Champagne', '--background', '#FDF8F0', '253, 248, 240'),
                    ('text', 'Rich Espresso', '--text', '#3A2A2A', '58, 42, 42'),
                    ('heading', 'Deep Caviar', '--heading', '#1A1212', '26, 18, 18'),
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
                    ('heading', 'Aged Bronze', '--heading', '#3A3028', '58, 48, 40'),
                    ('primary', 'Burnished Bronze', '--primary', '#A87A5E', '168, 122, 94'),
                    ('secondary', 'Warm Pewter', '--secondary', '#8B7D72', '139, 125, 114'),
                    ('accent', 'Patina', '--accent', '#6B8F7C', '107, 143, 124'),
                    ('border', 'Bone Border', '--border', '#E5DDD4', '229, 221, 212'),
                    ('success', 'Verdigris', '--success', '#5A8F7A', '90, 143, 122'),
                    ('warning', 'Ochre', '--warning', '#C49A4A', '196, 154, 74'),
                    ('error', 'Aged Red', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },
            {
                'name': 'Velvet Noir',
                'category': 'elegant-luxury',
                'mood': 'glamorous',
                'colors': [
                    ('background', 'Velvet Cream', '--background', '#FDF5F0', '253, 245, 240'),
                    ('text', 'Noir Black', '--text', '#1E1A1A', '30, 26, 26'),
                    ('heading', 'Deep Noir', '--heading', '#141010', '20, 16, 16'),
                    ('primary', 'Burgundy', '--primary', '#8B3A4A', '139, 58, 74'),
                    ('secondary', 'Mauve', '--secondary', '#9E7A8A', '158, 122, 138'),
                    ('accent', 'Gold Thread', '--accent', '#C4A44A', '196, 164, 74'),
                    ('border', 'Velvet Border', '--border', '#E0D0D0', '224, 208, 208'),
                    ('success', 'Emerald', '--success', '#2E8B57', '46, 139, 87'),
                    ('warning', 'Amber', '--warning', '#D4A04A', '212, 160, 74'),
                    ('error', 'Ruby', '--error', '#9B1D2D', '155, 29, 45'),
                ]
            },
            {
                'name': 'Pearl Essence',
                'category': 'elegant-luxury',
                'mood': 'refined',
                'colors': [
                    ('background', 'Pearl White', '--background', '#FAF8F5', '250, 248, 245'),
                    ('text', 'Pearl Gray', '--text', '#4A4440', '74, 68, 64'),
                    ('heading', 'Deep Pearl', '--heading', '#3A3430', '58, 52, 48'),
                    ('primary', 'Iridescent Blue', '--primary', '#7A9EB8', '122, 158, 184'),
                    ('secondary', 'Warm Silver', '--secondary', '#A8A09A', '168, 160, 154'),
                    ('accent', 'Rose Gold', '--accent', '#C48A8A', '196, 138, 138'),
                    ('border', 'Pearl Border', '--border', '#E5E0DC', '229, 224, 220'),
                    ('success', 'Seafoam', '--success', '#6BA89A', '107, 168, 154'),
                    ('warning', 'Champagne', '--warning', '#D4B87A', '212, 184, 122'),
                    ('error', 'Coral', '--error', '#CE7A7A', '206, 122, 122'),
                ]
            },
            {
                'name': 'Onyx & Gold',
                'category': 'elegant-luxury',
                'mood': 'sophisticated',
                'colors': [
                    ('background', 'Warm White', '--background', '#FAF6F2', '250, 246, 242'),
                    ('text', 'Onyx Black', '--text', '#2A2624', '42, 38, 36'),
                    ('heading', 'Deep Onyx', '--heading', '#1A1614', '26, 22, 20'),
                    ('primary', 'Matte Black', '--primary', '#3A3A3A', '58, 58, 58'),
                    ('secondary', 'Warm Gray', '--secondary', '#8A827A', '138, 130, 122'),
                    ('accent', 'Gold Leaf', '--accent', '#C4A44A', '196, 164, 74'),
                    ('border', 'Onyx Border', '--border', '#E0DCD8', '224, 220, 216'),
                    ('success', 'Forest', '--success', '#2E5E3B', '46, 94, 59'),
                    ('warning', 'Bronze', '--warning', '#B87A3A', '184, 122, 58'),
                    ('error', 'Deep Red', '--error', '#8B2A2A', '139, 42, 42'),
                ]
            },
            {
                'name': 'Silk Route',
                'category': 'elegant-luxury',
                'mood': 'exotic',
                'colors': [
                    ('background', 'Silk White', '--background', '#FCF8F2', '252, 248, 242'),
                    ('text', 'Spice Brown', '--text', '#4A3A2A', '74, 58, 42'),
                    ('heading', 'Deep Spice', '--heading', '#3A2A1A', '58, 42, 26'),
                    ('primary', 'Saffron', '--primary', '#D4A44A', '212, 164, 74'),
                    ('secondary', 'Cinnamon', '--secondary', '#A87A5A', '168, 122, 90'),
                    ('accent', 'Indigo', '--accent', '#4A5A8A', '74, 90, 138'),
                    ('border', 'Silk Border', '--border', '#E8DCC8', '232, 220, 200'),
                    ('success', 'Cardamom', '--success', '#5A9E6B', '90, 158, 107'),
                    ('warning', 'Turmeric', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Chili', '--error', '#B85A4A', '184, 90, 74'),
                ]
            },
            {
                'name': 'Marble & Brass',
                'category': 'elegant-luxury',
                'mood': 'refined',
                'colors': [
                    ('background', 'Marble White', '--background', '#F5F5F2', '245, 245, 242'),
                    ('text', 'Brass Brown', '--text', '#4A4238', '74, 66, 56'),
                    ('heading', 'Deep Marble', '--heading', '#3A3228', '58, 50, 40'),
                    ('primary', 'Aged Brass', '--primary', '#B8985E', '184, 152, 94'),
                    ('secondary', 'Warm Stone', '--secondary', '#9E9284', '158, 146, 132'),
                    ('accent', 'Verdigris', '--accent', '#5A9E8A', '90, 158, 138'),
                    ('border', 'Marble Border', '--border', '#E0DCD4', '224, 220, 212'),
                    ('success', 'Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Golden', '--warning', '#D4A85A', '212, 168, 90'),
                    ('error', 'Rust', '--error', '#B86A4A', '184, 106, 74'),
                ]
            },
            {
                'name': 'Regency',
                'category': 'elegant-luxury',
                'mood': 'regal',
                'colors': [
                    ('background', 'Regency Cream', '--background', '#FDF9F2', '253, 249, 242'),
                    ('text', 'Regency Blue', '--text', '#2A3A5A', '42, 58, 90'),
                    ('heading', 'Deep Regency', '--heading', '#1A2A4A', '26, 42, 74'),
                    ('primary', 'Royal Blue', '--primary', '#3A5A8A', '58, 90, 138'),
                    ('secondary', 'Warm Gold', '--secondary', '#C4A44A', '196, 164, 74'),
                    ('accent', 'Burgundy', '--accent', '#8A3A4A', '138, 58, 74'),
                    ('border', 'Regency Border', '--border', '#D8D8E0', '216, 216, 224'),
                    ('success', 'Forest', '--success', '#2E6B3A', '46, 107, 58'),
                    ('warning', 'Amber', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Crimson', '--error', '#A83A3A', '168, 58, 58'),
                ]
            },

            # ============================================
            # CATEGORY: earthy-organic (8 palettes)
            # Natural greens, browns, botanical
            # ============================================
            {
                'name': 'Forest Bath',
                'category': 'earthy-organic',
                'mood': 'natural',
                'colors': [
                    ('background', 'Forest Mist', '--background', '#F2F5F0', '242, 245, 240'),
                    ('text', 'Deep Forest', '--text', '#2A3A2A', '42, 58, 42'),
                    ('heading', 'Ancient Pine', '--heading', '#1A2A1A', '26, 42, 26'),
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
                    ('heading', 'Deep Roots', '--heading', '#2A2A1A', '42, 42, 26'),
                    ('primary', 'Herb Green', '--primary', '#5A8A4A', '90, 138, 74'),
                    ('secondary', 'Sage', '--secondary', '#8AAA7A', '138, 170, 122'),
                    ('accent', 'Lavender', '--accent', '#9E7AB8', '158, 122, 184'),
                    ('border', 'Garden Border', '--border', '#D8E2CC', '216, 226, 204'),
                    ('success', 'Fresh Leaf', '--success', '#4AA86B', '74, 168, 107'),
                    ('warning', 'Honey', '--warning', '#D4B04A', '212, 176, 74'),
                    ('error', 'Rose Hip', '--error', '#C45A5A', '196, 90, 90'),
                ]
            },
            {
                'name': 'Olive Grove',
                'category': 'earthy-organic',
                'mood': 'mediterranean',
                'colors': [
                    ('background', 'Olive White', '--background', '#F8F5EE', '248, 245, 238'),
                    ('text', 'Olive Brown', '--text', '#4A4235', '74, 66, 53'),
                    ('heading', 'Deep Olive', '--heading', '#3A3225', '58, 50, 37'),
                    ('primary', 'Olive Green', '--primary', '#6B8A4E', '107, 138, 78'),
                    ('secondary', 'Warm Stone', '--secondary', '#9E9684', '158, 150, 132'),
                    ('accent', 'Terracotta', '--accent', '#B86E4E', '184, 110, 78'),
                    ('border', 'Olive Border', '--border', '#E0D8C8', '224, 216, 200'),
                    ('success', 'Herb', '--success', '#5A9E5A', '90, 158, 90'),
                    ('warning', 'Citrus', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Tomato', '--error', '#B85A4A', '184, 90, 74'),
                ]
            },
            {
                'name': 'Wild Meadow',
                'category': 'earthy-organic',
                'mood': 'natural',
                'colors': [
                    ('background', 'Meadow White', '--background', '#F7F8F0', '247, 248, 240'),
                    ('text', 'Earth Brown', '--text', '#4A4030', '74, 64, 48'),
                    ('heading', 'Deep Earth', '--heading', '#3A3020', '58, 48, 32'),
                    ('primary', 'Wild Green', '--primary', '#6B9E5A', '107, 158, 90'),
                    ('secondary', 'Dried Grass', '--secondary', '#9EA86B', '158, 168, 107'),
                    ('accent', 'Wildflower', '--accent', '#B87A9E', '184, 122, 158'),
                    ('border', 'Meadow Border', '--border', '#D8E0C8', '216, 224, 200'),
                    ('success', 'Fresh Grass', '--success', '#4AA84A', '74, 168, 74'),
                    ('warning', 'Goldenrod', '--warning', '#D4B44A', '212, 180, 74'),
                    ('error', 'Poppy', '--error', '#C45A3A', '196, 90, 58'),
                ]
            },
            {
                'name': 'Cedar & Sage',
                'category': 'earthy-organic',
                'mood': 'woody',
                'colors': [
                    ('background', 'Cedar White', '--background', '#F5F2EE', '245, 242, 238'),
                    ('text', 'Cedar Brown', '--text', '#4A3A2A', '74, 58, 42'),
                    ('heading', 'Deep Cedar', '--heading', '#3A2A1A', '58, 42, 26'),
                    ('primary', 'Cedar', '--primary', '#8A6B4E', '138, 107, 78'),
                    ('secondary', 'Sage', '--secondary', '#8AAA7A', '138, 170, 122'),
                    ('accent', 'Juniper', '--accent', '#4A7A8A', '74, 122, 138'),
                    ('border', 'Cedar Border', '--border', '#E0D8CC', '224, 216, 204'),
                    ('success', 'Pine', '--success', '#4A8A5A', '74, 138, 90'),
                    ('warning', 'Amber', '--warning', '#C49A4A', '196, 154, 74'),
                    ('error', 'Brick', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },
            {
                'name': 'Eucalyptus',
                'category': 'earthy-organic',
                'mood': 'calm',
                'colors': [
                    ('background', 'Eucalyptus White', '--background', '#F0F5F0', '240, 245, 240'),
                    ('text', 'Eucalyptus Gray', '--text', '#3A4A3A', '58, 74, 58'),
                    ('heading', 'Deep Eucalyptus', '--heading', '#2A3A2A', '42, 58, 42'),
                    ('primary', 'Eucalyptus Green', '--primary', '#5A8A7A', '90, 138, 122'),
                    ('secondary', 'Silver Leaf', '--secondary', '#9EB8A8', '158, 184, 168'),
                    ('accent', 'Gum Blossom', '--accent', '#C47A9E', '196, 122, 158'),
                    ('border', 'Eucalyptus Border', '--border', '#D0E0D8', '208, 224, 216'),
                    ('success', 'New Leaf', '--success', '#5AAA7A', '90, 170, 122'),
                    ('warning', 'Wattle', '--warning', '#D4B84A', '212, 184, 74'),
                    ('error', 'Gum Nut', '--error', '#A86B4A', '168, 107, 74'),
                ]
            },
            {
                'name': 'Harvest Moon',
                'category': 'earthy-organic',
                'mood': 'autumnal',
                'colors': [
                    ('background', 'Harvest Cream', '--background', '#F8F2E8', '248, 242, 232'),
                    ('text', 'Harvest Brown', '--text', '#4A3A28', '74, 58, 40'),
                    ('heading', 'Deep Harvest', '--heading', '#3A2A18', '58, 42, 24'),
                    ('primary', 'Pumpkin', '--primary', '#D47A3A', '212, 122, 58'),
                    ('secondary', 'Wheat', '--secondary', '#C4A86B', '196, 168, 107'),
                    ('accent', 'Cranberry', '--accent', '#A84A6B', '168, 74, 107'),
                    ('border', 'Harvest Border', '--border', '#E8DCC0', '232, 220, 192'),
                    ('success', 'Kale', '--success', '#5A8A4A', '90, 138, 74'),
                    ('warning', 'Maize', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Apple Red', '--error', '#B84A3A', '184, 74, 58'),
                ]
            },
            {
                'name': 'Stone & Moss',
                'category': 'earthy-organic',
                'mood': 'zen',
                'colors': [
                    ('background', 'Zen White', '--background', '#F2F2EE', '242, 242, 238'),
                    ('text', 'Stone Gray', '--text', '#4A4A42', '74, 74, 66'),
                    ('heading', 'Deep Stone', '--heading', '#3A3A32', '58, 58, 50'),
                    ('primary', 'River Stone', '--primary', '#7A8A7A', '122, 138, 122'),
                    ('secondary', 'Moss', '--secondary', '#6B9E6B', '107, 158, 107'),
                    ('accent', 'Lichen', '--accent', '#9E9E5A', '158, 158, 90'),
                    ('border', 'Stone Border', '--border', '#D8D8D0', '216, 216, 208'),
                    ('success', 'Bamboo', '--success', '#5AAA5A', '90, 170, 90'),
                    ('warning', 'Golden Moss', '--warning', '#C4B44A', '196, 180, 74'),
                    ('error', 'Rust', '--error', '#B86A4A', '184, 106, 74'),
                ]
            },

            # ============================================
            # CATEGORY: urban-modern (8 palettes)
            # Concrete, steel, city-inspired
            # ============================================
            {
                'name': 'Urban Concrete',
                'category': 'urban-modern',
                'mood': 'urban',
                'colors': [
                    ('background', 'Concrete White', '--background', '#F2F0EE', '242, 240, 238'),
                    ('text', 'Urban Charcoal', '--text', '#3A3A38', '58, 58, 56'),
                    ('heading', 'Deep Urban', '--heading', '#2A2A28', '42, 42, 40'),
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
                    ('heading', 'Cast Iron', '--heading', '#2A2A2A', '42, 42, 42'),
                    ('primary', 'Rust', '--primary', '#B86A4A', '184, 106, 74'),
                    ('secondary', 'Steel', '--secondary', '#7A8A9E', '122, 138, 158'),
                    ('accent', 'Copper Pipe', '--accent', '#C48A5A', '196, 138, 90'),
                    ('border', 'Industrial Border', '--border', '#D0CEC8', '208, 206, 200'),
                    ('success', 'Safety Green', '--success', '#5AAA5A', '90, 170, 90'),
                    ('warning', 'Caution Yellow', '--warning', '#D4C04A', '212, 192, 74'),
                    ('error', 'Warning Red', '--error', '#C44A4A', '196, 74, 74'),
                ]
            },
            {
                'name': 'City Lights',
                'category': 'urban-modern',
                'mood': 'nocturnal',
                'colors': [
                    ('background', 'Night White', '--background', '#F0F2F5', '240, 242, 245'),
                    ('text', 'City Black', '--text', '#1E2024', '30, 32, 36'),
                    ('heading', 'Deep Night', '--heading', '#14161A', '20, 22, 26'),
                    ('primary', 'Neon Blue', '--primary', '#2A6B9E', '42, 107, 158'),
                    ('secondary', 'Sidewalk Gray', '--secondary', '#6B7A8A', '107, 122, 138'),
                    ('accent', 'Neon Pink', '--accent', '#D44A8A', '212, 74, 138'),
                    ('border', 'City Border', '--border', '#D0D4D8', '208, 212, 216'),
                    ('success', 'Neon Green', '--success', '#2AAA6B', '42, 170, 107'),
                    ('warning', 'Neon Yellow', '--warning', '#E5D04A', '229, 208, 74'),
                    ('error', 'Neon Red', '--error', '#E54A4A', '229, 74, 74'),
                ]
            },
            {
                'name': 'Metro Station',
                'category': 'urban-modern',
                'mood': 'transit',
                'colors': [
                    ('background', 'Station White', '--background', '#F5F2F0', '245, 242, 240'),
                    ('text', 'Metro Gray', '--text', '#3A3A3A', '58, 58, 58'),
                    ('heading', 'Deep Metro', '--heading', '#2A2A2A', '42, 42, 42'),
                    ('primary', 'Metro Blue', '--primary', '#2A5A8A', '42, 90, 138'),
                    ('secondary', 'Platform Gray', '--secondary', '#8A8A8A', '138, 138, 138'),
                    ('accent', 'Metro Orange', '--accent', '#D47A3A', '212, 122, 58'),
                    ('border', 'Metro Border', '--border', '#D0CEC8', '208, 206, 200'),
                    ('success', 'Go Green', '--success', '#4A9E5A', '74, 158, 90'),
                    ('warning', 'Delay Yellow', '--warning', '#D4B44A', '212, 180, 74'),
                    ('error', 'Stop Red', '--error', '#C44A4A', '196, 74, 74'),
                ]
            },
            {
                'name': 'Warehouse',
                'category': 'urban-modern',
                'mood': 'raw',
                'colors': [
                    ('background', 'Warehouse White', '--background', '#F0EEEA', '240, 238, 234'),
                    ('text', 'Raw Steel', '--text', '#4A4A4A', '74, 74, 74'),
                    ('heading', 'Dark Steel', '--heading', '#3A3A3A', '58, 58, 58'),
                    ('primary', 'Exposed Brick', '--primary', '#A85A4A', '168, 90, 74'),
                    ('secondary', 'Galvanized', '--secondary', '#8A929A', '138, 146, 154'),
                    ('accent', 'Safety Orange', '--accent', '#D46B3A', '212, 107, 58'),
                    ('border', 'Warehouse Border', '--border', '#D0CCC4', '208, 204, 196'),
                    ('success', 'OSHA Green', '--success', '#4A9E4A', '74, 158, 74'),
                    ('warning', 'Caution', '--warning', '#D4B44A', '212, 180, 74'),
                    ('error', 'Fire Red', '--error', '#C44A3A', '196, 74, 58'),
                ]
            },
            {
                'name': 'Startup Garage',
                'category': 'urban-modern',
                'mood': 'innovative',
                'colors': [
                    ('background', 'Garage White', '--background', '#F8F8F8', '248, 248, 248'),
                    ('text', 'Startup Black', '--text', '#1E1E1E', '30, 30, 30'),
                    ('heading', 'Founder Black', '--heading', '#141414', '20, 20, 20'),
                    ('primary', 'Innovation Blue', '--primary', '#2A6B9E', '42, 107, 158'),
                    ('secondary', 'Aluminum', '--secondary', '#8A929A', '138, 146, 154'),
                    ('accent', 'Disrupt Orange', '--accent', '#E56B3A', '229, 107, 58'),
                    ('border', 'Garage Border', '--border', '#D0D0D0', '208, 208, 208'),
                    ('success', 'Growth Green', '--success', '#2A9E5A', '42, 158, 90'),
                    ('warning', 'Pivot Yellow', '--warning', '#E5C04A', '229, 192, 74'),
                    ('error', 'Burnout Red', '--error', '#E54A4A', '229, 74, 74'),
                ]
            },
            {
                'name': 'Rooftop',
                'category': 'urban-modern',
                'mood': 'elevated',
                'colors': [
                    ('background', 'Skyline White', '--background', '#F5F7F8', '245, 247, 248'),
                    ('text', 'Skyline Gray', '--text', '#3A424A', '58, 66, 74'),
                    ('heading', 'Deep Skyline', '--heading', '#2A323A', '42, 50, 58'),
                    ('primary', 'Horizon Blue', '--primary', '#4A7A9E', '74, 122, 158'),
                    ('secondary', 'Cloud', '--secondary', '#9EAAB8', '158, 170, 184'),
                    ('accent', 'Sunset', '--accent', '#D47A6B', '212, 122, 107'),
                    ('border', 'Rooftop Border', '--border', '#D0D8E0', '208, 216, 224'),
                    ('success', 'Rooftop Garden', '--success', '#5A9E6B', '90, 158, 107'),
                    ('warning', 'Golden Hour', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Siren', '--error', '#CE5A5A', '206, 90, 90'),
                ]
            },
            {
                'name': 'Brutalist',
                'category': 'urban-modern',
                'mood': 'architectural',
                'colors': [
                    ('background', 'Brutalist White', '--background', '#EEECEA', '238, 236, 234'),
                    ('text', 'Raw Concrete', '--text', '#4A4844', '74, 72, 68'),
                    ('heading', 'Deep Concrete', '--heading', '#3A3834', '58, 56, 52'),
                    ('primary', 'Exposed Aggregate', '--primary', '#7A7670', '122, 118, 112'),
                    ('secondary', 'Formwork', '--secondary', '#A09C96', '160, 156, 150'),
                    ('accent', 'Corten Steel', '--accent', '#B86A4A', '184, 106, 74'),
                    ('border', 'Brutalist Border', '--border', '#D0CCC6', '208, 204, 198'),
                    ('success', 'Planted Terrace', '--success', '#5A8A5A', '90, 138, 90'),
                    ('warning', 'Rust', '--warning', '#C49A4A', '196, 154, 74'),
                    ('error', 'Structural Red', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },

            # ============================================
            # CATEGORY: soft-romantic (8 palettes)
            # Blush, rose, lavender, gentle
            # ============================================
            {
                'name': 'Blush & Cream',
                'category': 'soft-romantic',
                'mood': 'gentle',
                'colors': [
                    ('background', 'Blush White', '--background', '#FDF8F5', '253, 248, 245'),
                    ('text', 'Rose Brown', '--text', '#4A3A3A', '74, 58, 58'),
                    ('heading', 'Deep Rose', '--heading', '#3A2A2A', '58, 42, 42'),
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
                    ('heading', 'Deep Lavender', '--heading', '#3A3440', '58, 52, 64'),
                    ('primary', 'Lavender', '--primary', '#9E8AB8', '158, 138, 184'),
                    ('secondary', 'Wispy Purple', '--secondary', '#C4B8D4', '196, 184, 212'),
                    ('accent', 'Wild Lilac', '--accent', '#B87AA8', '184, 122, 168'),
                    ('border', 'Lavender Border', '--border', '#E0D8E8', '224, 216, 232'),
                    ('success', 'Mint', '--success', '#6BBA8A', '107, 186, 138'),
                    ('warning', 'Honey', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Berry', '--error', '#B86B8A', '184, 107, 138'),
                ]
            },
            {
                'name': 'Rose Quartz',
                'category': 'soft-romantic',
                'mood': 'serene',
                'colors': [
                    ('background', 'Quartz White', '--background', '#FDF8F8', '253, 248, 248'),
                    ('text', 'Quartz Gray', '--text', '#4A4040', '74, 64, 64'),
                    ('heading', 'Deep Quartz', '--heading', '#3A3030', '58, 48, 48'),
                    ('primary', 'Rose Quartz', '--primary', '#C49E9E', '196, 158, 158'),
                    ('secondary', 'Pale Rose', '--secondary', '#E0C8C8', '224, 200, 200'),
                    ('accent', 'Serenity Blue', '--accent', '#8AA8C4', '138, 168, 196'),
                    ('border', 'Quartz Border', '--border', '#E0D4D4', '224, 212, 212'),
                    ('success', 'Seafoam', '--success', '#6BA89E', '107, 168, 158'),
                    ('warning', 'Peach', '--warning', '#D4A88A', '212, 168, 138'),
                    ('error', 'Muted Rose', '--error', '#C47A7A', '196, 122, 122'),
                ]
            },
            {
                'name': 'Peach Sorbet',
                'category': 'soft-romantic',
                'mood': 'sweet',
                'colors': [
                    ('background', 'Sorbet White', '--background', '#FDF6F2', '253, 246, 242'),
                    ('text', 'Peach Brown', '--text', '#4A3A30', '74, 58, 48'),
                    ('heading', 'Deep Peach', '--heading', '#3A2A20', '58, 42, 32'),
                    ('primary', 'Peach', '--primary', '#D4A080', '212, 160, 128'),
                    ('secondary', 'Cream', '--secondary', '#E8D0B8', '232, 208, 184'),
                    ('accent', 'Apricot', '--accent', '#D48A5A', '212, 138, 90'),
                    ('border', 'Sorbet Border', '--border', '#E8D8C8', '232, 216, 200'),
                    ('success', 'Pistachio', '--success', '#7AAE7A', '122, 174, 122'),
                    ('warning', 'Mango', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Guava', '--error', '#C46B5A', '196, 107, 90'),
                ]
            },
            {
                'name': 'Cherry Blossom',
                'category': 'soft-romantic',
                'mood': 'delicate',
                'colors': [
                    ('background', 'Blossom White', '--background', '#FDF5F5', '253, 245, 245'),
                    ('text', 'Blossom Brown', '--text', '#4A3535', '74, 53, 53'),
                    ('heading', 'Deep Blossom', '--heading', '#3A2525', '58, 37, 37'),
                    ('primary', 'Cherry Blossom', '--primary', '#E0A0A0', '224, 160, 160'),
                    ('secondary', 'Pale Pink', '--secondary', '#F0C8C8', '240, 200, 200'),
                    ('accent', 'Sakura', '--accent', '#D46B8A', '212, 107, 138'),
                    ('border', 'Blossom Border', '--border', '#E8D0D0', '232, 208, 208'),
                    ('success', 'Young Leaf', '--success', '#7AB87A', '122, 184, 122'),
                    ('warning', 'Pollen', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Wilted Petal', '--error', '#C46B6B', '196, 107, 107'),
                ]
            },
            {
                'name': 'Dusty Rose',
                'category': 'soft-romantic',
                'mood': 'vintage',
                'colors': [
                    ('background', 'Dusty White', '--background', '#F5F0EE', '245, 240, 238'),
                    ('text', 'Dusty Brown', '--text', '#4A3A38', '74, 58, 56'),
                    ('heading', 'Deep Dusty', '--heading', '#3A2A28', '58, 42, 40'),
                    ('primary', 'Dusty Rose', '--primary', '#B88A8A', '184, 138, 138'),
                    ('secondary', 'Warm Taupe', '--secondary', '#A8948A', '168, 148, 138'),
                    ('accent', 'Mauve', '--accent', '#9E6B8A', '158, 107, 138'),
                    ('border', 'Dusty Border', '--border', '#D8CCC8', '216, 204, 200'),
                    ('success', 'Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Antique Gold', '--warning', '#C49A5A', '196, 154, 90'),
                    ('error', 'Burgundy', '--error', '#A85A5A', '168, 90, 90'),
                ]
            },
            {
                'name': 'Powder Blue',
                'category': 'soft-romantic',
                'mood': 'airy',
                'colors': [
                    ('background', 'Powder White', '--background', '#F2F5F8', '242, 245, 248'),
                    ('text', 'Powder Gray', '--text', '#4A5058', '74, 80, 88'),
                    ('heading', 'Deep Powder', '--heading', '#3A4048', '58, 64, 72'),
                    ('primary', 'Powder Blue', '--primary', '#9EB8D4', '158, 184, 212'),
                    ('secondary', 'Cloud', '--secondary', '#C8D8E8', '200, 216, 232'),
                    ('accent', 'Periwinkle', '--accent', '#8A9ECE', '138, 158, 206'),
                    ('border', 'Powder Border', '--border', '#D0DCE8', '208, 220, 232'),
                    ('success', 'Seafoam', '--success', '#6BA89E', '107, 168, 158'),
                    ('warning', 'Butter', '--warning', '#D4C06B', '212, 192, 107'),
                    ('error', 'Soft Coral', '--error', '#CE8A8A', '206, 138, 138'),
                ]
            },
            {
                'name': 'Wisteria',
                'category': 'soft-romantic',
                'mood': 'enchanting',
                'colors': [
                    ('background', 'Wisteria White', '--background', '#F8F5FA', '248, 245, 250'),
                    ('text', 'Wisteria Gray', '--text', '#4A4050', '74, 64, 80'),
                    ('heading', 'Deep Wisteria', '--heading', '#3A3040', '58, 48, 64'),
                    ('primary', 'Wisteria', '--primary', '#A88AB8', '168, 138, 184'),
                    ('secondary', 'Lilac', '--secondary', '#C8B0D4', '200, 176, 212'),
                    ('accent', 'Orchid', '--accent', '#B86BA8', '184, 107, 168'),
                    ('border', 'Wisteria Border', '--border', '#D8CCE0', '216, 204, 224'),
                    ('success', 'Jade', '--success', '#5A9E7A', '90, 158, 122'),
                    ('warning', 'Honey', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Magenta', '--error', '#B86B8A', '184, 107, 138'),
                ]
            },

            # ============================================
            # CATEGORY: dark-moody (7 palettes)
            # Deep backgrounds, rich accents
            # ============================================
            {
                'name': 'Midnight Study',
                'category': 'dark-moody',
                'mood': 'dark',
                'colors': [
                    ('background', 'Deep Navy', '--background', '#1A2430', '26, 36, 48'),
                    ('text', 'Pale Gray', '--text', '#C8D0D8', '200, 208, 216'),
                    ('heading', 'Off White', '--heading', '#E8ECF0', '232, 236, 240'),
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
                    ('heading', 'White', '--heading', '#E8E8EA', '232, 232, 234'),
                    ('primary', 'Gold', '--primary', '#C4A44A', '196, 164, 74'),
                    ('secondary', 'Dark Gray', '--secondary', '#4A4A50', '74, 74, 80'),
                    ('accent', 'Ruby', '--accent', '#C44A5A', '196, 74, 90'),
                    ('border', 'Obsidian Border', '--border', '#2A2A2E', '42, 42, 46'),
                    ('success', 'Emerald', '--success', '#2A8A4A', '42, 138, 74'),
                    ('warning', 'Topaz', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Garnet', '--error', '#B84A4A', '184, 74, 74'),
                ]
            },
            {
                'name': 'Noir Cinema',
                'category': 'dark-moody',
                'mood': 'cinematic',
                'colors': [
                    ('background', 'Cinema Black', '--background', '#141416', '20, 20, 22'),
                    ('text', 'Silver Screen', '--text', '#D0D0D4', '208, 208, 212'),
                    ('heading', 'Pure White', '--heading', '#F0F0F2', '240, 240, 242'),
                    ('primary', 'Crimson', '--primary', '#B82A3A', '184, 42, 58'),
                    ('secondary', 'Charcoal', '--secondary', '#3A3A40', '58, 58, 64'),
                    ('accent', 'Gold Spotlight', '--accent', '#D4B44A', '212, 180, 74'),
                    ('border', 'Cinema Border', '--border', '#242428', '36, 36, 40'),
                    ('success', 'Theater Green', '--success', '#2A7A3A', '42, 122, 58'),
                    ('warning', 'Marquee Yellow', '--warning', '#E5C44A', '229, 196, 74'),
                    ('error', 'Exit Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },
            {
                'name': 'Espresso Bar',
                'category': 'dark-moody',
                'mood': 'rich',
                'colors': [
                    ('background', 'Espresso', '--background', '#2A1E1A', '42, 30, 26'),
                    ('text', 'Crema', '--text', '#D4C8C0', '212, 200, 192'),
                    ('heading', 'White Foam', '--heading', '#E8E0D8', '232, 224, 216'),
                    ('primary', 'Caramel', '--primary', '#C48A4A', '196, 138, 74'),
                    ('secondary', 'Mocha', '--secondary', '#6B4A3A', '107, 74, 58'),
                    ('accent', 'Cherry', '--accent', '#A83A4A', '168, 58, 74'),
                    ('border', 'Espresso Border', '--border', '#3A2A24', '58, 42, 36'),
                    ('success', 'Matcha', '--success', '#4A8A5A', '74, 138, 90'),
                    ('warning', 'Honey', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Cinnamon', '--error', '#B85A3A', '184, 90, 58'),
                ]
            },
            {
                'name': 'Deep Forest',
                'category': 'dark-moody',
                'mood': 'mysterious',
                'colors': [
                    ('background', 'Deep Forest', '--background', '#1A2A1A', '26, 42, 26'),
                    ('text', 'Pale Moss', '--text', '#C8D8C0', '200, 216, 192'),
                    ('heading', 'Mist', '--heading', '#E0E8D8', '224, 232, 216'),
                    ('primary', 'Amber', '--primary', '#D4A44A', '212, 164, 74'),
                    ('secondary', 'Bark', '--secondary', '#5A4A3A', '90, 74, 58'),
                    ('accent', 'Wild Berry', '--accent', '#9E4A6B', '158, 74, 107'),
                    ('border', 'Forest Border', '--border', '#2A3A2A', '42, 58, 42'),
                    ('success', 'New Growth', '--success', '#4A9E5A', '74, 158, 90'),
                    ('warning', 'Firefly', '--warning', '#D4C04A', '212, 192, 74'),
                    ('error', 'Poison Berry', '--error', '#A84A5A', '168, 74, 90'),
                ]
            },
            {
                'name': 'Speakeasy',
                'category': 'dark-moody',
                'mood': 'intimate',
                'colors': [
                    ('background', 'Speakeasy Brown', '--background', '#2A221E', '42, 34, 30'),
                    ('text', 'Parchment', '--text', '#D0C4B8', '208, 196, 184'),
                    ('heading', 'Cream', '--heading', '#E8DCD0', '232, 220, 208'),
                    ('primary', 'Whiskey', '--primary', '#B87A3A', '184, 122, 58'),
                    ('secondary', 'Leather', '--secondary', '#6B4A3A', '107, 74, 58'),
                    ('accent', 'Vermouth', '--accent', '#8A3A4A', '138, 58, 74'),
                    ('border', 'Speakeasy Border', '--border', '#3A2E28', '58, 46, 40'),
                    ('success', 'Olive', '--success', '#5A8A4A', '90, 138, 74'),
                    ('warning', 'Bitters', '--warning', '#C49A4A', '196, 154, 74'),
                    ('error', 'Angostura', '--error', '#A84A3A', '168, 74, 58'),
                ]
            },
            {
                'name': 'Velvet Lounge',
                'category': 'dark-moody',
                'mood': 'luxurious',
                'colors': [
                    ('background', 'Velvet Purple', '--background', '#2A1A2A', '42, 26, 42'),
                    ('text', 'Silver', '--text', '#C8C0D0', '200, 192, 208'),
                    ('heading', 'Pearl', '--heading', '#E0D8E8', '224, 216, 232'),
                    ('primary', 'Gold', '--primary', '#C4A44A', '196, 164, 74'),
                    ('secondary', 'Plum', '--secondary', '#6B3A5A', '107, 58, 90'),
                    ('accent', 'Fuchsia', '--accent', '#B84A8A', '184, 74, 138'),
                    ('border', 'Velvet Border', '--border', '#3A2A3A', '58, 42, 58'),
                    ('success', 'Jade', '--success', '#3A8A5A', '58, 138, 90'),
                    ('warning', 'Champagne', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Ruby', '--error', '#B83A4A', '184, 58, 74'),
                ]
            },

            # ============================================
            # CATEGORY: vibrant-pop (7 palettes)
            # Playful, colorful, energetic
            # ============================================
            {
                'name': 'Citrus Splash',
                'category': 'vibrant-pop',
                'mood': 'energetic',
                'colors': [
                    ('background', 'Citrus White', '--background', '#FDF8F0', '253, 248, 240'),
                    ('text', 'Citrus Black', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Deep Citrus', '--heading', '#1A1A1A', '26, 26, 26'),
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
                    ('heading', 'Dark Chocolate', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Bubblegum', '--primary', '#E56BA8', '229, 107, 168'),
                    ('secondary', 'Cotton Candy', '--secondary', '#8AC4E5', '138, 196, 229'),
                    ('accent', 'Lemon Drop', '--accent', '#E5D44A', '229, 212, 74'),
                    ('border', 'Candy Border', '--border', '#E8D0D8', '232, 208, 216'),
                    ('success', 'Sour Apple', '--success', '#6BE54A', '107, 229, 74'),
                    ('warning', 'Butterscotch', '--warning', '#E5B44A', '229, 180, 74'),
                    ('error', 'Cherry', '--error', '#E54A5A', '229, 74, 90'),
                ]
            },
            {
                'name': 'Neon Pop',
                'category': 'vibrant-pop',
                'mood': 'electric',
                'colors': [
                    ('background', 'Neon White', '--background', '#F8F8FC', '248, 248, 252'),
                    ('text', 'Neon Black', '--text', '#1E1E24', '30, 30, 36'),
                    ('heading', 'Deep Neon', '--heading', '#14141A', '20, 20, 26'),
                    ('primary', 'Neon Pink', '--primary', '#E52A8A', '229, 42, 138'),
                    ('secondary', 'Neon Cyan', '--secondary', '#2AC4E5', '42, 196, 229'),
                    ('accent', 'Neon Yellow', '--accent', '#E5E02A', '229, 224, 42'),
                    ('border', 'Neon Border', '--border', '#D0D0D8', '208, 208, 216'),
                    ('success', 'Neon Green', '--success', '#2AE54A', '42, 229, 74'),
                    ('warning', 'Neon Orange', '--warning', '#E58A2A', '229, 138, 42'),
                    ('error', 'Neon Red', '--error', '#E52A2A', '229, 42, 42'),
                ]
            },
            {
                'name': 'Summer Festival',
                'category': 'vibrant-pop',
                'mood': 'festive',
                'colors': [
                    ('background', 'Festival White', '--background', '#FDF8F0', '253, 248, 240'),
                    ('text', 'Festival Black', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Deep Festival', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Festival Pink', '--primary', '#D44A8A', '212, 74, 138'),
                    ('secondary', 'Turquoise', '--secondary', '#2A9E9E', '42, 158, 158'),
                    ('accent', 'Sunflower', '--accent', '#D4B42A', '212, 180, 42'),
                    ('border', 'Festival Border', '--border', '#E0D8C8', '224, 216, 200'),
                    ('success', 'Meadow', '--success', '#4AB84A', '74, 184, 74'),
                    ('warning', 'Marigold', '--warning', '#D48A2A', '212, 138, 42'),
                    ('error', 'Hibiscus', '--error', '#D42A5A', '212, 42, 90'),
                ]
            },
            {
                'name': 'Fruit Punch',
                'category': 'vibrant-pop',
                'mood': 'refreshing',
                'colors': [
                    ('background', 'Punch White', '--background', '#FDF5F2', '253, 245, 242'),
                    ('text', 'Punch Black', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Deep Punch', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Watermelon', '--primary', '#D43A5A', '212, 58, 90'),
                    ('secondary', 'Pineapple', '--secondary', '#D4B42A', '212, 180, 42'),
                    ('accent', 'Blueberry', '--accent', '#4A6BD4', '74, 107, 212'),
                    ('border', 'Punch Border', '--border', '#E0D0C8', '224, 208, 200'),
                    ('success', 'Kiwi', '--success', '#6BD44A', '107, 212, 74'),
                    ('warning', 'Mango', '--warning', '#D48A2A', '212, 138, 42'),
                    ('error', 'Raspberry', '--error', '#D42A6B', '212, 42, 107'),
                ]
            },
            {
                'name': 'Retro Arcade',
                'category': 'vibrant-pop',
                'mood': 'nostalgic',
                'colors': [
                    ('background', 'Arcade White', '--background', '#F0F0F5', '240, 240, 245'),
                    ('text', 'Arcade Black', '--text', '#1E1E24', '30, 30, 36'),
                    ('heading', 'Deep Arcade', '--heading', '#14141A', '20, 20, 26'),
                    ('primary', 'Retro Red', '--primary', '#D42A2A', '212, 42, 42'),
                    ('secondary', 'Retro Blue', '--secondary', '#2A5AD4', '42, 90, 212'),
                    ('accent', 'Retro Yellow', '--accent', '#D4C42A', '212, 196, 42'),
                    ('border', 'Arcade Border', '--border', '#C8C8D0', '200, 200, 208'),
                    ('success', '1UP Green', '--success', '#2AD44A', '42, 212, 74'),
                    ('warning', 'Power Pellet', '--warning', '#D48A2A', '212, 138, 42'),
                    ('error', 'Game Over', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },
            {
                'name': 'Tropical Paradise',
                'category': 'vibrant-pop',
                'mood': 'exotic',
                'colors': [
                    ('background', 'Paradise White', '--background', '#FDF8F2', '253, 248, 242'),
                    ('text', 'Paradise Black', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Deep Paradise', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Hibiscus', '--primary', '#D42A6B', '212, 42, 107'),
                    ('secondary', 'Ocean', '--secondary', '#2A9ED4', '42, 158, 212'),
                    ('accent', 'Bird of Paradise', '--accent', '#D48A2A', '212, 138, 42'),
                    ('border', 'Paradise Border', '--border', '#E0D4C8', '224, 212, 200'),
                    ('success', 'Palm', '--success', '#4AD46B', '74, 212, 107'),
                    ('warning', 'Papaya', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Dragon Fruit', '--error', '#D42A8A', '212, 42, 138'),
                ]
            },

            # CATEGORY: luxury (7 palettes)
            # High-end fashion, jewelry, premium goods
            # ============================================
            {
                'name': 'Midnight Sapphire',
                'category': 'luxury',
                'mood': 'elegant',
                'colors': [
                    ('background', 'Pearl White', '--background', '#FAFAF8', '250, 250, 248'),
                    ('text', 'Sapphire Ink', '--text', '#1A2436', '26, 36, 54'),
                    ('heading', 'Deep Sapphire', '--heading', '#0F1624', '15, 22, 36'),
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
                    ('heading', 'Deep Caviar', '--heading', '#14100E', '20, 16, 14'),
                    ('primary', 'Burnished Gold', '--primary', '#C49A4A', '196, 154, 74'),
                    ('secondary', 'Warm Taupe', '--secondary', '#A8907A', '168, 144, 122'),
                    ('accent', 'Pearl', '--accent', '#F0E8D8', '240, 232, 216'),
                    ('border', 'Champagne Border', '--border', '#E8DCC8', '232, 220, 200'),
                    ('success', 'Emerald', '--success', '#1A6B3A', '26, 107, 58'),
                    ('warning', 'Topaz', '--warning', '#D4B06B', '212, 176, 107'),
                    ('error', 'Garnet', '--error', '#9E2A3A', '158, 42, 58'),
                ]
            },
            {
                'name': 'Velvet Noir',
                'category': 'luxury',
                'mood': 'glamorous',
                'colors': [
                    ('background', 'Velvet Cream', '--background', '#FDF5F0', '253, 245, 240'),
                    ('text', 'Noir Black', '--text', '#1C1818', '28, 24, 24'),
                    ('heading', 'Deep Noir', '--heading', '#120E0E', '18, 14, 14'),
                    ('primary', 'Burgundy Velvet', '--primary', '#7A2A3A', '122, 42, 58'),
                    ('secondary', 'Mauve', '--secondary', '#9E7A8A', '158, 122, 138'),
                    ('accent', 'Gold Thread', '--accent', '#C4A44A', '196, 164, 74'),
                    ('border', 'Velvet Border', '--border', '#E0D0D0', '224, 208, 208'),
                    ('success', 'Forest', '--success', '#2A5A3A', '42, 90, 58'),
                    ('warning', 'Amber', '--warning', '#D4A04A', '212, 160, 74'),
                    ('error', 'Ruby', '--error', '#9B1D2D', '155, 29, 45'),
                ]
            },
            {
                'name': 'Platinum Reserve',
                'category': 'luxury',
                'mood': 'sleek',
                'colors': [
                    ('background', 'Platinum White', '--background', '#F5F5F2', '245, 245, 242'),
                    ('text', 'Gunmetal', '--text', '#2A2E35', '42, 46, 53'),
                    ('heading', 'Deep Gunmetal', '--heading', '#1A1E24', '26, 30, 36'),
                    ('primary', 'Platinum', '--primary', '#A0A8B4', '160, 168, 180'),
                    ('secondary', 'Silver', '--secondary', '#C8CED8', '200, 206, 216'),
                    ('accent', 'Electric Blue', '--accent', '#2A6B9E', '42, 107, 158'),
                    ('border', 'Platinum Border', '--border', '#D0D4DC', '208, 212, 220'),
                    ('success', 'Teal', '--success', '#1A7A6B', '26, 122, 107'),
                    ('warning', 'Amber', '--warning', '#D49E3A', '212, 158, 58'),
                    ('error', 'Crimson', '--error', '#C42A3A', '196, 42, 58'),
                ]
            },
            {
                'name': 'Regency Gold',
                'category': 'luxury',
                'mood': 'regal',
                'colors': [
                    ('background', 'Regency Cream', '--background', '#FDF9F0', '253, 249, 240'),
                    ('text', 'Regency Navy', '--text', '#1A2436', '26, 36, 54'),
                    ('heading', 'Deep Regency', '--heading', '#0F1624', '15, 22, 36'),
                    ('primary', 'Royal Blue', '--primary', '#2A4A7A', '42, 74, 122'),
                    ('secondary', 'Antique Gold', '--secondary', '#C4A44A', '196, 164, 74'),
                    ('accent', 'Burgundy', '--accent', '#7A2A3A', '122, 42, 58'),
                    ('border', 'Regency Border', '--border', '#D8D8E0', '216, 216, 224'),
                    ('success', 'Forest', '--success', '#2A5A3A', '42, 90, 58'),
                    ('warning', 'Amber', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Crimson', '--error', '#9E2A3A', '158, 42, 58'),
                ]
            },
            {
                'name': 'Bone & Bronze',
                'category': 'luxury',
                'mood': 'refined',
                'colors': [
                    ('background', 'Bone White', '--background', '#F8F4EE', '248, 244, 238'),
                    ('text', 'Bronze Brown', '--text', '#4A3E35', '74, 62, 53'),
                    ('heading', 'Aged Bronze', '--heading', '#352A22', '53, 42, 34'),
                    ('primary', 'Burnished Bronze', '--primary', '#A87A5E', '168, 122, 94'),
                    ('secondary', 'Warm Pewter', '--secondary', '#8B7D72', '139, 125, 114'),
                    ('accent', 'Patina', '--accent', '#5A8A7A', '90, 138, 122'),
                    ('border', 'Bone Border', '--border', '#E5DDD4', '229, 221, 212'),
                    ('success', 'Verdigris', '--success', '#4A8A6B', '74, 138, 107'),
                    ('warning', 'Ochre', '--warning', '#C49A4A', '196, 154, 74'),
                    ('error', 'Aged Red', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },
            {
                'name': 'Diamond District',
                'category': 'luxury',
                'mood': 'brilliant',
                'colors': [
                    ('background', 'Diamond White', '--background', '#FAFAFA', '250, 250, 250'),
                    ('text', 'Carbon Gray', '--text', '#2A2E35', '42, 46, 53'),
                    ('heading', 'Deep Carbon', '--heading', '#1A1E24', '26, 30, 36'),
                    ('primary', 'Ice Blue', '--primary', '#6BA5C4', '107, 165, 196'),
                    ('secondary', 'Silver', '--secondary', '#C0C8D4', '192, 200, 212'),
                    ('accent', 'Sapphire', '--accent', '#1A4A8A', '26, 74, 138'),
                    ('border', 'Diamond Border', '--border', '#D8DCE4', '216, 220, 228'),
                    ('success', 'Emerald', '--success', '#1A7A4A', '26, 122, 74'),
                    ('warning', 'Yellow Diamond', '--warning', '#D4B84A', '212, 184, 74'),
                    ('error', 'Ruby', '--error', '#C42A4A', '196, 42, 74'),
                ]
            },

            # ============================================
            # CATEGORY: fashion (7 palettes)
            # Apparel, accessories, style-forward
            # ============================================
            {
                'name': 'Runway Edit',
                'category': 'fashion',
                'mood': 'chic',
                'colors': [
                    ('background', 'Porcelain', '--background', '#F7F5F2', '247, 245, 242'),
                    ('text', 'Runway Black', '--text', '#222222', '34, 34, 34'),
                    ('heading', 'Editor Black', '--heading', '#161616', '22, 22, 22'),
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
                    ('heading', 'Deep Urban', '--heading', '#141414', '20, 20, 20'),
                    ('primary', 'Concrete', '--primary', '#7A7A7A', '122, 122, 122'),
                    ('secondary', 'Denim Blue', '--secondary', '#4A6B8A', '74, 107, 138'),
                    ('accent', 'Neon Orange', '--accent', '#E56B2A', '229, 107, 42'),
                    ('border', 'Street Border', '--border', '#D0CEC8', '208, 206, 200'),
                    ('success', 'Lime', '--success', '#5AC42A', '90, 196, 42'),
                    ('warning', 'Yellow', '--warning', '#D4C02A', '212, 192, 42'),
                    ('error', 'Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },
            {
                'name': 'Boho Luxe',
                'category': 'fashion',
                'mood': 'bohemian',
                'colors': [
                    ('background', 'Linen', '--background', '#F8F1E5', '248, 241, 229'),
                    ('text', 'Earth Brown', '--text', '#4A3A2A', '74, 58, 42'),
                    ('heading', 'Deep Earth', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Terracotta', '--primary', '#C46B4A', '196, 107, 74'),
                    ('secondary', 'Sage', '--secondary', '#8AAA7A', '138, 170, 122'),
                    ('accent', 'Mustard', '--accent', '#D4A42A', '212, 164, 42'),
                    ('border', 'Linen Border', '--border', '#E0D4C0', '224, 212, 192'),
                    ('success', 'Moss', '--success', '#5A9E5A', '90, 158, 90'),
                    ('warning', 'Ochre', '--warning', '#C49A4A', '196, 154, 74'),
                    ('error', 'Rust', '--error', '#B85A3A', '184, 90, 58'),
                ]
            },
            {
                'name': 'Minimalist Closet',
                'category': 'fashion',
                'mood': 'minimal',
                'colors': [
                    ('background', 'Pure White', '--background', '#FAFAFA', '250, 250, 250'),
                    ('text', 'Soft Black', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Deep Soft', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Camel', '--primary', '#C49A6B', '196, 154, 107'),
                    ('secondary', 'Warm Gray', '--secondary', '#9E9E9E', '158, 158, 158'),
                    ('accent', 'Blush', '--accent', '#D4A0A0', '212, 160, 160'),
                    ('border', 'Minimal Border', '--border', '#E0E0E0', '224, 224, 224'),
                    ('success', 'Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Sand', '--warning', '#D4B88A', '212, 184, 138'),
                    ('error', 'Coral', '--error', '#C46B6B', '196, 107, 107'),
                ]
            },
            {
                'name': 'Denim & Leather',
                'category': 'fashion',
                'mood': 'classic',
                'colors': [
                    ('background', 'Vintage White', '--background', '#F5F0EA', '245, 240, 234'),
                    ('text', 'Indigo', '--text', '#2A3A5A', '42, 58, 90'),
                    ('heading', 'Deep Indigo', '--heading', '#1A2A4A', '26, 42, 74'),
                    ('primary', 'Denim Blue', '--primary', '#4A6B9E', '74, 107, 158'),
                    ('secondary', 'Leather Brown', '--secondary', '#7A5A3A', '122, 90, 58'),
                    ('accent', 'Copper Rivet', '--accent', '#C47A4A', '196, 122, 74'),
                    ('border', 'Denim Border', '--border', '#D8D8E0', '216, 216, 224'),
                    ('success', 'Olive', '--success', '#5A8A4A', '90, 138, 74'),
                    ('warning', 'Brass', '--warning', '#C4A44A', '196, 164, 74'),
                    ('error', 'Brick', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },
            {
                'name': 'Athleisure',
                'category': 'fashion',
                'mood': 'energetic',
                'colors': [
                    ('background', 'Active White', '--background', '#F5F7F8', '245, 247, 248'),
                    ('text', 'Active Black', '--text', '#1E242A', '30, 36, 42'),
                    ('heading', 'Deep Active', '--heading', '#141A20', '20, 26, 32'),
                    ('primary', 'Performance Navy', '--primary', '#1A3A5A', '26, 58, 90'),
                    ('secondary', 'Heather Gray', '--secondary', '#8A969E', '138, 150, 158'),
                    ('accent', 'Neon Lime', '--accent', '#6BC42A', '107, 196, 42'),
                    ('border', 'Active Border', '--border', '#D0D8E0', '208, 216, 224'),
                    ('success', 'Fresh Green', '--success', '#2AC45A', '42, 196, 90'),
                    ('warning', 'Energy Orange', '--warning', '#E58A2A', '229, 138, 42'),
                    ('error', 'Stop Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },
            {
                'name': 'Vintage Revival',
                'category': 'fashion',
                'mood': 'nostalgic',
                'colors': [
                    ('background', 'Cream', '--background', '#FDF8F0', '253, 248, 240'),
                    ('text', 'Sepia', '--text', '#4A3A2A', '74, 58, 42'),
                    ('heading', 'Deep Sepia', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Retro Orange', '--primary', '#D47A3A', '212, 122, 58'),
                    ('secondary', 'Avocado', '--secondary', '#6B8A4A', '107, 138, 74'),
                    ('accent', 'Mustard', '--accent', '#D4B42A', '212, 180, 42'),
                    ('border', 'Vintage Border', '--border', '#E0D4C0', '224, 212, 192'),
                    ('success', 'Harvest Gold', '--success', '#9E8A4A', '158, 138, 74'),
                    ('warning', 'Burnt Orange', '--warning', '#C46B2A', '196, 107, 42'),
                    ('error', 'Brick Red', '--error', '#A84A3A', '168, 74, 58'),
                ]
            },

            # ============================================
            # CATEGORY: beauty (7 palettes)
            # Cosmetics, skincare, wellness
            # ============================================
            {
                'name': 'Rose Gold Glow',
                'category': 'beauty',
                'mood': 'glamorous',
                'colors': [
                    ('background', 'Blush Cream', '--background', '#FDF5F2', '253, 245, 242'),
                    ('text', 'Rose Brown', '--text', '#4A3535', '74, 53, 53'),
                    ('heading', 'Deep Rose', '--heading', '#352525', '53, 37, 37'),
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
                    ('heading', 'Deep Botanical', '--heading', '#2A3A2A', '42, 58, 42'),
                    ('primary', 'Sage', '--primary', '#7A9E7A', '122, 158, 122'),
                    ('secondary', 'Aloe', '--secondary', '#9EC4A0', '158, 196, 160'),
                    ('accent', 'Lavender', '--accent', '#B89EC4', '184, 158, 196'),
                    ('border', 'Clean Border', '--border', '#D8E0D4', '216, 224, 212'),
                    ('success', 'Fresh Mint', '--success', '#5ABA7A', '90, 186, 122'),
                    ('warning', 'Honey', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Rose', '--error', '#C46B7A', '196, 107, 122'),
                ]
            },
            {
                'name': 'Luxury Skincare',
                'category': 'beauty',
                'mood': 'elegant',
                'colors': [
                    ('background', 'Cream', '--background', '#FDF9F2', '253, 249, 242'),
                    ('text', 'Rich Brown', '--text', '#3A2E28', '58, 46, 40'),
                    ('heading', 'Deep Rich', '--heading', '#2A1E18', '42, 30, 24'),
                    ('primary', 'Gold', '--primary', '#C4A44A', '196, 164, 74'),
                    ('secondary', 'Warm Taupe', '--secondary', '#A8907A', '168, 144, 122'),
                    ('accent', 'Teal', '--accent', '#2A8A7A', '42, 138, 122'),
                    ('border', 'Luxury Border', '--border', '#E0D8CC', '224, 216, 204'),
                    ('success', 'Emerald', '--success', '#2A7A4A', '42, 122, 74'),
                    ('warning', 'Amber', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Coral', '--error', '#C46B5A', '196, 107, 90'),
                ]
            },
            {
                'name': 'Spa Retreat',
                'category': 'beauty',
                'mood': 'calm',
                'colors': [
                    ('background', 'Spa White', '--background', '#F2F5F0', '242, 245, 240'),
                    ('text', 'Stone Gray', '--text', '#4A5544', '74, 85, 68'),
                    ('heading', 'Deep Stone', '--heading', '#3A4534', '58, 69, 52'),
                    ('primary', 'Sea Glass', '--primary', '#7AB8A8', '122, 184, 168'),
                    ('secondary', 'Bamboo', '--secondary', '#9EC47A', '158, 196, 122'),
                    ('accent', 'Lotus', '--accent', '#D4A0B8', '212, 160, 184'),
                    ('border', 'Spa Border', '--border', '#D0DCC8', '208, 220, 200'),
                    ('success', 'Eucalyptus', '--success', '#5A9E7A', '90, 158, 122'),
                    ('warning', 'Ginger', '--warning', '#D4A85A', '212, 168, 90'),
                    ('error', 'Coral', '--error', '#C47A6B', '196, 122, 107'),
                ]
            },
            {
                'name': 'Modern Makeup',
                'category': 'beauty',
                'mood': 'trendy',
                'colors': [
                    ('background', 'Studio White', '--background', '#F8F8FA', '248, 248, 250'),
                    ('text', 'Charcoal', '--text', '#2A2A30', '42, 42, 48'),
                    ('heading', 'Deep Charcoal', '--heading', '#1A1A20', '26, 26, 32'),
                    ('primary', 'Fuchsia', '--primary', '#D42A8A', '212, 42, 138'),
                    ('secondary', 'Plum', '--secondary', '#6B3A6B', '107, 58, 107'),
                    ('accent', 'Gold Shimmer', '--accent', '#D4B44A', '212, 180, 74'),
                    ('border', 'Makeup Border', '--border', '#D8D8E0', '216, 216, 224'),
                    ('success', 'Mint', '--success', '#4AC49E', '74, 196, 158'),
                    ('warning', 'Peach', '--warning', '#D48A6B', '212, 138, 107'),
                    ('error', 'Ruby', '--error', '#D42A4A', '212, 42, 74'),
                ]
            },
            {
                'name': 'Organic Apothecary',
                'category': 'beauty',
                'mood': 'earthy',
                'colors': [
                    ('background', 'Hemp White', '--background', '#F5F2EA', '245, 242, 234'),
                    ('text', 'Root Brown', '--text', '#4A3A28', '74, 58, 40'),
                    ('heading', 'Deep Root', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Herb Green', '--primary', '#5A8A4A', '90, 138, 74'),
                    ('secondary', 'Clay', '--secondary', '#9E7A5A', '158, 122, 90'),
                    ('accent', 'Calendula', '--accent', '#D4A44A', '212, 164, 74'),
                    ('border', 'Apothecary Border', '--border', '#D8D0C0', '216, 208, 192'),
                    ('success', 'Comfrey', '--success', '#4A9E5A', '74, 158, 90'),
                    ('warning', 'Turmeric', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Bloodroot', '--error', '#B85A3A', '184, 90, 58'),
                ]
            },
            {
                'name': 'Glass Skin',
                'category': 'beauty',
                'mood': 'luminous',
                'colors': [
                    ('background', 'Glass White', '--background', '#F0F4F8', '240, 244, 248'),
                    ('text', 'Dew Gray', '--text', '#4A5664', '74, 86, 100'),
                    ('heading', 'Deep Dew', '--heading', '#3A4654', '58, 70, 84'),
                    ('primary', 'Hydration Blue', '--primary', '#6BA5C4', '107, 165, 196'),
                    ('secondary', 'Pearl', '--secondary', '#D8E0E8', '216, 224, 232'),
                    ('accent', 'Coral', '--accent', '#D47A7A', '212, 122, 122'),
                    ('border', 'Glass Border', '--border', '#C8D4E0', '200, 212, 224'),
                    ('success', 'Aloe', '--success', '#5ABA8A', '90, 186, 138'),
                    ('warning', 'Vitamin C', '--warning', '#D4B44A', '212, 180, 74'),
                    ('error', 'Irritation', '--error', '#C46B6B', '196, 107, 107'),
                ]
            },

            # ============================================
            # CATEGORY: tech (7 palettes)
            # Electronics, gadgets, SaaS
            # ============================================
            {
                'name': 'Cyber Tech',
                'category': 'tech',
                'mood': 'futuristic',
                'colors': [
                    ('background', 'Terminal White', '--background', '#F8FAFC', '248, 250, 252'),
                    ('text', 'Code Gray', '--text', '#1E2430', '30, 36, 48'),
                    ('heading', 'Deep Code', '--heading', '#141824', '20, 24, 36'),
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
                    ('heading', 'Deep Space', '--heading', '#1C1C20', '28, 28, 32'),
                    ('primary', 'Apple Blue', '--primary', '#2A6BC4', '42, 107, 196'),
                    ('secondary', 'Silver', '--secondary', '#A8ACB4', '168, 172, 180'),
                    ('accent', 'Product Red', '--accent', '#D42A3A', '212, 42, 58'),
                    ('border', 'Space Border', '--border', '#D0D0D4', '208, 208, 212'),
                    ('success', 'Mint', '--success', '#2AC47A', '42, 196, 122'),
                    ('warning', 'Amber', '--warning', '#D49E2A', '212, 158, 42'),
                    ('error', 'Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },
            {
                'name': 'Gaming RGB',
                'category': 'tech',
                'mood': 'energetic',
                'colors': [
                    ('background', 'Dark Mode', '--background', '#12141A', '18, 20, 26'),
                    ('text', 'Light Gray', '--text', '#C8CCD4', '200, 204, 212'),
                    ('heading', 'White', '--heading', '#E8EAF0', '232, 234, 240'),
                    ('primary', 'RGB Purple', '--primary', '#8A4AC4', '138, 74, 196'),
                    ('secondary', 'Dark Gray', '--secondary', '#2A2E3A', '42, 46, 58'),
                    ('accent', 'RGB Cyan', '--accent', '#2AC4C4', '42, 196, 196'),
                    ('border', 'RGB Border', '--border', '#2A2E3A', '42, 46, 58'),
                    ('success', 'RGB Green', '--success', '#2AC45A', '42, 196, 90'),
                    ('warning', 'RGB Yellow', '--warning', '#D4C42A', '212, 196, 42'),
                    ('error', 'RGB Red', '--error', '#D42A4A', '212, 42, 74'),
                ]
            },
            {
                'name': 'SaaS Pro',
                'category': 'tech',
                'mood': 'professional',
                'colors': [
                    ('background', 'SaaS White', '--background', '#F9FAFB', '249, 250, 251'),
                    ('text', 'Slate', '--text', '#1F2937', '31, 41, 55'),
                    ('heading', 'Deep Slate', '--heading', '#111827', '17, 24, 39'),
                    ('primary', 'Indigo', '--primary', '#4F46E5', '79, 70, 229'),
                    ('secondary', 'Cool Gray', '--secondary', '#6B7280', '107, 114, 128'),
                    ('accent', 'Sky', '--accent', '#0EA5E9', '14, 165, 233'),
                    ('border', 'SaaS Border', '--border', '#E5E7EB', '229, 231, 235'),
                    ('success', 'Emerald', '--success', '#059669', '5, 150, 105'),
                    ('warning', 'Amber', '--warning', '#D97706', '217, 119, 6'),
                    ('error', 'Rose', '--error', '#E11D48', '225, 29, 72'),
                ]
            },
            {
                'name': 'Quantum',
                'category': 'tech',
                'mood': 'innovative',
                'colors': [
                    ('background', 'Quantum White', '--background', '#F5F7FA', '245, 247, 250'),
                    ('text', 'Quantum Gray', '--text', '#2A3040', '42, 48, 64'),
                    ('heading', 'Deep Quantum', '--heading', '#1A2030', '26, 32, 48'),
                    ('primary', 'Quantum Purple', '--primary', '#6A4E9B', '106, 78, 155'),
                    ('secondary', 'Dark Matter', '--secondary', '#1A1A2E', '26, 26, 46'),
                    ('accent', 'Neon Cyan', '--accent', '#00FFF5', '0, 255, 245'),
                    ('border', 'Quantum Border', '--border', '#D0D4E0', '208, 212, 224'),
                    ('success', 'Quantum Green', '--success', '#00FF9F', '0, 255, 159'),
                    ('warning', 'Quantum Yellow', '--warning', '#FFE600', '255, 230, 0'),
                    ('error', 'Quantum Red', '--error', '#FF3A3A', '255, 58, 58'),
                ]
            },
            {
                'name': 'Smart Home',
                'category': 'tech',
                'mood': 'friendly',
                'colors': [
                    ('background', 'Home White', '--background', '#F5F7F5', '245, 247, 245'),
                    ('text', 'Warm Gray', '--text', '#3A403A', '58, 64, 58'),
                    ('heading', 'Deep Warm', '--heading', '#2A302A', '42, 48, 42'),
                    ('primary', 'Smart Blue', '--primary', '#4A8AB8', '74, 138, 184'),
                    ('secondary', 'Slate', '--secondary', '#6B7A8A', '107, 122, 138'),
                    ('accent', 'Warm Light', '--accent', '#D4A84A', '212, 168, 74'),
                    ('border', 'Home Border', '--border', '#D0D8D0', '208, 216, 208'),
                    ('success', 'Connected Green', '--success', '#4AB85A', '74, 184, 90'),
                    ('warning', 'Alert Orange', '--warning', '#E58A2A', '229, 138, 42'),
                    ('error', 'Disconnected Red', '--error', '#D44A4A', '212, 74, 74'),
                ]
            },
            {
                'name': 'Developer Dark',
                'category': 'tech',
                'mood': 'focused',
                'colors': [
                    ('background', 'Editor Black', '--background', '#1E1E24', '30, 30, 36'),
                    ('text', 'Code Light', '--text', '#D4D4D8', '212, 212, 216'),
                    ('heading', 'White', '--heading', '#E8E8EC', '232, 232, 236'),
                    ('primary', 'Syntax Blue', '--primary', '#569CD6', '86, 156, 214'),
                    ('secondary', 'Comment Gray', '--secondary', '#6A9955', '106, 153, 85'),
                    ('accent', 'String Orange', '--accent', '#CE9178', '206, 145, 120'),
                    ('border', 'Editor Border', '--border', '#3A3A40', '58, 58, 64'),
                    ('success', 'Test Green', '--success', '#4EC9B0', '78, 201, 176'),
                    ('warning', 'Warning Yellow', '--warning', '#DCDCAA', '220, 220, 170'),
                    ('error', 'Error Red', '--error', '#F44747', '244, 71, 71'),
                ]
            },

            # ============================================
            # CATEGORY: home (7 palettes)
            # Furniture, decor, interior design
            # ============================================
            {
                'name': 'Modern Living',
                'category': 'home',
                'mood': 'modern',
                'colors': [
                    ('background', 'Living White', '--background', '#F5F3F0', '245, 243, 240'),
                    ('text', 'Charcoal', '--text', '#2C2A28', '44, 42, 40'),
                    ('heading', 'Deep Charcoal', '--heading', '#1C1A18', '28, 26, 24'),
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
                    ('heading', 'Deep Warm', '--heading', '#3A3630', '58, 54, 48'),
                    ('primary', 'Dusty Blue', '--primary', '#7A9AB8', '122, 154, 184'),
                    ('secondary', 'Pale Pink', '--secondary', '#D4B8B8', '212, 184, 184'),
                    ('accent', 'Mustard', '--accent', '#D4B44A', '212, 180, 74'),
                    ('border', 'Hygge Border', '--border', '#E0DCD4', '224, 220, 212'),
                    ('success', 'Mint', '--success', '#7AB89E', '122, 184, 158'),
                    ('warning', 'Sand', '--warning', '#D4B88A', '212, 184, 138'),
                    ('error', 'Coral', '--error', '#C47A7A', '196, 122, 122'),
                ]
            },
            {
                'name': 'Industrial Loft',
                'category': 'home',
                'mood': 'urban',
                'colors': [
                    ('background', 'Loft White', '--background', '#F0EEEA', '240, 238, 234'),
                    ('text', 'Iron Gray', '--text', '#3A3A38', '58, 58, 56'),
                    ('heading', 'Cast Iron', '--heading', '#2A2A28', '42, 42, 40'),
                    ('primary', 'Exposed Brick', '--primary', '#A85A4A', '168, 90, 74'),
                    ('secondary', 'Concrete', '--secondary', '#8A8A84', '138, 138, 132'),
                    ('accent', 'Copper Pipe', '--accent', '#C47A4A', '196, 122, 74'),
                    ('border', 'Industrial Border', '--border', '#D0CEC8', '208, 206, 200'),
                    ('success', 'Safety Green', '--success', '#5AAA5A', '90, 170, 90'),
                    ('warning', 'Caution Yellow', '--warning', '#D4C04A', '212, 192, 74'),
                    ('error', 'Warning Red', '--error', '#C44A4A', '196, 74, 74'),
                ]
            },
            {
                'name': 'Coastal Living',
                'category': 'home',
                'mood': 'calm',
                'colors': [
                    ('background', 'Sea Foam', '--background', '#F0F5F5', '240, 245, 245'),
                    ('text', 'Driftwood', '--text', '#4A504E', '74, 80, 78'),
                    ('heading', 'Deep Water', '--heading', '#2A3A3A', '42, 58, 58'),
                    ('primary', 'Ocean Blue', '--primary', '#4A8AA8', '74, 138, 168'),
                    ('secondary', 'Sand', '--secondary', '#D4C8B0', '212, 200, 176'),
                    ('accent', 'Coral', '--accent', '#D47A6B', '212, 122, 107'),
                    ('border', 'Coastal Border', '--border', '#C8D8D8', '200, 216, 216'),
                    ('success', 'Seagrass', '--success', '#5A9E7A', '90, 158, 122'),
                    ('warning', 'Sunset', '--warning', '#D4A06B', '212, 160, 107'),
                    ('error', 'Starfish', '--error', '#C46B5A', '196, 107, 90'),
                ]
            },
            {
                'name': 'Rustic Farmhouse',
                'category': 'home',
                'mood': 'rustic',
                'colors': [
                    ('background', 'Farmhouse White', '--background', '#F8F4EE', '248, 244, 238'),
                    ('text', 'Barn Brown', '--text', '#4A3A2A', '74, 58, 42'),
                    ('heading', 'Deep Barn', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Barn Red', '--primary', '#8A4A3A', '138, 74, 58'),
                    ('secondary', 'Hay', '--secondary', '#C4A86B', '196, 168, 107'),
                    ('accent', 'Sage', '--accent', '#7A9E7A', '122, 158, 122'),
                    ('border', 'Farmhouse Border', '--border', '#E0D8C8', '224, 216, 200'),
                    ('success', 'Forest', '--success', '#4A7A4A', '74, 122, 74'),
                    ('warning', 'Pumpkin', '--warning', '#D47A3A', '212, 122, 58'),
                    ('error', 'Brick', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },
            {
                'name': 'Minimalist White',
                'category': 'home',
                'mood': 'minimal',
                'colors': [
                    ('background', 'Pure White', '--background', '#FAFAFA', '250, 250, 250'),
                    ('text', 'Soft Black', '--text', '#2A2A2A', '42, 42, 42'),
                    ('heading', 'Deep Soft', '--heading', '#1A1A1A', '26, 26, 26'),
                    ('primary', 'Warm Gray', '--primary', '#9E9E9E', '158, 158, 158'),
                    ('secondary', 'Light Gray', '--secondary', '#D0D0D0', '208, 208, 208'),
                    ('accent', 'Black', '--accent', '#1A1A1A', '26, 26, 26'),
                    ('border', 'Minimal Border', '--border', '#E0E0E0', '224, 224, 224'),
                    ('success', 'Mint', '--success', '#7AB89E', '122, 184, 158'),
                    ('warning', 'Sand', '--warning', '#D4B88A', '212, 184, 138'),
                    ('error', 'Coral', '--error', '#C47A7A', '196, 122, 122'),
                ]
            },
            {
                'name': 'Bohemian Rhapsody',
                'category': 'home',
                'mood': 'eclectic',
                'colors': [
                    ('background', 'Boho Cream', '--background', '#FDF8F0', '253, 248, 240'),
                    ('text', 'Spice Brown', '--text', '#4A3A2A', '74, 58, 42'),
                    ('heading', 'Deep Spice', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Deep Purple', '--primary', '#6B3A6B', '107, 58, 107'),
                    ('secondary', 'Teal', '--secondary', '#2A8A7A', '42, 138, 122'),
                    ('accent', 'Gold', '--accent', '#C4A44A', '196, 164, 74'),
                    ('border', 'Boho Border', '--border', '#E0D4C0', '224, 212, 192'),
                    ('success', 'Sage', '--success', '#7A9E7A', '122, 158, 122'),
                    ('warning', 'Copper', '--warning', '#C47A4A', '196, 122, 74'),
                    ('error', 'Brick', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },

            # ============================================
            # CATEGORY: food (7 palettes)
            # Restaurants, cafes, gourmet
            # ============================================
            {
                'name': 'Artisan Coffee',
                'category': 'food',
                'mood': 'warm',
                'colors': [
                    ('background', 'Cream', '--background', '#FDF8F0', '253, 248, 240'),
                    ('text', 'Espresso', '--text', '#3A2A1E', '58, 42, 30'),
                    ('heading', 'Deep Espresso', '--heading', '#2A1A0E', '42, 26, 14'),
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
                    ('heading', 'Deep Forest', '--heading', '#1A2A1A', '26, 42, 26'),
                    ('primary', 'Fresh Green', '--primary', '#5A9E4A', '90, 158, 74'),
                    ('secondary', 'Earth', '--secondary', '#8A6B4A', '138, 107, 74'),
                    ('accent', 'Carrot', '--accent', '#D47A3A', '212, 122, 58'),
                    ('border', 'Grocery Border', '--border', '#D8E0C8', '216, 224, 200'),
                    ('success', 'Lime', '--success', '#6BC42A', '107, 196, 42'),
                    ('warning', 'Lemon', '--warning', '#D4C42A', '212, 196, 42'),
                    ('error', 'Tomato', '--error', '#D44A3A', '212, 74, 58'),
                ]
            },
            {
                'name': 'Gourmet Bakery',
                'category': 'food',
                'mood': 'sweet',
                'colors': [
                    ('background', 'Buttercream', '--background', '#FDF6E8', '253, 246, 232'),
                    ('text', 'Chocolate', '--text', '#3A2A1A', '58, 42, 26'),
                    ('heading', 'Dark Chocolate', '--heading', '#2A1A0A', '42, 26, 10'),
                    ('primary', 'Caramel', '--primary', '#C48A4A', '196, 138, 74'),
                    ('secondary', 'Vanilla', '--secondary', '#E8D4B4', '232, 212, 180'),
                    ('accent', 'Strawberry', '--accent', '#D45A7A', '212, 90, 122'),
                    ('border', 'Bakery Border', '--border', '#E8DCC8', '232, 220, 200'),
                    ('success', 'Pistachio', '--success', '#7AB86B', '122, 184, 107'),
                    ('warning', 'Lemon', '--warning', '#D4C44A', '212, 196, 74'),
                    ('error', 'Raspberry', '--error', '#C44A6B', '196, 74, 107'),
                ]
            },
            {
                'name': 'Wine & Spirits',
                'category': 'food',
                'mood': 'sophisticated',
                'colors': [
                    ('background', 'Wine Cream', '--background', '#FCF8F2', '252, 248, 242'),
                    ('text', 'Burgundy', '--text', '#3A1A2A', '58, 26, 42'),
                    ('heading', 'Deep Burgundy', '--heading', '#2A0A1A', '42, 10, 26'),
                    ('primary', 'Wine Red', '--primary', '#7A2A4A', '122, 42, 74'),
                    ('secondary', 'Gold', '--secondary', '#C4A44A', '196, 164, 74'),
                    ('accent', 'Cream', '--accent', '#F0E4D0', '240, 228, 208'),
                    ('border', 'Wine Border', '--border', '#D8C8C0', '216, 200, 192'),
                    ('success', 'Olive', '--success', '#5A8A4A', '90, 138, 74'),
                    ('warning', 'Amber', '--warning', '#D49E4A', '212, 158, 74'),
                    ('error', 'Crimson', '--error', '#A82A3A', '168, 42, 58'),
                ]
            },
            {
                'name': 'Fresh Seafood',
                'category': 'food',
                'mood': 'fresh',
                'colors': [
                    ('background', 'Sea White', '--background', '#F0F5F8', '240, 245, 248'),
                    ('text', 'Deep Blue', '--text', '#1A2A4A', '26, 42, 74'),
                    ('heading', 'Ocean Depth', '--heading', '#0A1A3A', '10, 26, 58'),
                    ('primary', 'Ocean Blue', '--primary', '#2A6B9E', '42, 107, 158'),
                    ('secondary', 'Coral', '--secondary', '#D47A6B', '212, 122, 107'),
                    ('accent', 'White', '--accent', '#FAFAFA', '250, 250, 250'),
                    ('border', 'Sea Border', '--border', '#C8D8E8', '200, 216, 232'),
                    ('success', 'Seaweed', '--success', '#4A9E6B', '74, 158, 107'),
                    ('warning', 'Citrus', '--warning', '#D4B44A', '212, 180, 74'),
                    ('error', 'Coral Red', '--error', '#D45A5A', '212, 90, 90'),
                ]
            },
            {
                'name': 'Farm Fresh',
                'category': 'food',
                'mood': 'rustic',
                'colors': [
                    ('background', 'Farm White', '--background', '#F8F4EA', '248, 244, 234'),
                    ('text', 'Soil Brown', '--text', '#4A3A28', '74, 58, 40'),
                    ('heading', 'Deep Soil', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Barn Red', '--primary', '#8A4A3A', '138, 74, 58'),
                    ('secondary', 'Hay', '--secondary', '#C4A86B', '196, 168, 107'),
                    ('accent', 'Green', '--accent', '#5A9E4A', '90, 158, 74'),
                    ('border', 'Farm Border', '--border', '#D8D0C0', '216, 208, 192'),
                    ('success', 'Harvest Green', '--success', '#4A8A4A', '74, 138, 74'),
                    ('warning', 'Pumpkin', '--warning', '#D47A3A', '212, 122, 58'),
                    ('error', 'Brick', '--error', '#A85A4A', '168, 90, 74'),
                ]
            },
            {
                'name': 'Sweet Treats',
                'category': 'food',
                'mood': 'playful',
                'colors': [
                    ('background', 'Marshmallow', '--background', '#FDF8F8', '253, 248, 248'),
                    ('text', 'Chocolate', '--text', '#3A2A2A', '58, 42, 42'),
                    ('heading', 'Dark Chocolate', '--heading', '#2A1A1A', '42, 26, 26'),
                    ('primary', 'Cotton Candy', '--primary', '#D4A0B8', '212, 160, 184'),
                    ('secondary', 'Mint', '--secondary', '#7AC49E', '122, 196, 158'),
                    ('accent', 'Lemon', '--accent', '#D4C44A', '212, 196, 74'),
                    ('border', 'Treats Border', '--border', '#E8D8D8', '232, 216, 216'),
                    ('success', 'Lime', '--success', '#6BC45A', '107, 196, 90'),
                    ('warning', 'Orange', '--warning', '#D48A3A', '212, 138, 58'),
                    ('error', 'Cherry', '--error', '#D44A5A', '212, 74, 90'),
                ]
            },

            # ============================================
            # CATEGORY: pet (7 palettes)
            # Pet supplies, veterinary, animal care
            # ============================================
            {
                'name': 'Pet Paradise',
                'category': 'pet',
                'mood': 'playful',
                'colors': [
                    ('background', 'Paradise White', '--background', '#F5F8F5', '245, 248, 245'),
                    ('text', 'Forest Brown', '--text', '#3A3A2A', '58, 58, 42'),
                    ('heading', 'Deep Forest', '--heading', '#2A2A1A', '42, 42, 26'),
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
                    ('heading', 'Deep Whisker', '--heading', '#3A3430', '58, 52, 48'),
                    ('primary', 'Lavender', '--primary', '#B89EC4', '184, 158, 196'),
                    ('secondary', 'Mauve', '--secondary', '#C4A0B8', '196, 160, 184'),
                    ('accent', 'Peach', '--accent', '#D4A88A', '212, 168, 138'),
                    ('border', 'Cozy Border', '--border', '#E0D8D4', '224, 216, 212'),
                    ('success', 'Catnip Green', '--success', '#6BBA7A', '107, 186, 122'),
                    ('warning', 'Tuna', '--warning', '#D4B06B', '212, 176, 107'),
                    ('error', 'Scratch Red', '--error', '#C46B6B', '196, 107, 107'),
                ]
            },
            {
                'name': 'Dog Park',
                'category': 'pet',
                'mood': 'energetic',
                'colors': [
                    ('background', 'Park White', '--background', '#F5F7F0', '245, 247, 240'),
                    ('text', 'Trail Brown', '--text', '#4A3A2A', '74, 58, 42'),
                    ('heading', 'Deep Trail', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Forest Green', '--primary', '#4A7A4A', '74, 122, 74'),
                    ('secondary', 'Bark Brown', '--secondary', '#8A6B4A', '138, 107, 74'),
                    ('accent', 'Frisbee Orange', '--accent', '#D47A3A', '212, 122, 58'),
                    ('border', 'Park Border', '--border', '#D8E0C8', '216, 224, 200'),
                    ('success', 'Fresh Grass', '--success', '#5AC45A', '90, 196, 90'),
                    ('warning', 'Tennis Ball', '--warning', '#D4C42A', '212, 196, 42'),
                    ('error', 'Leash Red', '--error', '#C44A4A', '196, 74, 74'),
                ]
            },
            {
                'name': 'Aquarium Life',
                'category': 'pet',
                'mood': 'calm',
                'colors': [
                    ('background', 'Aqua White', '--background', '#F0F5F8', '240, 245, 248'),
                    ('text', 'Deep Water', '--text', '#1A2A3A', '26, 42, 58'),
                    ('heading', 'Ocean Depth', '--heading', '#0A1A2A', '10, 26, 42'),
                    ('primary', 'Aqua Blue', '--primary', '#3A8AB8', '58, 138, 184'),
                    ('secondary', 'Coral', '--secondary', '#D47A6B', '212, 122, 107'),
                    ('accent', 'Seafoam', '--accent', '#7AC4B8', '122, 196, 184'),
                    ('border', 'Aqua Border', '--border', '#C8D8E8', '200, 216, 232'),
                    ('success', 'Algae Green', '--success', '#4AA86B', '74, 168, 107'),
                    ('warning', 'Goldfish', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Anemone Red', '--error', '#D45A5A', '212, 90, 90'),
                ]
            },
            {
                'name': 'Pet Boutique',
                'category': 'pet',
                'mood': 'luxurious',
                'colors': [
                    ('background', 'Boutique White', '--background', '#FDF9F5', '253, 249, 245'),
                    ('text', 'Rich Brown', '--text', '#3A2E28', '58, 46, 40'),
                    ('heading', 'Deep Rich', '--heading', '#2A1E18', '42, 30, 24'),
                    ('primary', 'Burgundy', '--primary', '#7A2A3A', '122, 42, 58'),
                    ('secondary', 'Gold', '--secondary', '#C4A44A', '196, 164, 74'),
                    ('accent', 'Cream', '--accent', '#F0E4D4', '240, 228, 212'),
                    ('border', 'Boutique Border', '--border', '#E0D8D0', '224, 216, 208'),
                    ('success', 'Emerald', '--success', '#2A7A4A', '42, 122, 74'),
                    ('warning', 'Amber', '--warning', '#D49E4A', '212, 158, 74'),
                    ('error', 'Ruby', '--error', '#A82A3A', '168, 42, 58'),
                ]
            },
            {
                'name': 'Wild Bird',
                'category': 'pet',
                'mood': 'natural',
                'colors': [
                    ('background', 'Nest White', '--background', '#F5F2EA', '245, 242, 234'),
                    ('text', 'Branch Brown', '--text', '#4A3A28', '74, 58, 40'),
                    ('heading', 'Deep Branch', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Robin Blue', '--primary', '#5A8AB8', '90, 138, 184'),
                    ('secondary', 'Moss', '--secondary', '#7A9E5A', '122, 158, 90'),
                    ('accent', 'Cardinal Red', '--accent', '#C42A3A', '196, 42, 58'),
                    ('border', 'Nest Border', '--border', '#D8D0C0', '216, 208, 192'),
                    ('success', 'Leaf Green', '--success', '#4A9E4A', '74, 158, 74'),
                    ('warning', 'Sunflower', '--warning', '#D4B42A', '212, 180, 42'),
                    ('error', 'Berry Red', '--error', '#B83A4A', '184, 58, 74'),
                ]
            },
            {
                'name': 'Equine Elegance',
                'category': 'pet',
                'mood': 'elegant',
                'colors': [
                    ('background', 'Stable White', '--background', '#F8F4EE', '248, 244, 238'),
                    ('text', 'Leather Brown', '--text', '#4A3A2A', '74, 58, 42'),
                    ('heading', 'Deep Leather', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Saddle Brown', '--primary', '#8A6B4A', '138, 107, 74'),
                    ('secondary', 'Hay', '--secondary', '#C4A86B', '196, 168, 107'),
                    ('accent', 'Ribbon Blue', '--accent', '#4A6B9E', '74, 107, 158'),
                    ('border', 'Stable Border', '--border', '#D8D0C0', '216, 208, 192'),
                    ('success', 'Pasture Green', '--success', '#5A9E5A', '90, 158, 90'),
                    ('warning', 'Golden', '--warning', '#D4A44A', '212, 164, 74'),
                    ('error', 'Rust', '--error', '#B86A4A', '184, 106, 74'),
                ]
            },

            # ============================================
            # CATEGORY: sports (7 palettes)
            # Athletic, fitness, outdoor
            # ============================================
            {
                'name': 'Athletic Performance',
                'category': 'sports',
                'mood': 'energetic',
                'colors': [
                    ('background', 'Performance White', '--background', '#F5F7F8', '245, 247, 248'),
                    ('text', 'Navy', '--text', '#1A2436', '26, 36, 54'),
                    ('heading', 'Deep Navy', '--heading', '#0F1624', '15, 22, 36'),
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
                    ('heading', 'Deep Forest', '--heading', '#1A2A1A', '26, 42, 26'),
                    ('primary', 'Pine Green', '--primary', '#3A6B3A', '58, 107, 58'),
                    ('secondary', 'Trail Brown', '--secondary', '#7A5A3A', '122, 90, 58'),
                    ('accent', 'Sunset Orange', '--accent', '#D47A3A', '212, 122, 58'),
                    ('border', 'Trail Border', '--border', '#D8D4C4', '216, 212, 196'),
                    ('success', 'Meadow', '--success', '#4A9E4A', '74, 158, 74'),
                    ('warning', 'Signal Yellow', '--warning', '#D4C42A', '212, 196, 42'),
                    ('error', 'Emergency Red', '--error', '#C44A4A', '196, 74, 74'),
                ]
            },
            {
                'name': 'Yoga & Wellness',
                'category': 'sports',
                'mood': 'calm',
                'colors': [
                    ('background', 'Zen White', '--background', '#F5F5F0', '245, 245, 240'),
                    ('text', 'Stone Gray', '--text', '#4A4A44', '74, 74, 68'),
                    ('heading', 'Deep Stone', '--heading', '#3A3A34', '58, 58, 52'),
                    ('primary', 'Lavender', '--primary', '#B89EC4', '184, 158, 196'),
                    ('secondary', 'Sage', '--secondary', '#8AAA7A', '138, 170, 122'),
                    ('accent', 'Peach', '--accent', '#D4A88A', '212, 168, 138'),
                    ('border', 'Zen Border', '--border', '#D8D8D0', '216, 216, 208'),
                    ('success', 'Mint', '--success', '#7AB89E', '122, 184, 158'),
                    ('warning', 'Honey', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Coral', '--error', '#C47A7A', '196, 122, 122'),
                ]
            },
            {
                'name': 'Surf Shop',
                'category': 'sports',
                'mood': 'beachy',
                'colors': [
                    ('background', 'Surf White', '--background', '#F0F5F8', '240, 245, 248'),
                    ('text', 'Deep Blue', '--text', '#1A2A4A', '26, 42, 74'),
                    ('heading', 'Ocean Depth', '--heading', '#0A1A3A', '10, 26, 58'),
                    ('primary', 'Turquoise', '--primary', '#2A9E9E', '42, 158, 158'),
                    ('secondary', 'Coral', '--secondary', '#D47A6B', '212, 122, 107'),
                    ('accent', 'Sand', '--accent', '#E8D8C0', '232, 216, 192'),
                    ('border', 'Surf Border', '--border', '#C8D8E8', '200, 216, 232'),
                    ('success', 'Wave Green', '--success', '#4AB86B', '74, 184, 107'),
                    ('warning', 'Sunset', '--warning', '#D4A06B', '212, 160, 107'),
                    ('error', 'Jellyfish Red', '--error', '#D45A5A', '212, 90, 90'),
                ]
            },
            {
                'name': 'Fitness Pro',
                'category': 'sports',
                'mood': 'intense',
                'colors': [
                    ('background', 'Gym White', '--background', '#F0F2F5', '240, 242, 245'),
                    ('text', 'Iron Gray', '--text', '#2A2E35', '42, 46, 53'),
                    ('heading', 'Deep Iron', '--heading', '#1A1E24', '26, 30, 36'),
                    ('primary', 'Charcoal', '--primary', '#3A3A40', '58, 58, 64'),
                    ('secondary', 'Neon Green', '--secondary', '#5AC42A', '90, 196, 42'),
                    ('accent', 'Neon Orange', '--accent', '#E58A2A', '229, 138, 42'),
                    ('border', 'Gym Border', '--border', '#C8CCD4', '200, 204, 212'),
                    ('success', 'PR Green', '--success', '#2AC45A', '42, 196, 90'),
                    ('warning', 'Rest Yellow', '--warning', '#D4C42A', '212, 196, 42'),
                    ('error', 'Overtraining Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },
            {
                'name': 'Golf Course',
                'category': 'sports',
                'mood': 'refined',
                'colors': [
                    ('background', 'Fairway White', '--background', '#F5F7F0', '245, 247, 240'),
                    ('text', 'Clubhouse Navy', '--text', '#1A2436', '26, 36, 54'),
                    ('heading', 'Deep Navy', '--heading', '#0F1624', '15, 22, 36'),
                    ('primary', 'Fairway Green', '--primary', '#4A8A4A', '74, 138, 74'),
                    ('secondary', 'Sand Trap', '--secondary', '#D4C8A8', '212, 200, 168'),
                    ('accent', 'Flag Red', '--accent', '#C42A3A', '196, 42, 58'),
                    ('border', 'Course Border', '--border', '#D8E0C8', '216, 224, 200'),
                    ('success', 'Birdie Green', '--success', '#2A9E4A', '42, 158, 74'),
                    ('warning', 'Bunker Sand', '--warning', '#D4B88A', '212, 184, 138'),
                    ('error', 'Out of Bounds', '--error', '#A82A3A', '168, 42, 58'),
                ]
            },
            {
                'name': 'Winter Sports',
                'category': 'sports',
                'mood': 'crisp',
                'colors': [
                    ('background', 'Snow White', '--background', '#F0F4F8', '240, 244, 248'),
                    ('text', 'Alpine Navy', '--text', '#1A2436', '26, 36, 54'),
                    ('heading', 'Deep Alpine', '--heading', '#0F1624', '15, 22, 36'),
                    ('primary', 'Glacier Blue', '--primary', '#4A7A9E', '74, 122, 158'),
                    ('secondary', 'Ice Gray', '--secondary', '#9EAAB8', '158, 170, 184'),
                    ('accent', 'Gondola Red', '--accent', '#C42A3A', '196, 42, 58'),
                    ('border', 'Snow Border', '--border', '#C8D4E0', '200, 212, 224'),
                    ('success', 'Evergreen', '--success', '#2A6B3A', '42, 107, 58'),
                    ('warning', 'Avalanche Yellow', '--warning', '#D4C42A', '212, 196, 42'),
                    ('error', 'Frostbite Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },

            # ============================================
            # CATEGORY: toys (7 palettes)
            # Children's toys, games, educational
            # ============================================
            {
                'name': 'Rainbow Fun',
                'category': 'toys',
                'mood': 'playful',
                'colors': [
                    ('background', 'Cloud White', '--background', '#F8FAFC', '248, 250, 252'),
                    ('text', 'Playful Navy', '--text', '#2A3A5A', '42, 58, 90'),
                    ('heading', 'Deep Playful', '--heading', '#1A2A4A', '26, 42, 74'),
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
                    ('heading', 'Deep Soft', '--heading', '#3A3434', '58, 52, 52'),
                    ('primary', 'Baby Blue', '--primary', '#8AC4E5', '138, 196, 229'),
                    ('secondary', 'Baby Pink', '--secondary', '#E5B8C4', '229, 184, 196'),
                    ('accent', 'Mint', '--accent', '#7AE5B8', '122, 229, 184'),
                    ('border', 'Baby Border', '--border', '#E0D8D8', '224, 216, 216'),
                    ('success', 'Soft Green', '--success', '#7AC47A', '122, 196, 122'),
                    ('warning', 'Soft Yellow', '--warning', '#E5D47A', '229, 212, 122'),
                    ('error', 'Soft Coral', '--error', '#E58A8A', '229, 138, 138'),
                ]
            },
            {
                'name': 'Educational Toys',
                'category': 'toys',
                'mood': 'smart',
                'colors': [
                    ('background', 'Learning White', '--background', '#F5F7FA', '245, 247, 250'),
                    ('text', 'Study Navy', '--text', '#2A3A5A', '42, 58, 90'),
                    ('heading', 'Deep Study', '--heading', '#1A2A4A', '26, 42, 74'),
                    ('primary', 'Primary Red', '--primary', '#E54A4A', '229, 74, 74'),
                    ('secondary', 'Primary Blue', '--secondary', '#4A6BE5', '74, 107, 229'),
                    ('accent', 'Primary Yellow', '--accent', '#E5D44A', '229, 212, 74'),
                    ('border', 'Learning Border', '--border', '#D0D8E0', '208, 216, 224'),
                    ('success', 'Correct Green', '--success', '#4AE55A', '74, 229, 90'),
                    ('warning', 'Think Orange', '--warning', '#E5A04A', '229, 160, 74'),
                    ('error', 'Wrong Red', '--error', '#E54A5A', '229, 74, 90'),
                ]
            },
            {
                'name': 'Outdoor Play',
                'category': 'toys',
                'mood': 'adventurous',
                'colors': [
                    ('background', 'Playground White', '--background', '#F5F7F0', '245, 247, 240'),
                    ('text', 'Adventure Brown', '--text', '#4A3A2A', '74, 58, 42'),
                    ('heading', 'Deep Adventure', '--heading', '#35281A', '53, 40, 26'),
                    ('primary', 'Jungle Green', '--primary', '#4A9E4A', '74, 158, 74'),
                    ('secondary', 'Sky Blue', '--secondary', '#6BA5C4', '107, 165, 196'),
                    ('accent', 'Sunshine', '--accent', '#D4B42A', '212, 180, 42'),
                    ('border', 'Playground Border', '--border', '#D8E0C8', '216, 224, 200'),
                    ('success', 'Grass Green', '--success', '#5AC45A', '90, 196, 90'),
                    ('warning', 'Caution Orange', '--warning', '#D48A3A', '212, 138, 58'),
                    ('error', 'Ouch Red', '--error', '#D44A4A', '212, 74, 74'),
                ]
            },
            {
                'name': 'Tech Toys',
                'category': 'toys',
                'mood': 'modern',
                'colors': [
                    ('background', 'Tech White', '--background', '#F8FAFC', '248, 250, 252'),
                    ('text', 'Circuit Gray', '--text', '#2A3040', '42, 48, 64'),
                    ('heading', 'Deep Circuit', '--heading', '#1A2030', '26, 32, 48'),
                    ('primary', 'Robotic Blue', '--primary', '#2A6BC4', '42, 107, 196'),
                    ('secondary', 'Neon Green', '--secondary', '#5AC42A', '90, 196, 42'),
                    ('accent', 'Laser Orange', '--accent', '#E58A2A', '229, 138, 42'),
                    ('border', 'Tech Border', '--border', '#D0D8E8', '208, 216, 232'),
                    ('success', 'Connected Green', '--success', '#2AC45A', '42, 196, 90'),
                    ('warning', 'Low Battery', '--warning', '#E5C42A', '229, 196, 42'),
                    ('error', 'Error Red', '--error', '#E52A2A', '229, 42, 42'),
                ]
            },
            {
                'name': 'Building Blocks',
                'category': 'toys',
                'mood': 'constructive',
                'colors': [
                    ('background', 'Block White', '--background', '#F5F5F0', '245, 245, 240'),
                    ('text', 'Blueprint Gray', '--text', '#3A3A3A', '58, 58, 58'),
                    ('heading', 'Deep Blueprint', '--heading', '#2A2A2A', '42, 42, 42'),
                    ('primary', 'Block Red', '--primary', '#C42A3A', '196, 42, 58'),
                    ('secondary', 'Block Blue', '--secondary', '#2A5AC4', '42, 90, 196'),
                    ('accent', 'Block Yellow', '--accent', '#C4B42A', '196, 180, 42'),
                    ('border', 'Block Border', '--border', '#D0D0C8', '208, 208, 200'),
                    ('success', 'Block Green', '--success', '#2AC44A', '42, 196, 74'),
                    ('warning', 'Block Orange', '--warning', '#C47A2A', '196, 122, 42'),
                    ('error', 'Block Red Error', '--error', '#C42A2A', '196, 42, 42'),
                ]
            },
            {
                'name': 'Puzzle & Board Games',
                'category': 'toys',
                'mood': 'thoughtful',
                'colors': [
                    ('background', 'Board White', '--background', '#F8F5F0', '248, 245, 240'),
                    ('text', 'Game Night Navy', '--text', '#2A3A5A', '42, 58, 90'),
                    ('heading', 'Deep Game', '--heading', '#1A2A4A', '26, 42, 74'),
                    ('primary', 'Player Red', '--primary', '#C42A3A', '196, 42, 58'),
                    ('secondary', 'Player Blue', '--secondary', '#2A5AC4', '42, 90, 196'),
                    ('accent', 'Player Yellow', '--accent', '#C4B42A', '196, 180, 42'),
                    ('border', 'Board Border', '--border', '#D8D4C8', '216, 212, 200'),
                    ('success', 'Player Green', '--success', '#2AC44A', '42, 196, 74'),
                    ('warning', 'Timer Orange', '--warning', '#C47A2A', '196, 122, 42'),
                    ('error', 'Elimination Red', '--error', '#C42A2A', '196, 42, 42'),
                ]
            },

            # ============================================
            # CATEGORY: health (7 palettes)
            # Pharmacy, supplements, medical
            # ============================================
            {
                'name': 'Pharmacy',
                'category': 'health',
                'mood': 'trustworthy',
                'colors': [
                    ('background', 'Pharmacy White', '--background', '#F5F8FA', '245, 248, 250'),
                    ('text', 'Medical Navy', '--text', '#1A2A4A', '26, 42, 74'),
                    ('heading', 'Deep Medical', '--heading', '#0A1A3A', '10, 26, 58'),
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
                    ('heading', 'Deep Herbal', '--heading', '#2A2A1A', '42, 42, 26'),
                    ('primary', 'Sage', '--primary', '#7A9E7A', '122, 158, 122'),
                    ('secondary', 'Earth', '--secondary', '#8A6B4A', '138, 107, 74'),
                    ('accent', 'Botanical Orange', '--accent', '#D47A3A', '212, 122, 58'),
                    ('border', 'Natural Border', '--border', '#D8D8C8', '216, 216, 200'),
                    ('success', 'Leaf Green', '--success', '#5A9E4A', '90, 158, 74'),
                    ('warning', 'Golden', '--warning', '#D4A84A', '212, 168, 74'),
                    ('error', 'Berry Red', '--error', '#C45A5A', '196, 90, 90'),
                ]
            },
            {
                'name': 'Fitness Nutrition',
                'category': 'health',
                'mood': 'energetic',
                'colors': [
                    ('background', 'Nutrition White', '--background', '#F5F7F5', '245, 247, 245'),
                    ('text', 'Performance Black', '--text', '#1E1E1E', '30, 30, 30'),
                    ('heading', 'Deep Performance', '--heading', '#141414', '20, 20, 20'),
                    ('primary', 'Energy Orange', '--primary', '#E58A2A', '229, 138, 42'),
                    ('secondary', 'Charcoal', '--secondary', '#3A3A3A', '58, 58, 58'),
                    ('accent', 'Recovery Green', '--accent', '#5AC42A', '90, 196, 42'),
                    ('border', 'Nutrition Border', '--border', '#D0D4D0', '208, 212, 208'),
                    ('success', 'Gains Green', '--success', '#2AC45A', '42, 196, 90'),
                    ('warning', 'Hydration Blue', '--warning', '#4A9EE5', '74, 158, 229'),
                    ('error', 'Overtraining Red', '--error', '#E52A2A', '229, 42, 42'),
                ]
            },
            {
                'name': 'Spa & Relaxation',
                'category': 'health',
                'mood': 'calm',
                'colors': [
                    ('background', 'Spa White', '--background', '#F2F5F2', '242, 245, 242'),
                    ('text', 'Stone Gray', '--text', '#4A504A', '74, 80, 74'),
                    ('heading', 'Deep Stone', '--heading', '#3A403A', '58, 64, 58'),
                    ('primary', 'Lavender', '--primary', '#C4A0D4', '196, 160, 212'),
                    ('secondary', 'Mint', '--secondary', '#7AC49E', '122, 196, 158'),
                    ('accent', 'Peach', '--accent', '#D4A88A', '212, 168, 138'),
                    ('border', 'Spa Border', '--border', '#D0D8D0', '208, 216, 208'),
                    ('success', 'Eucalyptus', '--success', '#5A9E7A', '90, 158, 122'),
                    ('warning', 'Honey', '--warning', '#D4B86B', '212, 184, 107'),
                    ('error', 'Coral', '--error', '#C47A7A', '196, 122, 122'),
                ]
            },
            {
                'name': 'Medical Equipment',
                'category': 'health',
                'mood': 'clinical',
                'colors': [
                    ('background', 'Sterile White', '--background', '#FAFAFC', '250, 250, 252'),
                    ('text', 'Clinical Gray', '--text', '#2A303A', '42, 48, 58'),
                    ('heading', 'Deep Clinical', '--heading', '#1A202A', '26, 32, 42'),
                    ('primary', 'Diagnostic Blue', '--primary', '#1A6BC4', '26, 107, 196'),
                    ('secondary', 'Equipment Gray', '--secondary', '#7A8A9E', '122, 138, 158'),
                    ('accent', 'Monitor Green', '--accent', '#2A9E4A', '42, 158, 74'),
                    ('border', 'Clinical Border', '--border', '#D0D4E0', '208, 212, 224'),
                    ('success', 'Stable Green', '--success', '#2AC45A', '42, 196, 90'),
                    ('warning', 'Alert Orange', '--warning', '#E58A2A', '229, 138, 42'),
                    ('error', 'Critical Red', '--error', '#D42A2A', '212, 42, 42'),
                ]
            },
            {
                'name': 'Wellness Retreat',
                'category': 'health',
                'mood': 'serene',
                'colors': [
                    ('background', 'Retreat White', '--background', '#F8F5F0', '248, 245, 240'),
                    ('text', 'Earth Brown', '--text', '#4A4035', '74, 64, 53'),
                    ('heading', 'Deep Earth', '--heading', '#3A3025', '58, 48, 37'),
                    ('primary', 'Terracotta', '--primary', '#C46B4A', '196, 107, 74'),
                    ('secondary', 'Sage', '--secondary', '#8AAA7A', '138, 170, 122'),
                    ('accent', 'Lavender', '--accent', '#B89EC4', '184, 158, 196'),
                    ('border', 'Retreat Border', '--border', '#E0D8CC', '224, 216, 204'),
                    ('success', 'Herb Green', '--success', '#5A9E5A', '90, 158, 90'),
                    ('warning', 'Honey', '--warning', '#D4B06B', '212, 176, 107'),
                    ('error', 'Rose', '--error', '#C46B7A', '196, 107, 122'),
                ]
            },
            {
                'name': 'Pediatric Care',
                'category': 'health',
                'mood': 'gentle',
                'colors': [
                    ('background', 'Pediatric White', '--background', '#FDF8F8', '253, 248, 248'),
                    ('text', 'Gentle Gray', '--text', '#4A4040', '74, 64, 64'),
                    ('heading', 'Deep Gentle', '--heading', '#3A3030', '58, 48, 48'),
                    ('primary', 'Calming Blue', '--primary', '#6BA5C4', '107, 165, 196'),
                    ('secondary', 'Soft Pink', '--secondary', '#D4A8B8', '212, 168, 184'),
                    ('accent', 'Cheerful Yellow', '--accent', '#D4C46B', '212, 196, 107'),
                    ('border', 'Pediatric Border', '--border', '#E0D4D4', '224, 212, 212'),
                    ('success', 'Healing Green', '--success', '#6BBA7A', '107, 186, 122'),
                    ('warning', 'Gentle Orange', '--warning', '#D4A06B', '212, 160, 107'),
                    ('error', 'Gentle Red', '--error', '#C47A7A', '196, 122, 122'),
                ]
            },

        ]

        # Clear existing palettes (optional)
        # ColorPalette.objects.all().delete()
        # ColorPaletteColor.objects.all().delete()

        # Load palettes
        palette_count = 0
        for palette_data in palettes:
            palette, created = ColorPalette.objects.get_or_create(
                name=palette_data['name'],
                defaults={
                    'category': palette_data['category'],
                    'mood': palette_data['mood'],
                    'slug': palette_data['name'].lower().replace(' ', '-').replace('&', 'and'),
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
                palette_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created palette: {palette.name} ({palette.category})'))
            else:
                self.stdout.write(self.style.WARNING(f'• Palette exists: {palette.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully loaded {palette_count} premium color palettes!'))