# builder/management/commands/seed_ai_designs.py

from django.core.management.base import BaseCommand
from builder.models import AIDesignTemplate
from builder.services.ai_service import AIDesignService
import json


class Command(BaseCommand):
    help = 'Seed AI designs for common combinations'
    
    def handle(self, *args, **options):
        service = AIDesignService()
        
        # Common combinations to pre-generate
        combinations = [
            ('beauty', 'luxury', 'beauty_pink'),
            ('beauty', 'modern', 'beauty_clean'),
            ('beauty', 'organic', 'beauty_glow'),
            ('fashion', 'luxury', 'fashion_luxury'),
            ('fashion', 'modern', 'fashion_modern'),
            ('technology', 'modern', 'tech_modern'),
            ('technology', 'bold', 'tech_dark'),
            ('food_beverage', 'warm', 'food_warm'),
            ('food_beverage', 'fresh', 'food_fresh'),
            ('home_decor', 'organic', 'decor_organic'),
            ('home_decor', 'warm', 'decor_warm'),
            ('health_wellness', 'calm', 'wellness_calm'),
        ]
        
        self.stdout.write(f"Seeding {len(combinations)} AI designs...")
        
        for industry, style, palette in combinations:
            # Check if already exists
            if AIDesignTemplate.objects.filter(industry=industry, style=style, palette=palette).exists():
                self.stdout.write(f"  ⏭️  {industry}/{style}/{palette} already exists")
                continue
            
            self.stdout.write(f"  🎨 Generating {industry}/{style}/{palette}...")
            
            try:
                # Generate the design
                customizations = service.generate_customizations(
                    store_name="{{STORE_NAME}}",
                    industry=industry,
                    style=style,
                    palette=palette
                )
                
                # Save it
                design = AIDesignTemplate.objects.create(
                    industry=industry,
                    style=style,
                    palette=palette,
                    customizations=customizations,
                    max_uses=3,
                    notes=f"Auto-seeded design for {industry} - {style} - {palette}"
                )
                
                self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {design.design_id[:8]}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Failed: {e}"))
        
        self.stdout.write(self.style.SUCCESS("✅ Seeding complete!"))