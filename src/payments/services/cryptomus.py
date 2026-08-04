# payments/services/cryptomus.py

import hashlib
import json
import requests
import base64
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class CryptomusService:
    """Cryptomus cryptocurrency payment gateway"""
    
    BASE_URL = 'https://api.cryptomus.com/v1'
    
    def __init__(self):
        self.merchant_id = settings.CRYPTOMUS_MERCHANT_ID
        self.api_key = settings.CRYPTOMUS_PAYMENT_API_KEY
        self.test_mode = getattr(settings, 'CRYPTOMUS_TEST_MODE', True)
    
    def _generate_sign(self, data):
        """Generate MD5 signature"""
        json_string = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        base64_encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        sign_string = f"{base64_encoded}{self.api_key}"
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
        return sign
    
    def _api_request(self, endpoint, data):
        """
        Make API request to Cryptomus.
        CRITICAL: Send data as raw JSON string, NOT as json parameter.
        """
        json_string = json.dumps(data, separators=(',', ':'))
        sign = self._generate_sign(data)
        
        headers = {
            'merchant': self.merchant_id,
            'sign': sign,
            'Content-Type': 'application/json',
        }
        
        logger.debug(f"API Request to {endpoint}")
        logger.debug(f"Data: {json_string}")
        logger.debug(f"Sign: {sign}")
        
        try:
            # ⚠️ IMPORTANT: Use data=json_string, NOT json=data
            response = requests.post(
                f"{self.BASE_URL}{endpoint}",
                data=json_string,
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('result'):
                return {'success': True, 'data': result['result']}
            else:
                error = result.get('message', 'Unknown error')
                logger.error(f"Cryptomus API error: {error}")
                return {'success': False, 'error': error}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {'success': False, 'error': str(e)}
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid response'}
    
    def create_payment(self, amount, order_id, currency='USDT',
                       success_url=None, cancel_url=None):
        """Create a payment invoice"""
        
        data = {
            'amount': f"{float(amount):.2f}",
            'currency': currency,
            'order_id': str(order_id),
        }
        
        # Add URLs if provided
        if success_url:
            data['url_return'] = success_url
            data['url_success'] = success_url
        
        if cancel_url:
            data['url_return'] = cancel_url
        
        # Add callback URL for webhooks
        callback_url = getattr(settings, 'CRYPTOMUS_CALLBACK_URL', '')
        if not callback_url:
            callback_url = f"{settings.SITE_URL}/payments/webhook/cryptomus/"
        data['url_callback'] = callback_url
        
        logger.info(f"Creating payment: {order_id} - {data['amount']} {currency}")
        
        result = self._api_request('/payment', data)
        
        if result['success']:
            payment = result['data']
            return {
                'success': True,
                'payment_url': payment.get('url'),
                'payment_uuid': payment.get('uuid'),
                'order_id': payment.get('order_id'),
                'amount': payment.get('amount'),
                'currency': payment.get('currency', currency),
                'status': payment.get('status'),
            }
        
        return result
    
    def create_payment_for_subscription(self, subscription, billing_period='monthly'):
        """Create payment for subscription"""
        from payments.models import PaymentTransaction
        import uuid
        
        plan = subscription.plan
        amount = plan.price_monthly if billing_period == 'monthly' else plan.price_yearly
        order_id = f"SUB-{subscription.id}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create transaction record
        transaction = PaymentTransaction.objects.create(
            user=subscription.user,
            subscription=subscription,
            plan=plan,
            transaction_id=order_id,
            amount=amount,
            currency='USD',
            billing_period=billing_period,
            status='pending',
            gateway_type='cryptomus'
        )
        
        # Create payment
        result = self.create_payment(
            amount=amount,
            order_id=order_id,
            currency='USDT',
            success_url=f"{settings.SITE_URL}/payments/success/",
            cancel_url=f"{settings.SITE_URL}/payments/pricing/",
        )
        
        if result.get('success'):
            transaction.status = 'processing'
            transaction.gateway_transaction_id = result['payment_uuid']
            transaction.gateway_response = result
            transaction.save()
            
            logger.info(f"Payment created: {result['payment_url']}")
            
            return {
                'success': True,
                'payment_url': result['payment_url'],
                'payment_uuid': result['payment_uuid'],
                'transaction': transaction,
            }
        else:
            transaction.status = 'failed'
            transaction.error_message = result.get('error', '')
            transaction.save()
            
            return {'success': False, 'error': result.get('error')}
    
    # payments/services/cryptomus.py - Update process_webhook

    def process_webhook(self, webhook_data):
        """Process incoming webhook and activate subscription"""
        
        if not self._verify_webhook_sign(webhook_data):
            return {'success': False, 'error': 'Invalid webhook signature'}
        
        order_id = webhook_data.get('order_id')
        payment_status = webhook_data.get('status')
        payment_uuid = webhook_data.get('uuid')
        
        logger.info(f"Webhook received: {order_id} - {payment_status}")
        
        if payment_status not in ['paid', 'paid_over']:
            logger.info(f"Ignoring status: {payment_status}")
            return {'success': True, 'ignored': True}
        
        # Payment confirmed! Now activate subscription
        from payments.models import PaymentTransaction, Subscription, Plan
        from django.utils import timezone
        
        try:
            transaction = PaymentTransaction.objects.get(transaction_id=order_id)
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Transaction not found: {order_id}")
            return {'success': False, 'error': 'Transaction not found'}
        
        # Mark transaction as completed
        transaction.status = 'completed'
        transaction.completed_at = timezone.now()
        transaction.gateway_response = webhook_data
        transaction.save()
        
        # Get metadata from transaction
        metadata = transaction.metadata or {}
        target_tier = metadata.get('target_plan_tier')
        billing_period = metadata.get('billing_period', 'monthly')
        
        if not target_tier:
            logger.error("No target tier in metadata")
            return {'success': False, 'error': 'No target tier'}
        
        # Get or create subscription for user
        subscription, created = Subscription.objects.get_or_create(
            user=transaction.user,
            defaults={'status': 'active'}
        )
        
        # Update subscription
        plan = Plan.objects.get(tier=target_tier)
        subscription.plan = plan
        subscription.status = 'active'
        subscription.billing_period = billing_period
        subscription.start_date = timezone.now()
        
        if billing_period == 'monthly':
            subscription.end_date = timezone.now() + timezone.timedelta(days=30)
        else:
            subscription.end_date = timezone.now() + timezone.timedelta(days=365)
        
        subscription.verified_at = timezone.now()
        subscription.amount_paid = transaction.amount
        subscription.payment_method = 'Cryptomus (Crypto)'
        subscription.payment_reference = payment_uuid
        subscription.save()
        
        # Link transaction to subscription
        transaction.subscription = subscription
        transaction.save()
        
        logger.info(f"✅ Subscription activated: {subscription.user.email} → {plan.name}")
        
        return {
            'success': True,
            'status': 'completed',
            'subscription_activated': True
        }