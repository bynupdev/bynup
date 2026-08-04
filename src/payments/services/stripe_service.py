#payments/services/stripe_service

import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from ..models import PaymentGateway, Transaction

class StripePaymentService:
    def __init__(self, payment_gateway):
        self.payment_gateway = payment_gateway
        self.setup_stripe()
    
    def setup_stripe(self):
        """Configure Stripe with user's API keys"""
        if self.payment_gateway.is_test_mode:
            api_key = self.payment_gateway.test_secret_key
        else:
            api_key = self.payment_gateway.live_secret_key
        
        if not api_key:
            raise ValidationError("Stripe secret key not configured")
        
        stripe.api_key = api_key
    
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """Create a Stripe Payment Intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return intent
        except stripe.error.StripeError as e:
            raise ValidationError(f"Stripe error: {str(e)}")
    
    def retrieve_payment_intent(self, payment_intent_id):
        """Retrieve a Payment Intent"""
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            raise ValidationError(f"Stripe error: {str(e)}")
    
    def create_checkout_session(self, order, success_url, cancel_url):
        """Create Stripe Checkout Session"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Order {order.order_number}",
                        },
                        'unit_amount': int(order.total_amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=order.customer_email,
                metadata={
                    'order_number': order.order_number,
                    'page_id': str(order.page.id)
                }
            )
            return session
        except stripe.error.StripeError as e:
            raise ValidationError(f"Stripe error: {str(e)}")
    
    def handle_webhook(self, payload, sig_header, webhook_secret):
        """Handle Stripe webhook"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            raise ValidationError("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise ValidationError("Invalid signature")
        


    def refund_payment(self, payment_intent_id, amount):
        """Refund a Stripe payment"""
        try:
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=int(amount * 100),  # Convert to cents
            )
            return {
                'success': True,
                'refund_id': refund.id,
                'status': refund.status,
                'amount': amount,
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f"Stripe refund failed: {str(e)}")
