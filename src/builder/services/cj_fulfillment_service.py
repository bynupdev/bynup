import requests
import logging
from django.conf import settings
from builder.services.cj_service import CJService # Assuming your CJ service is here

logger = logging.getLogger(__name__)

def fulfill_cj_order(order):
    """
    Identifies CJ products in an order and sends them to CJ for fulfillment.
    """
    cj_service = CJService() # This should handle your API token logic
    cj_items = []

    # 1. Filter order items for CJ Products
    for item in order.items.all():
        # We assume CJ products have a 'cj_pid' or a specific SKU format
        # Replace 'product_id' or 'product_sku' logic with your specific field
        if item.product_sku and item.product_sku.startswith('CJ'): 
            cj_items.append({
                "vid": item.product_variant, # CJ uses 'vid' for variants
                "quantity": item.quantity,
                "shippingName": item.product_title
            })

    if not cj_items:
        logger.info(f"Order {order.order_number} contains no CJ products. Skipping.")
        return

    # 2. Prepare the CJ API Payload
    # API Docs: https://developers.cjdropshipping.com/
    url = f"{cj_service.BASE_URL}/shopping/order/confirmOrder"
    
    payload = {
        "orderNumber": order.order_number,
        "shippingZip": order.delivery_zip,
        "shippingCountryCode": order.delivery_country, # Must be ISO code like 'US'
        "shippingProvince": order.delivery_state,
        "shippingCity": order.delivery_city,
        "shippingAddress": order.delivery_address,
        "shippingCustomerName": order.customer_name,
        "shippingPhone": order.customer_phone,
        "remark": f"Auto-fulfilled order from {order.page.subdomain}",
        "products": cj_items
    }

    # 3. Post to CJ
    try:
        response = requests.post(
            url, 
            headers=cj_service.headers, 
            json=payload, 
            timeout=15
        )
        res_data = response.json()

        if res_data.get('code') == 200:
            logger.info(f"Successfully pushed Order {order.order_number} to CJ.")
            # Store CJ's internal order ID if needed
            order.cj_order_id = res_data.get('data', {}).get('orderId')
            order.save()
        else:
            logger.error(f"CJ API Error for Order {order.order_number}: {res_data.get('message')}")
            
    except Exception as e:
        logger.error(f"Failed to connect to CJ API: {str(e)}")