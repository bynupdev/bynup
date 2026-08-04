from django.core.management.base import BaseCommand
from builder.models import ComponentCategory, Component

class Command(BaseCommand):
    help = 'Populate sample components for drag and drop builder'

    def handle(self, *args, **options):
        # Create categories
        hero_category, _ = ComponentCategory.objects.get_or_create(
            name='Hero Sections',
            slug='hero-sections',
            defaults={'description': 'Eye-catching hero sections'}
        )
        
        content_category, _ = ComponentCategory.objects.get_or_create(
            name='Content Sections',
            slug='content-sections',
            defaults={'description': 'Content display sections'}
        )
        
        # Create sample components
        components_data = [
            {
                'name': 'Simple Hero',
                'category': hero_category,
                'component_type': 'hero',
                'html_content': '''
                    <section class="hero-section" style="background: linear-gradient(135deg, #4361ee, #3a0ca3); color: white; padding: 4rem 0; text-align: center;">
                        <div class="container">
                            <h1 style="font-size: 3rem; margin-bottom: 1rem;">Your Main Headline</h1>
                            <p style="font-size: 1.2rem; max-width: 600px; margin: 0 auto 2rem;">Your compelling subheadline goes here</p>
                            <button style="background-color: #f72585; color: white; border: none; padding: 1rem 2rem; border-radius: 6px; font-size: 1.1rem;">Get Started</button>
                        </div>
                    </section>
                ''',
                'css_content': '''
                    .hero-section { min-height: 400px; display: flex; align-items: center; }
                '''
            },
            {
                'name': 'Feature Grid',
                'category': content_category,
                'component_type': 'feature',
                'html_content': '''
                    <section style="padding: 4rem 0; background: #f8f9fa;">
                        <div class="container">
                            <h2 style="text-align: center; margin-bottom: 3rem;">Our Features</h2>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
                                <div style="text-align: center; padding: 2rem; background: white; border-radius: 8px;">
                                    <i class="fas fa-rocket fa-2x" style="color: #4361ee; margin-bottom: 1rem;"></i>
                                    <h3>Fast & Reliable</h3>
                                    <p>Lightning fast performance with 99.9% uptime</p>
                                </div>
                                <div style="text-align: center; padding: 2rem; background: white; border-radius: 8px;">
                                    <i class="fas fa-shield-alt fa-2x" style="color: #4361ee; margin-bottom: 1rem;"></i>
                                    <h3>Secure</h3>
                                    <p>Enterprise-grade security for your peace of mind</p>
                                </div>
                                <div style="text-align: center; padding: 2rem; background: white; border-radius: 8px;">
                                    <i class="fas fa-support fa-2x" style="color: #4361ee; margin-bottom: 1rem;"></i>
                                    <h3>24/7 Support</h3>
                                    <p>Round-the-clock customer support</p>
                                </div>
                            </div>
                        </div>
                    </section>
                ''',
                'css_content': '''
                    .feature-grid { display: grid; gap: 2rem; }
                '''
            }
        ]
        
        for component_data in components_data:
            Component.objects.get_or_create(
                name=component_data['name'],
                category=component_data['category'],
                defaults=component_data
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated sample components')) 