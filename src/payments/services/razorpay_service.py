# payments/services/razorpay_service.py
import razorpay
import json
import hmac
import hashlib
from django.core.exceptions import ValidationError
from django.urls import reverse
import uuid

class RazorpayService:
    def __init__(self, gateway):
        self.gateway = gateway
        self.key_id = gateway.get_razorpay_key_id()
        self.key_secret = gateway.get_razorpay_key_secret()
        self.is_test_mode = gateway.is_test_mode
        
        if not self.key_id or not self.key_secret:
            raise ValidationError("Razorpay credentials not configured")
        
        # Initialize Razorpay client
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
        
        # Set test mode
        if self.is_test_mode:
            # Razorpay uses same API for test and live, just different keys
            pass
    
    def create_order(self, amount, currency='INR', receipt=None, notes=None):
        """Create Razorpay order"""
        try:
            data = {
                'amount': int(amount * 100),  # Convert to paise
                'currency': currency,
                'payment_capture': 1,  # Auto-capture payment
                'receipt': receipt or f'receipt_{uuid.uuid4().hex[:8]}',
            }
            
            if notes:
                data['notes'] = notes
            
            order = self.client.order.create(data=data)
            return order
            
        except Exception as e:
            raise ValidationError(f"Razorpay order creation failed: {str(e)}")
    
    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify payment signature"""
        try:
            # Create signature verification string
            payload = f"{razorpay_order_id}|{razorpay_payment_id}"
            
            # Generate expected signature
            expected_signature = hmac.new(
                self.key_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, razorpay_signature)
            
        except Exception as e:
            raise ValidationError(f"Signature verification failed: {str(e)}")
    
    def fetch_payment(self, payment_id):
        """Fetch payment details"""
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as e:
            raise ValidationError(f"Failed to fetch payment: {str(e)}")
    
    def create_checkout_data(self, order_data, customer_info, request):
        """Create checkout data for frontend"""
        try:
            # Calculate amount
            if order_data.get('checkout_type') == 'instant':
                amount = order_data.get('product', {}).get('price', 0)
                description = order_data.get('product', {}).get('title', 'Product')
            else:
                amount = order_data.get('cart', {}).get('total_amount', 0)
                description = f"Order with {len(order_data.get('cart', {}).get('items', []))} items"
            
            # Create Razorpay order
            razorpay_order = self.create_order(
                amount=amount,
                currency='INR',
                receipt=f"order_{uuid.uuid4().hex[:8]}",
                notes={
                    'customer_name': customer_info.get('name', ''),
                    'customer_email': customer_info.get('email', ''),
                    'page_id': str(self.gateway.page.id)
                }
            )
            
            return {
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'key_id': self.key_id,
                'name': self.gateway.page.brand_name,
                'description': description,
                'prefill': {
                    'name': customer_info.get('name', ''),
                    'email': customer_info.get('email', ''),
                    'contact': customer_info.get('phone', '')
                },
                'theme': {
                    'color': '#4361ee'
                }
            }
            
        except Exception as e:
            raise ValidationError(f"Razorpay checkout creation failed: {str(e)}")
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature"""
        try:
            # Razorpay expects the raw request body
            self.client.utility.verify_webhook_signature(
                payload,
                signature,
                self.gateway.get_razorpay_webhook_secret()
            )
            return True
        except Exception as e:
            raise ValidationError(f"Webhook signature verification failed: {str(e)}")