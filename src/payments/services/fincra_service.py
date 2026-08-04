# payments/services/fincra_service.py
import requests
import json
import hmac
import hashlib
from django.core.exceptions import ValidationError
from django.urls import reverse
import uuid
import time

class FincraService:
    def __init__(self, gateway):
        self.gateway = gateway
        self.api_key = gateway.get_fincra_api_key()
        self.secret_key = gateway.get_fincra_secret_key()
        self.business_id = gateway.get_fincra_business_id()
        self.is_test_mode = gateway.is_test_mode
        
        if not self.api_key or not self.secret_key or not self.business_id:
            raise ValidationError("Fincra credentials not fully configured")
        
        # Set base URLs based on mode
        if self.is_test_mode:
            self.base_url = "https://sandboxapi.fincra.com"
        else:
            self.base_url = "https://api.fincra.com"
        
        # Headers for API calls
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_headers(self):
        """Get headers with optional signature for sensitive endpoints"""
        return self.headers
    
    def create_payment_link(self, amount, currency, customer_data, description, metadata=None):
        """Create Fincra payment link"""
        try:
            # Generate reference
            reference = f"fin_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            payload = {
                'business': self.business_id,
                'amount': amount,
                'currency': currency,
                'customer': {
                    'name': customer_data.get('name', ''),
                    'email': customer_data.get('email', ''),
                    'phoneNumber': customer_data.get('phone', '')
                },
                'description': description,
                'redirectUrl': metadata.get('redirect_url', '') if metadata else '',
                'webhookUrl': metadata.get('webhook_url', '') if metadata else '',
                'reference': reference,
                'metadata': metadata or {}
            }
            
            # Add subaccount if specified
            subaccount_id = self.gateway.get_fincra_subaccount_id()
            if subaccount_id:
                payload['subAccount'] = subaccount_id
            
            response = requests.post(
                f"{self.base_url}/payment-links",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    'success': True,
                    'payment_link': data.get('data', {}).get('paymentLink'),
                    'reference': reference,
                    'data': data
                }
            else:
                error_data = response.json()
                raise ValidationError(f"Fincra payment link creation failed: {error_data}")
                
        except Exception as e:
            raise ValidationError(f"Fincra payment link creation error: {str(e)}")
    
    def create_collection_account(self, currency, country_code, customer_email):
        """Create virtual account for bank transfers"""
        try:
            payload = {
                'business': self.business_id,
                'currency': currency,
                'country': country_code,  # e.g., 'NG' for Nigeria
                'customer': {
                    'email': customer_email
                },
                'accountType': 'collection'  # 'collection' or 'payout'
            }
            
            response = requests.post(
                f"{self.base_url}/virtual-accounts/generate",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    'success': True,
                    'account_number': data.get('data', {}).get('accountNumber'),
                    'bank_name': data.get('data', {}).get('bank', {}).get('name'),
                    'account_name': data.get('data', {}).get('accountName'),
                    'reference': data.get('data', {}).get('reference'),
                    'data': data
                }
            else:
                error_data = response.json()
                raise ValidationError(f"Fincra virtual account creation failed: {error_data}")
                
        except Exception as e:
            raise ValidationError(f"Fincra virtual account creation error: {str(e)}")
    
    def initiate_card_payment(self, amount, currency, card_details, customer_data, metadata=None):
        """Initiate card payment"""
        try:
            reference = f"card_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            payload = {
                'business': self.business_id,
                'amount': amount,
                'currency': currency,
                'customer': {
                    'name': customer_data.get('name', ''),
                    'email': customer_data.get('email', ''),
                    'phoneNumber': customer_data.get('phone', '')
                },
                'card': {
                    'number': card_details.get('number'),
                    'expiryMonth': card_details.get('expiry_month'),
                    'expiryYear': card_details.get('expiry_year'),
                    'cvv': card_details.get('cvv'),
                    'pin': card_details.get('pin', '')
                },
                'reference': reference,
                'redirectUrl': metadata.get('redirect_url', '') if metadata else '',
                'metadata': metadata or {}
            }
            
            response = requests.post(
                f"{self.base_url}/charges/card",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'reference': reference,
                    'auth_url': data.get('data', {}).get('authUrl'),
                    'requires_3ds': data.get('data', {}).get('requires3DS', False),
                    'data': data
                }
            else:
                error_data = response.json()
                raise ValidationError(f"Fincra card payment failed: {error_data}")
                
        except Exception as e:
            raise ValidationError(f"Fincra card payment error: {str(e)}")
    
    def verify_payment(self, reference):
        """Verify payment status"""
        try:
            response = requests.get(
                f"{self.base_url}/transactions/query?reference={reference}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                transaction = data.get('data', {})
                
                return {
                    'success': True,
                    'reference': transaction.get('reference'),
                    'status': transaction.get('status'),  # 'successful', 'pending', 'failed'
                    'amount': transaction.get('amount'),
                    'currency': transaction.get('currency'),
                    'payment_method': transaction.get('paymentMethod'),
                    'customer_email': transaction.get('customer', {}).get('email'),
                    'data': data
                }
            else:
                error_data = response.json()
                raise ValidationError(f"Fincra payment verification failed: {error_data}")
                
        except Exception as e:
            raise ValidationError(f"Fincra payment verification error: {str(e)}")
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature"""
        try:
            # Fincra uses HMAC-SHA256 with secret key
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            raise ValidationError(f"Webhook signature verification failed: {str(e)}")
    
    def create_checkout_data(self, order_data, customer_info, request):
        """Create checkout data for Fincra"""
        try:
            # Calculate amount
            if order_data.get('checkout_type') == 'instant':
                amount = order_data.get('product', {}).get('price', 0)
                description = order_data.get('product', {}).get('title', 'Product')
            else:
                amount = order_data.get('cart', {}).get('total_amount', 0)
                description = f"Order with {len(order_data.get('cart', {}).get('items', []))} items"
            
            # Create metadata
            metadata = {
                'order_data': order_data,
                'customer_info': customer_info,
                'page_id': str(self.gateway.page.id),
                'redirect_url': request.build_absolute_uri(
                    reverse('payments:fincra_callback', args=[self.gateway.page.subdomain])
                ),
                'webhook_url': request.build_absolute_uri(
                    reverse('payments:fincra_webhook', args=[self.gateway.page.subdomain])
                )
            }
            
            # Create payment link
            result = self.create_payment_link(
                amount=amount,
                currency='NGN',  # Fincra primarily uses NGN, but supports others
                customer_data={
                    'name': customer_info.get('name', ''),
                    'email': customer_info.get('email', ''),
                    'phone': customer_info.get('phone', '')
                },
                description=description,
                metadata=metadata
            )
            
            if result['success']:
                return {
                    'payment_link': result['payment_link'],
                    'reference': result['reference'],
                    'amount': amount,
                    'currency': 'NGN',
                    'description': description,
                    'metadata': metadata
                }
            else:
                raise ValidationError("Failed to create Fincra payment link")
                
        except Exception as e:
            raise ValidationError(f"Fincra checkout creation failed: {str(e)}")