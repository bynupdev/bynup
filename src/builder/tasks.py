from celery import shared_task
from django.conf import settings
from .models import Product, ProductVariant, ProductInventory
from builder.services.cj_service import CJService
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def sync_all_cj_stocks(self):
    service = CJService()
    products = Product.objects.filter(cj_pid__isnull=False, status='active')
    
    for product in products:
        try:
            # 1. Get current data from CJ
            product_data = service.get_product_details(product.cj_pid)
            if not product_data:
                continue

            variants = product_data.get('variants', [])
            product_total_qty = 0

            for v in variants:
                v_sku = v.get('variantSku')
                
                # 2. Get stock (using the most reliable field from your logs)
                raw_qty = int(v.get('inventoryNum', 0))
                
                # 3. Apply Safety Buffer
                # If CJ has 5, and buffer is 2, we record 3.
                final_qty = max(0, raw_qty - settings.STOCK_SAFETY_BUFFER)
                product_total_qty += final_qty

                # 4. Update Variant and Inventory
                ProductInventory.objects.filter(sku=v_sku).update(quantity=final_qty)

            # 5. Update parent Product
            product.quantity = product_total_qty
            if product_total_qty <= 0:
                product.status = 'out_of_stock'
            product.save()

        except Exception as exc:
            logger.error(f"Error syncing {product.cj_pid}: {exc}")
            # Optional: self.retry(exc=exc, countdown=60)