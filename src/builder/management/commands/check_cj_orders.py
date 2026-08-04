from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from builder.models import PublishedPage, CJOrder, CJSyncLog
from builder.services.cj_service import CJService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check status of pending CJ orders'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--store',
            type=str,
            help='Check only for specific store (subdomain)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Check orders updated in last N hours'
        )
    
    def handle(self, *args, **options):
        # Get orders to check
        time_threshold = timezone.now() - timedelta(hours=options['hours'])
        
        orders_query = CJOrder.objects.filter(
            status__in=['submitted', 'processing'],
            updated_at__gte=time_threshold
        ).select_related('page', 'page__cj_settings')
        
        if options['store']:
            orders_query = orders_query.filter(page__subdomain=options['store'])
        
        # Filter only stores with active CJ integration
        orders = []
        for order in orders_query:
            try:
                settings = order.page.cj_settings
                if settings.is_active and settings.daily_api_calls < settings.max_daily_calls:
                    orders.append(order)
            except:
                continue
        
        if not orders:
            self.stdout.write(self.style.WARNING('No orders to check'))
            return
        
        self.stdout.write(f"Checking {len(orders)} orders...")
        
        successful = 0
        failed = 0
        
        for order in orders:
            try:
                self.check_order_status(order)
                successful += 1
            except Exception as e:
                failed += 1
                logger.error(f"Error checking order {order.id}: {str(e)}")
        
        self.stdout.write(
            self.style.SUCCESS(f"Completed: {successful} successful, {failed} failed")
        )
    
    def check_order_status(self, order):
        """Check status of a single order"""
        settings = order.page.cj_settings
        
        if not order.cj_order_id:
            return
        
        # Create sync log
        sync_log = CJSyncLog.objects.create(
            page=order.page,
            sync_type='order_status_check',
            status='started',
            request_data={'order_id': order.cj_order_id}
        )
        
        try:
            cj_service = CJService(settings.api_key, order.page)
            result = cj_service.get_order_status(order.cj_order_id)
            
            if result['success']:
                order_data = result['order']
                
                old_status = order.status
                order.status = order_data['status']
                
                if order_data.get('tracking_number'):
                    order.tracking_number = order_data['tracking_number']
                    order.tracking_url = order_data.get('tracking_url', '')
                
                if order_data.get('estimated_delivery'):
                    order.estimated_delivery = order_data['estimated_delivery']
                
                if order_data['status'] == 'shipped' and not order.shipped_at:
                    order.shipped_at = timezone.now()
                elif order_data['status'] == 'delivered' and not order.delivered_at:
                    order.delivered_at = timezone.now()
                
                order.save()
                
                sync_log.status = 'success'
                sync_log.completed_at = timezone.now()
                sync_log.response_data = result
                sync_log.save()
                
                # Update API call count
                settings.daily_api_calls += 1
                settings.save(update_fields=['daily_api_calls'])
                
                self.stdout.write(f"  Order {order.order_number}: {old_status} → {order.status}")
            else:
                sync_log.status = 'failed'
                sync_log.error_message = result.get('error', 'Status check failed')
                sync_log.completed_at = timezone.now()
                sync_log.save()
                
                raise Exception(result.get('error'))
                
        except Exception as e:
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            raise