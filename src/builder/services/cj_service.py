








# services/cj_service.py
# services/cj_service.py - UPDATED WITH PROPER AUTHENTICATION
import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from builder.models import CJProduct

logger = logging.getLogger(__name__)


class CJServiceException(Exception):
    """Base exception for CJ service errors"""
    pass


class CJAuthenticationException(CJServiceException):
    """Authentication failed"""
    pass


# builder/cj_service.py
import requests
from django.utils import timezone
from datetime import timedelta
                
class CJOrderRequest:
    """Order request data model"""
    def __init__(self, **kwargs):
        self.order_no = kwargs.get('order_no')
        self.shipping_country_code = kwargs.get('shipping_country_code')
        self.product_list = kwargs.get('product_list', [])
        self.buyer_info = kwargs.get('buyer_info', {})
        self.warehouse = kwargs.get('warehouse', 'CN')
        self.shipping_method = kwargs.get('shipping_method')
        self.currency = kwargs.get('currency', 'USD')


import requests
import logging
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

logger = logging.getLogger(__name__)


import requests
import logging

logger = logging.getLogger(__name__)

class CJService:
    BASE_URL = "https://developers.cjdropshipping.com/api2.0/v1"

    def __init__(self, token):
        self.headers = {
            "CJ-Access-Token": token,
            "Content-Type": "application/json"
        }

    def get_warehouses(self):
        """Fetches all available CJ global warehouses."""
        url = f"{self.BASE_URL}/product/stock/getWarehouseList"
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            data = response.json()
            return data.get('data', []) if data.get('code') == 200 else []
        except Exception as e:
            logger.error(f"Error fetching warehouses: {e}")
            return []

    # def get_stock_details(self, pid):
    #     """Fetches stock breakdown across all warehouses for a specific PID."""
    #     url = f"{self.BASE_URL}/product/variant/queryByPid"
    #     try:
    #         response = requests.get(url, headers=self.headers, params={"pid": pid}, timeout=20)
    #         data = response.json()

    #         print(f"Stock data is {data}")
    #         # Returns list of {areaId, areaEn, stockNum}
    #         return data.get('data', []) if data.get('code') == 200 else []
    #     except Exception as e:
    #         logger.error(f"Error fetching stock details for {pid}: {e}")
    #         return []
    def get_stock_by_vid(self, vid):
        """Fetches warehouse-specific stock for a single Variant ID."""
        url = f"{self.BASE_URL}/product/stock/queryByVid"
        try:
            # Note: 'vid' is a required parameter for this specific endpoint
            response = requests.get(url, headers=self.headers, params={"vid": vid}, timeout=20)
            data = response.json()
            print(f"Stock data in service is: {data}")
            
            if data.get('code') == 200:
                # Returns a list of warehouse objects: 
                # [{"areaId": "0", "areaEn": "China Warehouse", "stockNum": 150}, ...]
                return data.get('data', []) 
            else:
                print(f"CJ API Error: {data.get('message')}")
                return []
        except Exception as e:
            print(f"Request failed for vid {vid}: {e}")
            return []
       
    def get_product_details(self, pid):
            url = f"{self.BASE_URL}/product/query"
            res = requests.get(url, headers=self.headers, params={"pid": pid})
            data = res.json()
            if data.get("code") == 200:
                prod = data.get("data", {})
                # Ensure images are clean
                if not prod.get('productImage') and prod.get('productImageList'):
                    prod['productImage'] = prod['productImageList'][0]
                return prod
            return None
    
    def get_variants(self, pid):
        """Fetches all color/size variants for a product."""
        url = f"{self.BASE_URL}/product/variant/queryByPid"
        res = requests.get(url, headers=self.headers, params={"pid": pid})
        return res.json().get('data', []) if res.json().get('code') == 200 else []
    
    def get_product_reviews(self, pid):
        """Fetches real customer reviews from CJ."""
        url = f"{self.BASE_URL}/product/comment/list"
        params = {"pid": pid, "pageNumber": 1, "pageSize": 20}
        try:
            res = requests.get(url, headers=self.headers, params=params, )
            data = res.json()
            if data.get("code") == 200:
                return data.get("data", {}).get("list", [])
            return []
        except Exception:
            return []
  
    # builder/services/cj_service.py

#         # http://localhost:8000/builder/cj-search/lux1/?q=phone




import requests
import time

class CJManager:
    def __init__(self, token):
        self.base_url = "https://developers.cjdropshipping.com"
        self.headers = {
            "CJ-Access-Token": token,
            "platformToken": token,
            "Content-Type": "application/json"
        }

    def get_logistic_name(self, vid, country_code, zip_code, city, province):
        """
        FUNCTION 1: Replicates test_logistics.
        Finds the exact shipping string needed for the order.
        """
        url = f"{self.base_url}/api2.0/v1/logistic/freightCalculate"
        print(f"url is {url}")
        payload = {
            "startCountryCode": "CN", # Use "US" if product is in US warehouse
            "endCountryCode": country_code,
            "zip": zip_code,
            "province": province,
            "city": "Los Angeles",
            "products": [{"vid": vid, "quantity": 1}]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=20)
            data = response.json()
            print(f"Logistic data is {data}")
            if data.get('code') == 200 and data.get('data'):
                methods = data['data'][0].get('logisticName')
                print(f"Logistic name is {methods}")
                # Extracts the specific method name (e.g., 'FedEx-432')
                return data['data'][0].get('logisticName')
        except Exception as e:
            print(f"Logistics API Error: {e}")
        return None

    def create_cj_order(self, order_data, logistic_name):
        """
        FUNCTION 2: Replicates test_order_creation.
        Sends the final payload to CJ using the logistic_name found in Step 1.
        """
        url = f"{self.base_url}/api2.0/v1/shopping/order/createOrderV2"

        print(f"Order data is {order_data}")
        
        payload = {
            "orderNumber": f"{order_data['number']}-{int(time.time())}",
            "shippingZip": str(order_data['zip']),
            "shippingCountryCode": str(order_data['country_code']),
            "shippingCountry": str(order_data['country_name']), # Verified requirement from test
            "countryCode": str(order_data['country_code']),
            "shippingProvince": str(order_data['province']),
            "shippingCity": str(order_data['city']),
            "shippingAddress": str(order_data['address']),
            "shippingCustomerName": str(order_data['name']),
            "shippingPhone": str(order_data['phone']),
            "logisticName": logistic_name,
            "payType": 3,
            "fromCountryCode": "CN",
            "products": [{"vid": order_data['vid'], "quantity": 1}]
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        print(f"Order response is {response}")
        return response.json()

    # def fulfill_cj_order(self, order):
    #     """
    #     THE WRAPPER: Coordinates Function 1 and Function 2.
    #     Call this function from your views.py.
    #     """

    #     print(f"CJ Order {order.country_iso}")
        
    #     for item in order.items.all():
    #         vid=item.vid
    #         # 1. Run the logistics function
    #         logistic_name = self.get_logistic_name(
    #             vid=vid,
    #             country_code=order.country_iso,
    #             zip_code=order.delivery_zip,
    #             city=order.delivery_city,
    #             province=order.delivery_state
    #         )

    #         # Fallback if lookup returns nothing
    #         if not logistic_name:
    #             logistic_name = "CJPacket Sensitive"

    #         # 2. Package data for the order function
    #         order_info = {
    #             "number": order.order_number,
    #             "zip": order.delivery_zip,
    #             "country_code": order.country_iso,
    #             "country_name": order.customer_country,
    #             "province": order.delivery_state,
    #             "city": order.delivery_city,
    #             "address": order.delivery_address,
    #             "name": order.customer_name,
    #             "phone": order.phone,
    #             "vid": vid
    #         }

    #         # print(f"Order info is {order_info}")
        
    #         # print(f"Logistic name is {logistic_name}")
    #         # 3. Run the order creation function
    #         result = self.create_cj_order(order_info, logistic_name)
    #         print(f"result is {result}")
    #         # 4. Handle DB updates
    #         if result.get('code') == 200:
    #             order.cj_order_id = result['data'].get('orderId')
    #             order.status = 'FULFILLED'
    #             order.save()
    #             print(f"order status is {order.status}")

                
        
    #     return True
    


    def fulfill_cj_order_corrected(self, order):
        """
        CORRECTED: Creates a single CJ order with all items
        """
        print(f"Processing CJ Order {order.order_number}")
        
        # 1. Collect all product data
        products_data = []
        
        for item in order.items.all():
            if item.vid:
                product_item = {
                    "vid": item.vid,
                    "quantity": item.quantity
                }
                products_data.append(product_item)
        
        if not products_data:
            print("No valid VIDs found in order items")
            return False
        
        # 2. Get logistics for FIRST product
        first_vid = products_data[0]['vid']
        logistic_name = self.get_logistic_name(
            vid=first_vid,
            country_code=order.country_iso,
            zip_code=order.delivery_zip,
            city=order.delivery_city,
            province=order.delivery_state
        )
        
        if not logistic_name:
            logistic_name = "CJPacket Sensitive"
        
        # 3. Prepare order data
        order_info = {
            "number": order.order_number,
            "zip": order.delivery_zip,
            "country_code": order.country_iso,
            "country_name": order.customer_country,
            "province": order.delivery_state,
            "city": order.delivery_city,
            "address": order.delivery_address,
            "name": order.customer_name,
            "phone": order.phone,
        }
        
        # 4. Create CJ order
        result = self.create_cj_order_multiple(order_info, logistic_name, products_data)
        print(f"CJ Order Creation Result: {result}")
        
        # 5. Handle response
        if result.get('code') == 200:
            cj_order_id = result['data'].get('orderId')
            
            # Save CJ order ID to the order
            order.cj_order_id = cj_order_id
            order.cj_fulfilled_at = timezone.now()
            order.status = 'fulfilled'  # Or 'processing'
            order.save()
            
            # Also update individual items if needed
            for item in order.items.all():
                item.cj_fulfilled = True  # Add this field to OrderItem if needed
                item.save()
            
            print(f"✅ Order {order.order_number} fulfilled with CJ ID: {cj_order_id}")
            return True
        else:
            error_msg = result.get('message', 'Unknown error')
            print(f"❌ Failed to create CJ order: {error_msg}")
            return False
    
    def create_cj_order_multiple(self, order_data, logistic_name, products_data):
        """
        Create CJ order with multiple products
        """
        url = f"{self.base_url}/api2.0/v1/shopping/order/createOrderV2"
        
        payload = {
            "orderNumber": f"{order_data['number']}-{int(time.time())}",
            "shippingZip": order_data['zip'],
            "shippingCountryCode": order_data['country_code'],
            "shippingCountry": order_data['country_name'],
            "countryCode": order_data['country_code'],
            "shippingProvince": order_data['province'],
            "shippingCity": order_data['city'],
            "shippingAddress": order_data['address'],
            "shippingCustomerName": order_data['name'],
            "shippingPhone": order_data['phone'],
            "logisticName": logistic_name,
            "payType": 3,
            "fromCountryCode": "CN",
            "products": products_data
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error creating CJ order: {e}")
            return {"code": 500, "message": str(e)}
    def get_variant_details(self, vid):
        """Fetches the variant details (including variantKey) from CJ."""
        url = f"{self.base_url}/api2.0/v1/product/variant/queryByVid"
        params = {"vid": vid}

        print("==============================================================")
        print("==============================================================")
        print(f"Got to func one {url}")
        print("==============================================================")
        print("==============================================================")
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=20)
            data = response.json()
            print("==============================================================")
            print("==============================================================")
            print(f"New variant data is {data}")
            print("==============================================================")
            print("==============================================================")

            if data.get('code') == 200:
                return data.get('data')
        except Exception as e:
            print(f"CJ API Error (queryByVid): {e}")
        return None

    # --- NEW METHOD: PROCESS & SAVE DATA ---
    def sync_product_color_size(self, product_obj):
        """
        Takes a Django Product object, calls CJ for its variant details,
        extracts color/size from the variantKey, and saves the model.
        """
        # Endpoint to get details for ONE specific variant
        url = f"{self.base_url}/api2.0/v1/product/variant/queryByVid"
        params = {"vid": product_obj.cj_vid}
        print("==============================================================")
        print("==============================================================")
        print(f"Got to func two {url}")
        print("==============================================================")
        print("==============================================================")
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=20)
            res_json = response.json()
            print("==============================================================")
            print("==============================================================")
            print(f"Json Got to func two Json {res_json}")
            print("==============================================================")
            print("==============================================================")
            
            if res_json.get('code') == 200 and res_json.get('data'):
                variant_data = res_json['data']
                print("==============================================================")
                print("==============================================================")
                print(f"VD Got to func two Vriant data {variant_data}")
                print("==============================================================")
                print("==============================================================")
                # variantKey looks like "Color:Black-Size:M"
                variant_key = variant_data.get('variantKey', '')
                print('variant key is: ',variant_key)
                
                if variant_key:
                    # Logic to split the string into actual values
                    print("Inside key")
                    parts = variant_key.split('-')
                    print(f'parts: {parts}')
                    for part in parts:
                        if ':' in part:
                            print("hiphen function")
                            attr_name, attr_val = part.split(':', 1)
                            clean_name = attr_name.strip().lower()
                            print(f'Clean name is {clean_name}')
                            clean_val = attr_val.strip()
                            print(f'Clean value is {clean_val}')
                            
                            if clean_name == 'color':
                                product_obj.colors = clean_val
                            elif clean_name == 'size':
                                product_obj.sizes = clean_val

                        elif ',' in part:
                            print("Coma function")
                            attr_name, attr_val = part.split(',', 1)
                            clean_name = attr_name.strip().lower()
                            print(f'Clean name is {clean_name}')
                            clean_val = attr_val.strip()
                            print(f'Clean value is {clean_val}')
                            
                            if clean_name == 'color':
                                product_obj.colors = clean_val
                            elif clean_name == 'size':
                                product_obj.sizes = clean_val

                        
                    
                    # Update other potential missing data like price while we're at it
                    if not product_obj.price:
                        product_obj.price = variant_data.get('variantPrice')
                        
                    product_obj.save()
                    return True
        except Exception as e:
            print(f"Error syncing attributes for VID {product_obj.cj_vid}: {e}")
        
        return False
# def fulfill_cj_order(order):
#     """
#     Identifies CJ products in an order and sends them to CJ for fulfillment using real data.
#     """
#     from builder.models import CJSettings, Product
#     import requests
#     import logging

#     logger = logging.getLogger(__name__)

#     # 1. Setup Service and Token
#     account = CJSettings.objects.first()
#     if not account or not account.access_token:
#         logger.error("CJ Access Token missing from CJSettings.")
#         return
    
#     # The value for platformToken is exactly the same as your access_token
#     headers = {
#         "CJ-Access-Token": account.access_token,
#         "platformToken": account.access_token,  # <--- ADD THIS
#         "Content-Type": "application/json"
#     }
    
#     cj_items = []
    
#     # 2. Map items to CJ VIDs
#     for item in order.items.all():
#         try:
#             product_obj = Product.objects.get(id=item.product_id)
#             if product_obj.cj_pid:
#                 # Ensure the vid is the actual CJ Variant ID, not a string like 'Color:None'
#                 cj_items.append({
#                     "vid": product_obj.cj_vid, 
#                     "quantity": item.quantity,
#                     "shippingName": item.product_title[:100] # CJ limits title length
#                 })
#         except (Product.DoesNotExist, ValueError):
#             continue

#     if not cj_items:
#         return 

#     # 3. Build Payload with Real Data & Fallbacks
#     # CJ API is strict: City, Province, and Phone cannot be empty strings.
#     url = "https://developers.cjdropshipping.com/api2.0/v1/shopping/order/createOrder"
    
# #     payload = {
# #     "orderNumber": str(order.order_number),
# #     "shippingZip": str(order.delivery_zip or "12345"),
# #     "shippingCountryCode": "US", # Original field
# #     "countryCode": "US",         # ADD THIS: Satisfies V2 validator
# #     "shippingProvince": str(order.delivery_state or "CA"),
# #     "shippingCity": str(order.delivery_city or "City"),
# #     "shippingAddress": str(order.delivery_address or "Address"),
# #     "shippingCustomerName": str(order.customer_name or "Customer"),
# #     "shippingPhone": str(order.customer_phone or "0000000000"),
# #     "remark": f"Order from {order.page.subdomain}",
# #     "payType": 3,
# #     "products": cj_items # Ensure cj_items uses the REAL Hex VIDs!
# # }
#     # Call the freight calculator first
#     cj_service = CJService(token=account.access_token)
#     best_logistic = cj_service.get_best_logistic(item.product_variant, "US")
#     print(f"Best logistic selected: {best_logistic}")
#     payload = {
#         "orderNumber": "ORD-F49E69F6",

#         "platform": "api",               # 🔥 REQUIRED

#         "shippingCountryCode": "US",
#         "shippingCountry": "United States",
#         "shippingProvince": "California",
#         "shippingCity": "Los Angeles",
#         "shippingAddress": "12345 Street",
#         "shippingZip": "12345",
#         "shippingCustomerName": "Mfecho Jerase",
#         "shippingPhone": "0000000000",

#         "remark": "Order from lux1",
#         "payType": 3,
#         "fromCountryCode": "CN",

#         "logisticName": best_logistic,
#         "shopLogisticsType": 1,

#         "products": [
#             {
#                 "vid": "1992892143659040770",
#                 "quantity": 1
#             }
#         ]
#     }
#     print(payload["shippingAddress"])
#     # 4. Execute Request
#     try:
#         response = requests.post(url, headers=headers, json=payload, timeout=15)
#         res_data = response.json()

#         if res_data.get('code') == 200:
#             # Successfully imported to CJ
#             cj_order_id = res_data.get('data', {}).get('orderId')
#             order.cj_order_id = cj_order_id
#             order.status = 'processing' # Or your internal status
#             order.save()
#             print(f"✅ Success: Order {order.order_number} pushed to CJ. CJ ID: {cj_order_id}")
#         else:
#             print(f"❌ CJ API Error: {res_data.get('message')}")
#             # Log the payload for debugging if it still fails
#             print(f"Debug Payload: {payload}")
            
#     except Exception as e:
#         logger.error(f"Fulfillment Connection Failed: {str(e)}")


# #         # http://localhost:8000/builder/cj-search/lux1/?q=phone