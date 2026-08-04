 from django.core.management.base import BaseCommand
from builder.models import ComponentCategory, Component

class Command(BaseCommand):
    help = 'Create sample drag and drop components'

    def handle(self, *args, **options):
        
        # Create categories
        categories_data = [
            {'name': 'Hero Sections', 'slug': 'hero-sections'},
            {'name': 'Content Blocks', 'slug': 'content-blocks'},
            {'name': 'Ecommerce', 'slug': 'ecommerce'},
            {'name': 'Contact Forms', 'slug': 'contact-forms'},
        ]
        
        for cat_data in categories_data:
            category, created = ComponentCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Hero Section Components
        hero_components = [
            {
                'name': 'Simple Hero',
                'category': ComponentCategory.objects.get(slug='hero-sections'),
                'component_type': 'hero',
                'html_content': '''
                    <section class="hero-section" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 0; text-align: center;">
                        <div class="container">
                            <h1 style="font-size: 3.5rem; font-weight: bold; margin-bottom: 1.5rem;">Welcome to Our Platform</h1>
                            <p style="font-size: 1.3rem; max-width: 600px; margin: 0 auto 2.5rem; opacity: 0.9;">Transform your business with our amazing solutions and services designed for success.</p>
                            <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                                <button style="background: #f72585; color: white; border: none; padding: 15px 30px; border-radius: 8px; font-size: 1.1rem; font-weight: 600; cursor: pointer;">Get Started</button>
                                <button style="background: transparent; color: white; border: 2px solid white; padding: 15px 30px; border-radius: 8px; font-size: 1.1rem; font-weight: 600; cursor: pointer;">Learn More</button>
                            </div>
                        </div>
                    </section>
                ''',
                'css_content': '''
                    .hero-section { 
                        min-height: 500px; 
                        display: flex; 
                        align-items: center; 
                    }
                    @media (max-width: 768px) {
                        .hero-section h1 { font-size: 2.5rem !important; }
                        .hero-section p { font-size: 1.1rem !important; }
                    }
                '''
            },
            {
                'name': 'Product Showcase',
                'category': ComponentCategory.objects.get(slug='ecommerce'),
                'component_type': 'product',
                'html_content': '''
                    <section style="padding: 60px 0; background: #f8f9fa;">
                        <div class="container">
                            <h2 style="text-align: center; margin-bottom: 3rem; color: #333;">Featured Products</h2>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem;">
                                <div style="background: white; border-radius: 12px; padding: 2rem; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s ease;">
                                    <div style="width: 80px; height: 80px; background: #4361ee; border-radius: 50%; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center;">
                                        <i class="fas fa-box" style="color: white; font-size: 2rem;"></i>
                                    </div>
                                    <h3 style="color: #333; margin-bottom: 1rem;">Premium Package</h3>
                                    <p style="color: #666; margin-bottom: 1.5rem;">Everything you need to get started with advanced features.</p>
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #f72585; margin-bottom: 1.5rem;">$99.99</div>
                                    <button style="background: #4361ee; color: white; border: none; padding: 12px 24px; border-radius: 6px; width: 100%; font-weight: 600; cursor: pointer;">Add to Cart</button>
                                </div>
                                <div style="background: white; border-radius: 12px; padding: 2rem; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s ease;">
                                    <div style="width: 80px; height: 80px; background: #f72585; border-radius: 50%; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center;">
                                        <i class="fas fa-star" style="color: white; font-size: 2rem;"></i>
                                    </div>
                                    <h3 style="color: #333; margin-bottom: 1rem;">Pro Package</h3>
                                    <p style="color: #666; margin-bottom: 1.5rem;">Advanced features for growing businesses and professionals.</p>
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #f72585; margin-bottom: 1.5rem;">$199.99</div>
                                    <button style="background: #4361ee; color: white; border: none; padding: 12px 24px; border-radius: 6px; width: 100%; font-weight: 600; cursor: pointer;">Add to Cart</button>
                                </div>
                            </div>
                        </div>
                    </section>
                ''',
                'css_content': '''
                    .product-card:hover { 
                        transform: translateY(-5px); 
                    }
                '''
            },
            {
                'name': 'Feature Grid',
                'category': ComponentCategory.objects.get(slug='content-blocks'),
                'component_type': 'feature',
                'html_content': '''
                    <section style="padding: 80px 0; background: white;">
                        <div class="container">
                            <h2 style="text-align: center; margin-bottom: 1rem; color: #333;">Why Choose Us</h2>
                            <p style="text-align: center; color: #666; max-width: 600px; margin: 0 auto 4rem; font-size: 1.1rem;">We provide the best solutions for your business needs with exceptional quality and support.</p>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 3rem;">
                                <div style="text-align: center;">
                                    <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #4361ee, #3a0ca3); border-radius: 50%; margin: 0 auto 1.5rem; display: flex; align-items: center; justify-content: center;">
                                        <i class="fas fa-bolt" style="color: white; font-size: 2rem;"></i>
                                    </div>
                                    <h3 style="color: #333; margin-bottom: 1rem;">Lightning Fast</h3>
                                    <p style="color: #666;">Blazing fast performance that keeps your customers engaged and satisfied.</p>
                                </div>
                                <div style="text-align: center;">
                                    <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #f72585, #b5179e); border-radius: 50%; margin: 0 auto 1.5rem; display: flex; align-items: center; justify-content: center;">
                                        <i class="fas fa-shield-alt" style="color: white; font-size: 2rem;"></i>
                                    </div>
                                    <h3 style="color: #333; margin-bottom: 1rem;">Secure & Safe</h3>
                                    <p style="color: #666;">Enterprise-grade security to protect your data and customer information.</p>
                                </div>
                                <div style="text-align: center;">
                                    <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #4cc9f0, #4361ee); border-radius: 50%; margin: 0 auto 1.5rem; display: flex; align-items: center; justify-content: center;">
                                        <i class="fas fa-support" style="color: white; font-size: 2rem;"></i>
                                    </div>
                                    <h3 style="color: #333; margin-bottom: 1rem;">24/7 Support</h3>
                                    <p style="color: #666;">Round-the-clock customer support to help you whenever you need it.</p>
                                </div>
                            </div>
                        </div>
                    </section>
                ''',
                'css_content': '''
                    .feature-item { 
                        transition: transform 0.3s ease; 
                    }
                    .feature-item:hover { 
                        transform: translateY(-10px); 
                    }
                '''
            },
            {
                'name': 'Contact Form',
                'category': ComponentCategory.objects.get(slug='contact-forms'),
                'component_type': 'contact',
                'html_content': '''
                    <section style="padding: 80px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <div class="container">
                            <div style="max-width: 800px; margin: 0 auto;">
                                <h2 style="text-align: center; margin-bottom: 1rem;">Get In Touch</h2>
                                <p style="text-align: center; margin-bottom: 3rem; opacity: 0.9;">Have questions? We'd love to hear from you. Send us a message and we'll respond as soon as possible.</p>
                                <form style="background: white; padding: 3rem; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
                                        <div>
                                            <label style="display: block; color: #333; margin-bottom: 0.5rem; font-weight: 600;">First Name</label>
                                            <input type="text" style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 1rem;" placeholder="John">
                                        </div>
                                        <div>
                                            <label style="display: block; color: #333; margin-bottom: 0.5rem; font-weight: 600;">Last Name</label>
                                            <input type="text" style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 1rem;" placeholder="Doe">
                                        </div>
                                    </div>
                                    <div style="margin-bottom: 1.5rem;">
                                        <label style="display: block; color: #333; margin-bottom: 0.5rem; font-weight: 600;">Email Address</label>
                                        <input type="email" style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 1rem;" placeholder="john@example.com">
                                    </div>
                                    <div style="margin-bottom: 1.5rem;">
                                        <label style="display: block; color: #333; margin-bottom: 0.5rem; font-weight: 600;">Message</label>
                                        <textarea style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 1rem; min-height: 120px;" placeholder="Your message here..."></textarea>
                                    </div>
                                    <button type="submit" style="background: #f72585; color: white; border: none; padding: 15px 30px; border-radius: 6px; font-size: 1.1rem; font-weight: 600; width: 100%; cursor: pointer;">Send Message</button>
                                </form>
                            </div>
                        </div>
                    </section>
                ''',
                'css_content': '''
                    input:focus, textarea:focus { 
                        border-color: #4361ee !important; 
                        outline: none; 
                    }
                '''
            }
        ]

        for comp_data in hero_components:
            component, created = Component.objects.get_or_create(
                name=comp_data['name'],
                category=comp_data['category'],
                defaults=comp_data
            )
            if created:
                self.stdout.write(f'Created component: {component.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample drag and drop components!')
        )

 