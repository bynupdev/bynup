#payments/services/paypal_service

import requests
import json
from django.core.exceptions import ValidationError
from django.urls import reverse
from ..models import Order, Transaction
import uuid
import base64

class PayPalService:
    def __init__(self, gateway):
        self.gateway = gateway
        self.client_id = gateway.get_paypal_client_id()
        self.client_secret = gateway.get_paypal_client_secret()
        self.is_test_mode = gateway.is_test_mode
        self.access_token = None
        self.base_url = self.get_base_url()
        self.authenticate()
    
    def get_base_url(self):
        """Get PayPal API base URL based on mode"""
        if self.is_test_mode:
            return "https://api-m.sandbox.paypal.com"
        return "https://api-m.paypal.com"
    
    def authenticate(self):
        """Authenticate with PayPal and get access token"""
        try:
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            base64_auth = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {base64_auth}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            data = 'grant_type=client_credentials'
            
            response = requests.post(
                f'{self.base_url}/v1/oauth2/token',
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
            else:
                raise ValidationError(f"PayPal authentication failed: {response.text}")
                
        except Exception as e:
            raise ValidationError(f"PayPal authentication error: {str(e)}")
    
    def create_order(self, order_data, customer_info, request):
        """Create PayPal order"""
        try:
            # Get order amount and details
            if order_data.get('checkout_type') == 'instant':
                amount = order_data.get('product', {}).get('price', 0)
                items = [{
                    'name': order_data.get('product', {}).get('title', 'Product'),
                    'description': order_data.get('product', {}).get('description', ''),
                    'quantity': 1,
                    'unit_amount': {
                        'currency_code': 'USD',
                        'value': str(amount)
                    }
                }]
            else:  # cart checkout
                amount = order_data.get('cart', {}).get('total_amount', 0)
                items = []
                for item in order_data.get('cart', {}).get('items', []):
                    items.append({
                        'name': item.get('title', 'Product'),
                        'description': item.get('description', ''),
                        'quantity': str(item.get('quantity', 1)),
                        'unit_amount': {
                            'currency_code': 'USD',
                            'value': str(item.get('price', 0))
                        }
                    })
            
            # Create PayPal order payload
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": str(amount),
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value": str(amount)
                                }
                            }
                        },
                        "items": items
                    }
                ],
                "application_context": {
                    "brand_name": self.gateway.page.brand_name,
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW",
                    "return_url": request.build_absolute_uri(
                        reverse('payments:paypal_success', args=[self.gateway.page.subdomain])
                    ),
                    "cancel_url": request.build_absolute_uri(
                        reverse('payments:paypal_cancel', args=[self.gateway.page.subdomain])
                    ),
                    "shipping_preference": "NO_SHIPPING"
                }
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}',
                'PayPal-Request-Id': f'order_{uuid.uuid4().hex[:8]}'
            }
            
            response = requests.post(
                f'{self.base_url}/v2/checkout/orders',
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 201:
                order_response = response.json()
                
                # Find approval URL
                approval_url = None
                for link in order_response.get('links', []):
                    if link.get('rel') == 'approve':
                        approval_url = link.get('href')
                        break
                
                return {
                    'order_id': order_response['id'],
                    'approval_url': approval_url,
                    'status': order_response['status'],
                    'gateway': 'paypal'
                }
            else:
                raise ValidationError(f"PayPal order creation failed: {response.text}")
                
        except Exception as e:
            raise ValidationError(f"PayPal order creation error: {str(e)}")
    
    def capture_order(self, order_id):
        """Capture PayPal payment"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.post(
                f'{self.base_url}/v2/checkout/orders/{order_id}/capture',
                headers=headers
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                raise ValidationError(f"PayPal capture failed: {response.text}")
                
        except Exception as e:
            raise ValidationError(f"PayPal capture error: {str(e)}")
    
    def get_order_details(self, order_id):
        """Get PayPal order details"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(
                f'{self.base_url}/v2/checkout/orders/{order_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise ValidationError(f"PayPal order details failed: {response.text}")
                
        except Exception as e:
            raise ValidationError(f"PayPal order details error: {str(e)}")


    def refund_payment(self, capture_id, amount):
        """Refund a PayPal payment"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}',
                'PayPal-Request-Id': f'refund_{uuid.uuid4().hex[:8]}'
            }
            
            payload = {
                "amount": {
                    "value": str(amount),
                    "currency_code": "USD"
                }
            }
            
            response = requests.post(
                f'{self.base_url}/v2/payments/captures/{capture_id}/refund',
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code in [201, 200]:
                return {
                    'success': True,
                    'refund_id': response.json().get('id'),
                    'status': response.json().get('status'),
                    'amount': amount,
                }
            else:
                raise ValidationError(f"PayPal refund failed: {response.text}")
                
        except Exception as e:
            raise ValidationError(f"PayPal refund error: {str(e)}")