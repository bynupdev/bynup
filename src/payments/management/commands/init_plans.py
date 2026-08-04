# # payments/management/commands/init_plans.py

# from django.core.management.base import BaseCommand
# from payments.models import Plan


# class Command(BaseCommand):
#     help = 'Initialize subscription plans'

#     def handle(self, *args, **options):
#         self.stdout.write('Initializing subscription plans...')
        
#         plans = [
#             {
#                 'tier': 'free',
#                 'name': 'Starter',
#                 'description': 'Perfect for getting started',
#                 'price_monthly': 0,
#                 'price_yearly': 0,
#                 'max_websites': 1,
#                 'max_products': 10,
#                 'max_storage_mb': 100,
#                 'max_visitors': 1000,
#                 'max_form_submissions': 10,
#                 'max_emails': 0,
#                 'custom_domain': False,
#                 'remove_branding': False,
#                 'advanced_seo': False,
#                 'priority_support': False,
#                 'email_marketing': False,
#                 'abandoned_cart': False,
#                 'discount_codes': False,
#                 'white_label': False,
#                 'custom_templates': False,
#                 'display_order': 1,
#                 'badge': 'Free Forever',
#             },
#             {
#                 'tier': 'pro',
#                 'name': 'Pro',
#                 'description': 'For growing businesses',
#                 'price_monthly': 12,
#                 'price_yearly': 108,
#                 'max_websites': 3,
#                 'max_products': 500,
#                 'max_storage_mb': 1024,
#                 'max_visitors': 25000,
#                 'max_form_submissions': 500,
#                 'max_emails': 500,
#                 'custom_domain': True,
#                 'remove_branding': True,
#                 'advanced_seo': True,
#                 'priority_support': True,
#                 'email_marketing': True,
#                 'abandoned_cart': False,
#                 'discount_codes': False,
#                 'white_label': False,
#                 'custom_templates': False,
#                 'display_order': 2,
#                 'badge': 'Most Popular',
#             },
#             {
#                 'tier': 'business',
#                 'name': 'Business',
#                 'description': 'For established businesses',
#                 'price_monthly': 29,
#                 'price_yearly': 261,
#                 'max_websites': -1,
#                 'max_products': 5000,
#                 'max_storage_mb': 12288,
#                 'max_visitors': 100000,
#                 'max_form_submissions': 5000,
#                 'max_emails': 5000,
#                 'custom_domain': True,
#                 'remove_branding': True,
#                 'advanced_seo': True,
#                 'priority_support': True,
#                 'email_marketing': True,
#                 'abandoned_cart': True,
#                 'discount_codes': True,
#                 'white_label': False,
#                 'custom_templates': False,
#                 'display_order': 3,
#                 'badge': '',
#             },
#             {
#                 'tier': 'agency',
#                 'name': 'Agency',
#                 'description': 'For agencies and high-volume businesses',
#                 'price_monthly': 79,
#                 'price_yearly': 711,
#                 'max_websites': -1,
#                 'max_products': -1,
#                 'max_storage_mb': 102400,
#                 'max_visitors': -1,
#                 'max_form_submissions': -1,
#                 'max_emails': 50000,
#                 'custom_domain': True,
#                 'remove_branding': True,
#                 'advanced_seo': True,
#                 'priority_support': True,
#                 'email_marketing': True,
#                 'abandoned_cart': True,
#                 'discount_codes': True,
#                 'white_label': True,
#                 'custom_templates': True,
#                 'display_order': 4,
#                 'badge': 'Enterprise',
#             },
#         ]
        
#         for plan_data in plans:
#             plan, created = Plan.objects.update_or_create(
#                 tier=plan_data['tier'],
#                 defaults=plan_data
#             )
            
#             if created:
#                 self.stdout.write(self.style.SUCCESS(f'✓ Created plan: {plan.name}'))
#             else:
#                 self.stdout.write(self.style.WARNING(f'• Updated plan: {plan.name}'))
        
#         self.stdout.write(self.style.SUCCESS('\n✅ All plans initialized successfully!'))

# payments/management/commands/init_plans.py

from django.core.management.base import BaseCommand
from payments.models import Plan


class Command(BaseCommand):
    help = 'Initialize subscription plans'

    def handle(self, *args, **options):
        self.stdout.write('Updating subscription plans...')
        
        plans = [
            {
                'tier': 'free',
                'name': 'Starter',
                'description': 'Perfect for getting started',
                'price_monthly': 0,
                'price_yearly': 0,
                'max_websites': 1,
                'max_products': 10,
                'max_storage_mb': 100,
                'max_visitors': 1000,
                'max_form_submissions': 10,
                'max_emails': 0,
                'custom_domain': False,
                'remove_branding': False,
                'advanced_seo': False,
                'priority_support': False,
                'email_marketing': False,
                'abandoned_cart': False,
                'discount_codes': False,
                'white_label': False,
                'custom_templates': False,
                'display_order': 1,
                'badge': 'Free Forever',
            },
            {
                'tier': 'pro',
                'name': 'Pro',
                'description': 'For growing businesses',
                'price_monthly': 12,
                'price_yearly': 108,
                # ===== CHANGED VALUES =====
                'max_websites': 1,           # Changed from 3 to 1
                'max_products': 250,          # Changed from 500 to 250
                'max_storage_mb': 1024,       # 1GB (unchanged)
                'max_visitors': -1,        # Unchanged
                'max_form_submissions': 250,  # Changed from 500 to 250
                # ===== END CHANGES =====
                'max_emails': 500,
                'custom_domain': True,
                'remove_branding': True,
                'advanced_seo': True,
                'priority_support': True,
                'email_marketing': True,
                'abandoned_cart': False,
                'discount_codes': False,
                'white_label': False,
                'custom_templates': False,
                'display_order': 2,
                'badge': 'Most Popular',
            },
            {
                'tier': 'business',
                'name': 'Business',
                'description': 'For established businesses',
                'price_monthly': 29,
                'price_yearly': 261,
                # ===== CHANGED VALUES =====
                'max_websites': 3,            # Changed from unlimited (-1) to 3
                'max_products': 2000,         # Changed from 5000 to 2000
                'max_storage_mb': 10240,      # Changed from 12GB (12288) to 10GB (10240)
                'max_visitors': -1,       # Unchanged
                'max_form_submissions': 2500, # Changed from 5000 to 2500
                # ===== END CHANGES =====
                'max_emails': 2500,
                'custom_domain': True,
                'remove_branding': True,
                'advanced_seo': True,
                'priority_support': True,
                'email_marketing': True,
                'abandoned_cart': True,
                'discount_codes': True,
                'referral_links': True,
                'white_label': False,
                'custom_templates': False,
                'display_order': 3,
                'badge': '',
            },
            {
                'tier': 'agency',
                'name': 'Agency',
                'description': 'For agencies and high-volume businesses',
                'price_monthly': 79,
                'price_yearly': 711,
                # ===== UNCHANGED =====
                'max_websites': -1,           # Unlimited
                'max_products': -1,           # Unlimited
                'max_storage_mb': 102400,     # 100GB
                'max_visitors': -1,           # Unlimited
                'max_form_submissions': -1,   # Unlimited
                # ===== END UNCHANGED =====
                'max_emails': 50000,
                'custom_domain': True,
                'remove_branding': True,
                'advanced_seo': True,
                'priority_support': True,
                'email_marketing': True,
                'abandoned_cart': True,
                'discount_codes': True,
                'referral_links': True,
                'white_label': True,
                'custom_templates': True,
                'display_order': 4,
                'badge': 'Enterprise',
            },
        ]
        
        for plan_data in plans:
            plan, created = Plan.objects.update_or_create(
                tier=plan_data['tier'],
                defaults=plan_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created plan: {plan.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'• Updated plan: {plan.name}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ All plans updated successfully!'))