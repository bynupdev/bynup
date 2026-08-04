# payments/management/commands/check_expired_subscriptions.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import Subscription, Plan


class Command(BaseCommand):
    help = 'Check and expire subscriptions that have passed their end date'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find expired active subscriptions
        expired = Subscription.objects.filter(
            status='active',
            end_date__lt=now
        )
        
        # Also handle canceled subscriptions that have reached end date
        expired_canceled = Subscription.objects.filter(
            status='canceled',
            end_date__lt=now
        )
        
        free_plan = Plan.objects.filter(tier='free').first()
        
        for sub in expired:
            sub.status = 'expired'
            if free_plan:
                sub.plan = free_plan
            sub.save()
            self.stdout.write(f"Expired: {sub.user.email}")
        
        for sub in expired_canceled:
            sub.status = 'expired'
            if free_plan:
                sub.plan = free_plan
            sub.save()
            self.stdout.write(f"Expired (canceled): {sub.user.email}")
        
        total = expired.count() + expired_canceled.count()
        self.stdout.write(self.style.SUCCESS(f"Processed {total} expired subscriptions"))