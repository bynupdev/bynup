# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.conf import settings
# from django.urls import reverse
# from email.utils import formataddr

# class EmailService:
#     @staticmethod
#     def _get_clean_from_email(brand_name):
#         """
#         Safely formats the 'From' header to avoid:
#         Store Name <Bynup <info@bynup.store>>
#         """
#         raw_email = settings.DEFAULT_FROM_EMAIL
        
#         # If DEFAULT_FROM_EMAIL is "Bynup <info@bynup.store>", 
#         # we extract only "info@bynup.store"
#         if "<" in raw_email:
#             clean_email = raw_email.split("<")[-1].replace(">", "").strip()
#         else:
#             clean_email = raw_email.strip()
            
#         # Returns "Brand Name <clean_email@site.com>" correctly formatted
#         return formataddr((brand_name, clean_email))

#     @staticmethod
#     def send_order_confirmation(order):
#         """Sends a confirmation email to the customer"""
#         subject = f"Order Confirmation {order.order_number} - {order.page.brand_name}"
#         from_email = EmailService._get_clean_from_email(order.page.brand_name)
#         to = order.customer_email

#         context = {
#             'order': order,
#             'page': order.page,
#             'brand_name': order.page.brand_name,
#             'items': order.items.all()
#         }
        
#         html_content = render_to_string('emails/order_confirmation.html', context)
#         text_content = strip_tags(html_content)

#         email = EmailMultiAlternatives(subject, text_content, from_email, [to])
#         email.attach_alternative(html_content, "text/html")
        
#         try:
#             email.send()
#             return True
#         except Exception as e:
#             print(f"Customer Email failed: {str(e)}")
#             return False

#     @staticmethod
#     def send_admin_order_notification(order):
#         """Sends an alert to the store owner/admin"""
#         subject = f"New Order: {order.order_number} - {order.page.brand_name}"
#         # We use the Platform Name for admin alerts
#         from_email = EmailService._get_clean_from_email("Bynup Orders")
        
#         # Recipient is the store owner's email
#         # admin_email = order.page.user.email if hasattr(order.page, 'user') else settings.DEFAULT_FROM_EMAIL
#         admin_email = None
#         if order.page.user and order.page.user.email:
#             admin_email = order.page.user.email
#         else:
#             # Fallback to a default admin email or log the issue
#             admin_email = settings.DEFAULT_FROM_EMAIL
#             print(f"⚠️ No owner email found for store: {order.page.brand_name} (subdomain: {order.page.subdomain})")

#         context = {
#             'order': order,
#             'page': order.page,
#             'brand_name': order.page.brand_name,
#             'items': order.items.all()
#         }
        
#         html_content = render_to_string('emails/admin_new_order.html', context)
#         text_content = strip_tags(html_content)

#         email = EmailMultiAlternatives(subject, text_content, from_email, [admin_email])
#         email.attach_alternative(html_content, "text/html")
        
#         try:
#             email.send()
#             return True
#         except Exception as e:
#             print(f"Admin Email failed: {str(e)}")
#             return False
        

#     @staticmethod
#     def send_subscription_pending_notification(subscription):
#         """Notify User that their upgrade is pending verification"""
#         subject = f"Upgrade Pending: {subscription.plan.name} - {subscription.payment_reference}"
#         to_email = subscription.user.email
        
#         context = {
#             'user': subscription.user,
#             'subscription': subscription,
#             'plan_name': subscription.plan.name,
#             'reference': subscription.payment_reference,
#             'amount': subscription.amount_paid,
#         }
        
#         html_content = render_to_string('emails/subscription_pending_user.html', context)
#         text_content = strip_tags(html_content)
        
#         email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_email])
#         email.attach_alternative(html_content, "text/html")
#         email.send()

#     @staticmethod
#     def send_admin_subscription_alert(subscription):
#         """Notify Admin (You) to verify a new payment"""
#         subject = f"NEW PAYMENT: {subscription.user.email} - {subscription.payment_reference}"
        
#         context = {
#             'subscription': subscription,
#             'user': subscription.user,
#         }
        
#         html_content = render_to_string('emails/subscription_pending_admin.html', context)
#         text_content = strip_tags(html_content)
        
#         email = EmailMultiAlternatives(
#             subject, 
#             text_content, 
#             settings.DEFAULT_FROM_EMAIL, 
#             [settings.DEFAULT_FROM_EMAIL] # Or your specific admin email
#         )
#         email.attach_alternative(html_content, "text/html")
#         email.send()



from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from email.utils import formataddr


class EmailService:
    
    @staticmethod
    def _get_clean_from_email(brand_name):
        """
        Safely formats the 'From' header to avoid:
        Store Name <Bynup <info@bynup.store>>
        """
        raw_email = settings.DEFAULT_FROM_EMAIL
        
        if "<" in raw_email:
            clean_email = raw_email.split("<")[-1].replace(">", "").strip()
        else:
            clean_email = raw_email.strip()
            
        return formataddr((brand_name, clean_email))

    @staticmethod
    def _get_order_items_with_images(order):
        """
        Enrich order items with product images from the Product model.
        Returns a list of dicts with image URLs and variant details.
        """
        from builder.models import Product
        
        enriched_items = []
        
        for item in order.items.all():
            image_url = None
            
            try:
                product = Product.objects.filter(
                    page=order.page, 
                    id=item.product_id
                ).first()
                
                if product and product.main_image:
                    image_url = product.main_image.url
                elif product and product.product_images.exists():
                    image_url = product.product_images.first().image.url
            except Exception:
                pass
            
            if not image_url and item.product_image:
                image_url = item.product_image
            
            enriched_items.append({
                'title': item.product_title,
                'quantity': item.quantity,
                'price': item.product_price,
                'total_price': item.total_price,
                'image_url': image_url,
                'selected_color': item.selected_color or '',
                'selected_size': item.selected_size or '',
            })
        
        return enriched_items

    @staticmethod
    def _get_transaction_info(order):
        """
        Get payment gateway and transaction details from the Transaction model.
        Returns a dict with gateway_display, gateway_type, transaction_status.
        """
        from payments.models import Transaction
        
        transaction = Transaction.objects.filter(
            order=order
        ).select_related('payment_gateway').first()
        
        if transaction:
            gateway_type = transaction.payment_gateway.gateway_type
            gateway_display = transaction.payment_gateway.get_gateway_type_display()
            
            # Clean up the display name for common gateways
            gateway_names = {
                'stripe': 'Stripe',
                'paypal': 'PayPal',
                'razorpay': 'Razorpay',
                'fincra': 'Fincra',
                'cryptomus': 'Cryptomus',
                'pay_on_delivery': 'Pay on Delivery',
                'social_media': 'Social Media',
            }
            
            return {
                'gateway_type': gateway_type,
                'gateway_display': gateway_names.get(gateway_type, gateway_display),
                'gateway_transaction_id': transaction.gateway_transaction_id or '',
                'transaction_status': transaction.status,
                'transaction_status_display': transaction.get_status_display(),
            }
        
        # Fallback to order.payment_method
        payment_method = order.payment_method if hasattr(order, 'payment_method') else 'unknown'
        gateway_names = {
            'stripe': 'Stripe',
            'paypal': 'PayPal',
            'razorpay': 'Razorpay',
            'fincra': 'Fincra',
            'cryptomus': 'Cryptomus',
            'pay_on_delivery': 'Pay on Delivery',
            'social_media': 'Social Media',
            'bank_transfer': 'Bank Transfer',
        }
        
        return {
            'gateway_type': payment_method,
            'gateway_display': gateway_names.get(payment_method, payment_method.title()),
            'gateway_transaction_id': '',
            'transaction_status': 'pending',
            'transaction_status_display': 'Pending',
        }

    @staticmethod
    def _get_base_context(order):
        from payments.models import Transaction
        
        # First, try to get payment method from the most recent transaction
        transaction = Transaction.objects.filter(
            order=order
        ).select_related('payment_gateway').order_by('-created_at').first()
        
        if transaction and transaction.payment_gateway:
            # Get the gateway_type directly from the PaymentGateway model
            payment_method = transaction.payment_gateway.gateway_type
            
            # Convert to display name
            gateway_names = {
                'stripe': 'Stripe',
                'paypal': 'PayPal', 
                'razorpay': 'Razorpay',
                'fincra': 'Fincra',
                'cryptomus': 'Cryptomus',
                'pay_on_delivery': 'Pay on Delivery',
                'social_media': 'Social Media',
                'bank_transfer': 'Bank Transfer',
            }
            
            payment_display = gateway_names.get(payment_method, payment_method)
        else:
            # Fallback to order's payment_method field
            payment_method = getattr(order, 'payment_method', 'stripe')
            
            # Also check if it's pay_on_delivery or social_media based on order status
            if order.status == 'pending_pod':
                payment_method = 'pay_on_delivery'
            
            gateway_names = {
                'stripe': 'Stripe',
                'paypal': 'PayPal',
                'razorpay': 'Razorpay',
                'fincra': 'Fincra',
                'cryptomus': 'Cryptomus',
                'pay_on_delivery': 'Pay on Delivery',
                'social_media': 'Social Media',
                'bank_transfer': 'Bank Transfer',
            }
            
            payment_display = gateway_names.get(payment_method, payment_method.title())
        
        return {
            'order': order,
            'page': order.page,
            'brand_name': order.page.brand_name,
            'items': EmailService._get_order_items_with_images(order),
            'payment_method': payment_display,  # This is what the template uses
            'shop_url': f"https://{order.page.subdomain}.bynup.store",
            'order_tracking_url': f"https://{order.page.subdomain}.bynup.store/payments/customer/orders/{order.page.subdomain}/",
            'admin_orders_url': f"https://www.bynup.store/payments/orders/dashboard/{order.page.subdomain}/",
        }
    # ──────────────────────────────────────────────
    # Order Emails
    # ──────────────────────────────────────────────

    @staticmethod
    def send_order_confirmation(order):
        """Sends a confirmation email to the customer"""
        subject = f"Order Confirmation #{order.order_number} – {order.page.brand_name}"
        from_email = EmailService._get_clean_from_email(order.page.brand_name)
        to = order.customer_email

        context = EmailService._get_base_context(order)
        
        html_content = render_to_string('emails/order_confirmation.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(subject, text_content, from_email, [to])
        email.attach_alternative(html_content, "text/html")
        
        try:
            email.send()
            return True
        except Exception as e:
            print(f"❌ Customer Email failed: {str(e)}")
            return False

    @staticmethod
    def send_admin_order_notification(order):
        """Sends an alert to the store owner/admin"""
        subject = f"New Order #{order.order_number} – {order.page.brand_name}"
        from_email = EmailService._get_clean_from_email("Bynup Orders")
        
        # Determine admin email
        admin_email = None
        if hasattr(order.page, 'user') and order.page.user and order.page.user.email:
            admin_email = order.page.user.email
        else:
            admin_email = settings.DEFAULT_FROM_EMAIL
            print(f"⚠️ No owner email found for store: {order.page.brand_name} "
                  f"(subdomain: {order.page.subdomain})")

        context = EmailService._get_base_context(order)
        context['admin_url'] = context['admin_orders_url']
        
        html_content = render_to_string('emails/admin_new_order.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(subject, text_content, from_email, [admin_email])
        email.attach_alternative(html_content, "text/html")
        
        try:
            email.send()
            return True
        except Exception as e:
            print(f"❌ Admin Email failed: {str(e)}")
            return False

    # ──────────────────────────────────────────────
    # Subscription Emails
    # ──────────────────────────────────────────────

    @staticmethod
    def send_subscription_pending_notification(subscription):
        """Notify User that their upgrade is pending verification"""
        from payments.models import PaymentTransaction
        
        transaction = PaymentTransaction.objects.filter(
            subscription=subscription
        ).order_by('-created_at').first()
        
        subject = f"Upgrade Pending: {subscription.plan.name} – {subscription.payment_reference}"
        to_email = subscription.user.email
        
        context = {
            'user': subscription.user,
            'subscription': subscription,
            'plan_name': subscription.plan.name,
            'reference': subscription.payment_reference,
            'amount': subscription.amount_paid,
            'payment_gateway': transaction.get_gateway_type_display() if transaction else 'Unknown',
            'gateway_transaction_id': transaction.gateway_transaction_id if transaction else '',
        }
        
        html_content = render_to_string('emails/subscription_pending_user.html', context)
        text_content = strip_tags(html_content)
        
        from_email = EmailService._get_clean_from_email("Bynup")
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_admin_subscription_alert(subscription):
        """Notify Admin to verify a new payment"""
        from payments.models import PaymentTransaction
        
        transaction = PaymentTransaction.objects.filter(
            subscription=subscription
        ).order_by('-created_at').first()
        
        subject = f"New Payment: {subscription.user.email} – {subscription.payment_reference}"
        
        context = {
            'subscription': subscription,
            'user': subscription.user,
            'payment_gateway': transaction.get_gateway_type_display() if transaction else 'Unknown',
            'gateway_transaction_id': transaction.gateway_transaction_id if transaction else '',
            'transaction_status': transaction.get_status_display() if transaction else 'Unknown',
        }
        
        html_content = render_to_string('emails/subscription_pending_admin.html', context)
        text_content = strip_tags(html_content)
        
        from_email = EmailService._get_clean_from_email("Bynup Payments")
        email = EmailMultiAlternatives(
            subject, 
            text_content, 
            from_email, 
            [settings.DEFAULT_FROM_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()