from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

from builder import models
from builder.models import PublishedPage, CJSettings, CJProduct, CJSyncLog
from builder.services.cj_service import CJService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sync CJ product prices and inventory for all active stores'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--store',
            type=str,
            help='Sync only for specific store (subdomain)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if not due'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of products to sync per store'
        )
    
    def handle(self, *args, **options):
        stores_to_sync = self.get_stores_to_sync(options)
        
        if not stores_to_sync:
            self.stdout.write(self.style.WARNING('No stores need syncing'))
            return
        
        self.stdout.write(f"Syncing {len(stores_to_sync)} stores...")
        
        for store in stores_to_sync:
            self.sync_store_products(store, options)
    
    def get_stores_to_sync(self, options):
        """Get stores that need product syncing"""
        query = PublishedPage.objects.filter(
            cj_settings__is_active=True
        ).select_related('cj_settings')
        
        if options['store']:
            query = query.filter(subdomain=options['store'])
        
        stores = []
        for store in query:
            settings = store.cj_settings
            
            # Check if we should sync this store
            if not settings.auto_sync_prices and not settings.auto_sync_inventory:
                continue
            
            # Check API limits
            if settings.daily_api_calls >= settings.max_daily_calls:
                self.stdout.write(
                    self.style.WARNING(f"Skipping {store.subdomain}: API limit reached")
                )
                continue
            
            stores.append(store)
        
        return stores
    
    def sync_store_products(self, store, options):
        """Sync products for a specific store"""
        self.stdout.write(f"Syncing products for {store.brand_name} ({store.subdomain})...")
        
        settings = store.cj_settings
        cj_service = CJService(settings.api_key, store)
        
        # Get products that need syncing
        products_query = CJProduct.objects.filter(
            page=store,
            sync_status__in=['synced', 'out_of_sync']
        )
        
        if not options['force']:
            # Filter by sync intervals
            now = timezone.now()
            
            if settings.auto_sync_prices:
                price_threshold = now - timedelta(hours=settings.price_sync_interval)
                products_query = products_query.filter(
                    models.Q(last_price_sync__isnull=True) |
                    models.Q(last_price_sync__lt=price_threshold)
                )
            
            if settings.auto_sync_inventory:
                inventory_threshold = now - timedelta(hours=settings.inventory_sync_interval)
                products_query = products_query.filter(
                    models.Q(last_inventory_sync__isnull=True) |
                    models.Q(last_inventory_sync__lt=inventory_threshold)
                )
        
        # Limit number of products
        products = products_query[:options['limit']]
        
        if not products:
            self.stdout.write(f"  No products need syncing")
            return
        
        # Create sync log
        sync_log = CJSyncLog.objects.create(
            page=store,
            sync_type='price_sync' if settings.auto_sync_prices else 'inventory_sync',
            status='started',
            request_data={
                'product_count': len(products),
                'force': options['force']
            }
        )
        
        successful = 0
        failed = 0
        
        for cj_product in products:
            try:
                # Get latest product data
                result = cj_service.get_product_detail(cj_product.cj_product_id, include_variants=False)
                
                if not result['success']:
                    failed += 1
                    cj_product.sync_status = 'failed'
                    cj_product.last_sync_error = result.get('error', 'Sync failed')
                    cj_product.retry_count += 1
                    cj_product.save()
                    continue
                
                product_data = result['product']
                cj_price = product_data['pricing']['price']
                stock = product_data['inventory']['stock']
                
                # Update product data
                update_fields = []
                
                if settings.auto_sync_prices and cj_price != cj_product.cj_price_usd:
                    # Price changed - update selling price
                    selling_price = cj_product.calculate_selling_price()
                    
                    if selling_price and cj_product.local_product:
                        cj_product.local_product.price = selling_price
                        cj_product.local_product.save()
                    
                    cj_product.cj_price_usd = cj_price
                    cj_product.last_price_sync = timezone.now()
                    update_fields.extend(['cj_price_usd', 'last_price_sync'])
                
                if settings.auto_sync_inventory and stock != cj_product.cj_stock_quantity:
                    cj_product.cj_stock_quantity = stock
                    cj_product.local_stock_quantity = stock
                    cj_product.last_inventory_sync = timezone.now()
                    update_fields.extend(['cj_stock_quantity', 'local_stock_quantity', 'last_inventory_sync'])
                
                # Update other fields
                cj_product.cj_data = product_data
                cj_product.last_full_sync = timezone.now()
                cj_product.sync_status = 'synced'
                cj_product.last_sync_error = ''
                cj_product.retry_count = 0
                
                update_fields.extend(['cj_data', 'last_full_sync', 'sync_status', 'last_sync_error', 'retry_count'])
                
                cj_product.save(update_fields=update_fields)
                successful += 1
                
            except Exception as e:
                failed += 1
                cj_product.sync_status = 'failed'
                cj_product.last_sync_error = str(e)
                cj_product.retry_count += 1
                cj_product.save()
                logger.error(f"Error syncing product {cj_product.cj_product_id}: {str(e)}")
        
        # Update sync log
        sync_log.status = 'success' if successful > 0 else 'failed'
        sync_log.items_processed = len(products)
        sync_log.items_succeeded = successful
        sync_log.items_failed = failed
        sync_log.api_calls_made = len(products)
        sync_log.completed_at = timezone.now()
        sync_log.save()
        
        # Update API call count
        settings.daily_api_calls += len(products)
        settings.save(update_fields=['daily_api_calls'])
        
        self.stdout.write(
            self.style.SUCCESS(f"  Completed: {successful} successful, {failed} failed")
        )
