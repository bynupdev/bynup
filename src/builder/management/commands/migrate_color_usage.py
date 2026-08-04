from django.core.management.base import BaseCommand
from django.db import transaction
from builder.models import PublishedPage, ColorPalette, PaletteColorUsage, ColorPaletteColor
import json

class Command(BaseCommand):
    help = 'Migrate existing color palette data to support global color sync'

    def handle(self, *args, **options):
        self.stdout.write('Migrating color palette data for global sync...')
        
        pages = PublishedPage.objects.filter(
            active_palette__isnull=False,
            active_palette_colors__isnull=False
        ).exclude(active_palette_colors={})
        
        total_pages = pages.count()
        self.stdout.write(f'Found {total_pages} pages with active palettes')
        
        migrated_count = 0
        skipped_count = 0
        
        for page in pages:
            try:
                with transaction.atomic():
                    palette = page.active_palette
                    colors_data = page.active_palette_colors
                    
                    if not isinstance(colors_data, dict):
                        self.stdout.write(self.style.WARNING(
                            f'  ⚠️ Page {page.id} has invalid colors data, skipping'
                        ))
                        skipped_count += 1
                        continue
                    
                    for var_name, color_value in colors_data.items():
                        # Get hex value
                        hex_value = color_value
                        if isinstance(color_value, dict):
                            hex_value = color_value.get('hex', '')
                        
                        if not hex_value or not hex_value.startswith('#'):
                            continue
                        
                        # Find or create palette color
                        palette_color, created = ColorPaletteColor.objects.get_or_create(
                            palette=palette,
                            variable_name=var_name,
                            defaults={
                                'name': var_name.replace('_', ' ').title(),
                                'hex_value': hex_value,
                                'color_type': 'custom',
                                'usage_count': 0
                            }
                        )
                        
                        if not created:
                            palette_color.hex_value = hex_value
                            palette_color.save()
                        
                        # Create usage record
                        usage, usage_created = PaletteColorUsage.objects.update_or_create(
                            page=page,
                            palette=palette,
                            palette_color=palette_color,
                            variable_name=var_name,
                            defaults={
                                'current_hex_value': hex_value,
                                'element_count': 1
                            }
                        )
                    
                    migrated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✅ Migrated page {page.id}: {page.brand_name}'
                    ))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'  ❌ Error migrating page {page.id}: {str(e)}'
                ))
                skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Migration complete!\n'
            f'   Pages migrated: {migrated_count}\n'
            f'   Pages skipped: {skipped_count}'
        ))