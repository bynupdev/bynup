from django.core.exceptions import ValidationError
from ..models import Order, Transaction
from decimal import Decimal

class PayOnDeliveryService:
    """Service for handling Pay on Delivery payments"""
    
    def __init__(self, gateway):
        self.gateway = gateway
    
    def validate_order_for_pod(self, order_data):
        """
        Validate if order is eligible for Pay on Delivery
        """
        total_amount = Decimal(str(order_data.get('total_amount', 0)))
        
        # Check minimum amount
        if total_amount < self.gateway.pod_minimum_amount:
            raise ValidationError(
                f"Minimum order amount for Pay on Delivery is ${self.gateway.pod_minimum_amount}"
            )
        
        # Check maximum amount
        if total_amount > self.gateway.pod_maximum_amount:
            raise ValidationError(
                f"Maximum order amount for Pay on Delivery is ${self.gateway.pod_maximum_amount}"
            )
        
        # Check delivery zones if configured
        delivery_zones = self.gateway.pod_available_zones or []
        customer_zone = order_data.get('customer', {}).get('delivery_zone', '')
        
        if delivery_zones and customer_zone not in delivery_zones:
            raise ValidationError(
                "Pay on Delivery is not available in your delivery zone"
            )
        
        return True
    
    def create_pod_order(self, order_data, customer_info, request):
        """
        Create Pay on Delivery order
        """
        try:
            # Import CheckoutService here to avoid circular imports
            from .checkout_service import CheckoutService
            
            # Validate order
            self.validate_order_for_pod(order_data)
            
            # Create checkout service instance
            checkout_service = CheckoutService(page=self.gateway.page, gateway=self.gateway)
            
            # Create order based on checkout type
            if order_data.get('checkout_type') == 'instant':
                order = checkout_service.create_order_from_product(
                    order_data.get('product', {}), 
                    customer_info
                )
            else:  # cart checkout
                order = checkout_service.create_order_from_cart(
                    order_data.get('cart', {}), 
                    customer_info
                )
            
            # Create transaction record for POD
            transaction = Transaction.objects.create(
                order=order,
                payment_gateway=self.gateway,
                gateway_transaction_id=f"POD-{order.order_number}",
                amount=order.total_amount,
                status='pending',
                currency='USD',
                gateway_response={
                    'payment_method': 'pay_on_delivery',
                    'requires_confirmation': self.gateway.pod_requires_confirmation,
                    'instructions': self.gateway.pod_instructions,
                    'created_at': order.created_at.isoformat()
                }
            )
            
            # Set order status to "pending_pod" (waiting for delivery)
            order.status = 'pending_pod'
            order.save()
            
            return {
                'success': True,
                'order_number': order.order_number,
                'transaction_id': transaction.id,
                'status': 'pending_pod',
                'instructions': self.gateway.pod_instructions,
                'requires_confirmation': self.gateway.pod_requires_confirmation,
                'message': 'Pay on Delivery order created successfully. You will pay when your order is delivered.'
            }
            
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Pay on Delivery order creation failed: {str(e)}")
    
    def confirm_payment_received(self, transaction_id, admin_user):
        """
        Confirm that payment was received upon delivery
        """
        try:
            transaction = Transaction.objects.get(
                id=transaction_id,
                payment_gateway=self.gateway,
                status='pending'
            )
            
            transaction.status = 'success'
            transaction.gateway_response['payment_received_at'] = timezone.now().isoformat()
            transaction.gateway_response['confirmed_by'] = admin_user.username
            transaction.processed_at = timezone.now()
            transaction.save()
            
            # Update order status
            order = transaction.order
            order.status = 'completed'
            order.paid_at = timezone.now()
            order.save()
            
            return {
                'success': True,
                'message': 'Payment confirmed successfully',
                'order_number': order.order_number
            }
            
        except Transaction.DoesNotExist:
            raise ValidationError("Transaction not found")
    
    def cancel_pod_order(self, transaction_id, reason):
        """
        Cancel a Pay on Delivery order
        """
        try:
            transaction = Transaction.objects.get(
                id=transaction_id,
                payment_gateway=self.gateway,
                status='pending'
            )
            
            transaction.status = 'failed'
            transaction.gateway_response['cancelled_at'] = timezone.now().isoformat()
            transaction.gateway_response['cancellation_reason'] = reason
            transaction.save()
            
            # Update order status
            order = transaction.order
            order.status = 'cancelled'
            order.save()
            
            return {
                'success': True,
                'message': 'Order cancelled successfully'
            }
            
        except Transaction.DoesNotExist:
            raise ValidationError("Transaction not found")