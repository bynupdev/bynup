# payments/services/cryptomus_service.py
import requests
import json
import hashlib
import hmac
import uuid
from django.core.exceptions import ValidationError
from django.urls import reverse
import time

class CryptomusService:
    def __init__(self, gateway):
        self.gateway = gateway
        self.api_key = gateway.get_cryptomus_api_key()
        self.merchant_uuid = gateway.get_cryptomus_merchant_uuid()
        self.webhook_secret = gateway.get_cryptomus_webhook_secret()
        
        if not self.api_key or not self.merchant_uuid:
            raise ValidationError("Cryptomus credentials not fully configured")
        
        # Cryptomus uses same API for test and live
        self.base_url = "https://api.cryptomus.com/v1"
        
        # Supported currencies
        self.supported_currencies = {
            'USDT': ['TRC20', 'ERC20', 'BEP20'],
            'BTC': ['BTC'],
            'ETH': ['ETH'],
            'BNB': ['BEP20'],
            'LTC': ['LTC'],
            'DOGE': ['DOGE'],
            'SOL': ['SOL'],
            'TRX': ['TRC20'],
            'MATIC': ['POLYGON'],
            'XRP': ['XRP'],
        }
    
    def generate_signature(self, data, secret_key=None):
        """Generate Cryptomus signature"""
        data_string = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        
        if secret_key:
            sign_string = data_string + secret_key
        else:
            sign_string = data_string + self.api_key
        
        return hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    
    def create_payment(self, amount, currency, order_id, additional_data=None):
        """Create cryptocurrency payment"""
        try:
            # Generate unique payment UUID
            payment_uuid = str(uuid.uuid4())
            
            # Prepare request data
            data = {
                "amount": str(amount),
                "currency": currency.upper(),
                "order_id": order_id,
                "url_callback": additional_data.get('webhook_url', '') if additional_data else '',
                "url_return": additional_data.get('return_url', '') if additional_data else '',
                "url_success": additional_data.get('success_url', '') if additional_data else '',
                "is_payment_multiple": False,
                "lifetime": 1800,  # 30 minutes in seconds
                "to_currency": additional_data.get('to_currency') if additional_data else None,
                "subtract": 1,  # Subtract commission from received amount
            }
            
            # Filter out None values
            data = {k: v for k, v in data.items() if v is not None}
            
            # Generate signature
            sign = self.generate_signature(data)
            
            headers = {
                'Content-Type': 'application/json',
                'merchant': self.merchant_uuid,
                'sign': sign,
            }
            
            response = requests.post(
                f"{self.base_url}/payment",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('state') == 0:  #Success
                    result = response_data.get('result', {})
                    
                    return {
                        'success': True,
                        'payment_uuid': payment_uuid,
                        'payment_url': result.get('url'),
                        'payment_id': result.get('uuid'),
                        'amount': result.get('amount'),
                        'currency': result.get('currency'),
                        'address': result.get('address'),
                        'network': result.get('network'),
                        'expired_at': result.get('expired_at'),
                        'qr_code': result.get('qr_code'),
                        'data': response_data
                    }
                else:
                    raise ValidationError(f"Cryptomus error: {response_data.get('message')}")
            else:
                error_data = response.json()
                raise ValidationError(f"Cryptomus payment creation failed: {error_data}")
                
        except Exception as e:
            raise ValidationError(f"Cryptomus payment creation error: {str(e)}")
    
    def get_payment_info(self, payment_uuid):
        """Get payment information"""
        try:
            data = {"uuid": payment_uuid}
            sign = self.generate_signature(data)
            
            headers = {
                'Content-Type': 'application/json',
                'merchant': self.merchant_uuid,
                'sign': sign,
            }
            
            response = requests.post(
                f"{self.base_url}/payment/info",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('state') == 0:
                    result = response_data.get('result', {})
                    
                    return {
                        'success': True,
                        'payment_uuid': payment_uuid,
                        'status': result.get('status'),  # 'paid', 'pending', 'expired'
                        'amount': result.get('amount'),
                        'currency': result.get('currency'),
                        'paid_amount': result.get('paid_amount'),
                        'is_final': result.get('is_final'),
                        'data': response_data
                    }
                else:
                    raise ValidationError(f"Cryptomus error: {response_data.get('message')}")
            else:
                error_data = response.json()
                raise ValidationError(f"Cryptomus payment info failed: {error_data}")
                
        except Exception as e:
            raise ValidationError(f"Cryptomus payment info error: {str(e)}")
    
    def get_balance(self, currency=None):
        """Get wallet balance"""
        try:
            data = {}
            if currency:
                data["currency"] = currency.upper()
            
            sign = self.generate_signature(data)
            
            headers = {
                'Content-Type': 'application/json',
                'merchant': self.merchant_uuid,
                'sign': sign,
            }
            
            response = requests.post(
                f"{self.base_url}/balance",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('state') == 0:
                    return {
                        'success': True,
                        'balances': response_data.get('result', []),
                        'data': response_data
                    }
                else:
                    raise ValidationError(f"Cryptomus error: {response_data.get('message')}")
            else:
                error_data = response.json()
                raise ValidationError(f"Cryptomus balance check failed: {error_data}")
                
        except Exception as e:
            raise ValidationError(f"Cryptomus balance check error: {str(e)}")
    
    def verify_webhook_signature(self, payload, received_signature):
        """Verify webhook signature"""
        try:
            # Convert payload to string if it's dict
            if isinstance(payload, dict):
                payload_string = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
            else:
                payload_string = str(payload)
            
            # Generate expected signature
            sign_string = payload_string + self.webhook_secret
            expected_signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
            
            return hmac.compare_digest(expected_signature, received_signature)
            
        except Exception as e:
            raise ValidationError(f"Webhook signature verification failed: {str(e)}")
    
    def get_supported_currencies(self):
        """Get list of supported cryptocurrencies"""
        return list(self.supported_currencies.keys())
    
    def get_networks_for_currency(self, currency):
        """Get available networks for a currency"""
        currency_upper = currency.upper()
        return self.supported_currencies.get(currency_upper, [])
    
    def create_checkout_data(self, order_data, customer_info, request):
        """Create checkout data for Cryptomus"""
        try:
            # Calculate amount
            if order_data.get('checkout_type') == 'instant':
                amount = order_data.get('product', {}).get('price', 0)
                description = order_data.get('product', {}).get('title', 'Product')
            else:
                amount = order_data.get('cart', {}).get('total_amount', 0)
                description = f"Order #{order_data.get('order_id', '')}"
            
            # Create additional data
            additional_data = {
                'webhook_url': request.build_absolute_uri(
                    reverse('payments:cryptomus_webhook', args=[self.gateway.page.subdomain])
                ),
                'return_url': request.build_absolute_uri(
                    reverse('payments:cryptomus_callback', args=[self.gateway.page.subdomain])
                ),
                'success_url': request.build_absolute_uri(
                    reverse('payments:checkout_success', args=[self.gateway.page.subdomain])
                ),
                'order_id': description,
            }
            
            # Default to USDT
            currency = 'USDT'
            
            # Create payment
            result = self.create_payment(
                amount=amount,
                currency=currency,
                order_id=description,
                additional_data=additional_data
            )
            
            if result['success']:
                return {
                    'payment_url': result['payment_url'],
                    'payment_id': result['payment_id'],
                    'payment_uuid': result['payment_uuid'],
                    'amount': result['amount'],
                    'currency': result['currency'],
                    'address': result['address'],
                    'network': result['network'],
                    'expired_at': result['expired_at'],
                    'qr_code': result['qr_code'],
                    'order_id': description,
                    'is_crypto': True,
                    'gateway': 'cryptomus'
                }
            else:
                raise ValidationError("Failed to create Cryptomus payment")
                
        except Exception as e:
            raise ValidationError(f"Cryptomus checkout creation failed: {str(e)}")
