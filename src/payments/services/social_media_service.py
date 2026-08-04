
# # payments/services/social_media_service.py

# import json
# import urllib.parse
# from django.urls import reverse
# from django.core.exceptions import ValidationError
# from django.utils import timezone
# import logging

# logger = logging.getLogger(__name__)

# class SocialMediaService:
#     """
#     Service for handling social media payment integration
#     """
    
#     def __init__(self, gateway):
#         self.gateway = gateway
#         self.supported_platforms = {
#             'whatsapp': self.format_whatsapp_message,
#             'facebook': self.format_facebook_message,
#             'instagram': self.format_instagram_message,
#             'telegram': self.format_telegram_message,
#             'x': self.format_x_message,
#         }
        
#         # Log the gateway configuration for debugging
#         logger.info(f"Initializing SocialMediaService for gateway ID: {gateway.id}")
#         logger.info(f"Enabled platforms: {gateway.social_media_platforms}")
#         logger.info(f"WhatsApp number: {gateway.whatsapp_number}")
#         logger.info(f"Facebook username: {gateway.facebook_username}")
#         logger.info(f"Instagram username: {gateway.instagram_username}")
#         logger.info(f"Telegram username: {gateway.telegram_username}")
#         logger.info(f"X username: {gateway.x_username}")
    
#     def validate_platform_config(self, platform):
#         """Validate that a platform is properly configured"""
#         if platform == 'whatsapp':
#             if not self.gateway.whatsapp_number:
#                 return False, "WhatsApp number is required"
#             # Basic validation - remove any non-numeric characters and check length
#             cleaned_number = ''.join(filter(str.isdigit, self.gateway.whatsapp_number))
#             if len(cleaned_number) < 10:
#                 return False, "WhatsApp number must be at least 10 digits"
#             return True, None
            
#         elif platform == 'facebook':
#             if not self.gateway.facebook_username and not self.gateway.facebook_messenger_link:
#                 return False, "Either Facebook username or messenger link is required"
#             return True, None
            
#         elif platform == 'instagram':
#             if not self.gateway.instagram_username:
#                 return False, "Instagram username is required"
#             return True, None
            
#         elif platform == 'telegram':
#             if not self.gateway.telegram_username:
#                 return False, "Telegram username is required"
#             return True, None
            
#         elif platform == 'x':
#             if not self.gateway.x_username and not self.gateway.x_dm_link:
#                 return False, "Either X username or DM link is required"
#             return True, None
            
#         return False, f"Unknown platform: {platform}"
    
#     def create_social_media_order(self, order_data, customer_info, request):
#         """
#         Create order and generate social media message
#         """
#         try:
#             # Import here to avoid circular imports
#             from ..models import Order, OrderItem, Transaction
#             import uuid

#             # Extract shipping details from order_data and add to customer_info
#             shipping_cost = order_data.get('shipping_cost', 0)
#             shipping_rate = order_data.get('shipping_rate', {})
            
#             # Add shipping details to customer_info so they get saved
#             customer_info['shipping_method'] = shipping_rate.get('name', 'Standard Shipping')
#             customer_info['delivery_estimate'] = shipping_rate.get('delivery_estimate', '')
#             customer_info['shipping_cost'] = shipping_cost
            
#             # Validate that at least one platform is enabled and configured
#             enabled_platforms = self.gateway.social_media_platforms or []
#             if not enabled_platforms:
#                 raise ValidationError("No social media platforms enabled. Please enable at least one platform.")
            
#             # Validate each enabled platform
#             configured_platforms = []
#             platform_errors = []
            
#             for platform in enabled_platforms:
#                 is_valid, error = self.validate_platform_config(platform)
#                 if is_valid:
#                     configured_platforms.append(platform)
#                 else:
#                     platform_errors.append(f"{platform}: {error}")
            
#             if not configured_platforms:
#                 error_msg = "No social media platforms properly configured.\n" + "\n".join(platform_errors)
#                 raise ValidationError(error_msg)
            
#             # Create order in database
#             order_number = f"{self.gateway.social_media_order_prefix}{uuid.uuid4().hex[:8].upper()}"
            
#             # Determine order type and create
#             if order_data.get('checkout_type') == 'instant':
#                 order = self._create_order_from_product(
#                     order_number, order_data.get('product', {}), customer_info
#                 )
#             else:
#                 order = self._create_order_from_cart(
#                     order_number, order_data.get('cart', {}), customer_info
#                 )
            
#             # Create transaction record
#             transaction = Transaction.objects.create(
#                 order=order,
#                 payment_gateway=self.gateway,
#                 gateway_transaction_id=f"SOC-{order.order_number}",
#                 amount=order.total_amount,
#                 status='pending',
#                 currency='USD',
#                 gateway_response={
#                     'payment_method': 'social_media',
#                     'platforms': configured_platforms,
#                     'created_at': order.created_at.isoformat()
#                 }
#             )
            
#             # Set order status
#             order.status = 'pending'
#             order.save()
            
#             # Generate social media messages for configured platforms
#             platform_messages = {}
#             for platform in configured_platforms:
#                 if platform in self.supported_platforms:
#                     try:
#                         formatter = self.supported_platforms[platform]
#                         result = formatter(order, customer_info, request)
#                         if result:
#                             platform_messages[platform] = result
#                             logger.info(f"Generated {platform} message successfully")
#                     except Exception as e:
#                         logger.error(f"Error formatting {platform} message: {str(e)}")
#                         # Continue with other platforms even if one fails
            
#             if not platform_messages:
#                 raise ValidationError("Failed to generate messages for any configured platform")
            
#             return {
#                 'success': True,
#                 'order_number': order.order_number,
#                 'transaction_id': transaction.id,
#                 'platform_messages': platform_messages,
#                 'customer_info': customer_info,
#                 'order_details': {
#                     'order_number': order.order_number,
#                     'subtotal': float(order.subtotal),
#                     'tax_amount': float(order.tax_amount),
#                     'shipping_amount': float(order.shipping_amount),
#                     'discount_amount': float(order.discount_amount),
#                     'total_amount': float(order.total_amount),
#                     'customer_name': order.customer_name,
#                     'customer_email': order.customer_email,
#                     'phone': order.phone,
#                     'created_at': order.created_at.isoformat() if order.created_at else None,
#                 },
#                 'message': 'Social media order created successfully'
#             }
            
#         except ValidationError as e:
#             logger.error(f"Validation error in create_social_media_order: {str(e)}")
#             raise
#         except Exception as e:
#             logger.error(f"Unexpected error in create_social_media_order: {str(e)}")
#             raise ValidationError(f"Social media order creation failed: {str(e)}")
    
#     def _create_order_from_product(self, order_number, product_data, customer_info):
#         """Create order from single product"""
#         from ..models import Order, OrderItem
        
#         # Calculate totals
#         quantity = int(product_data.get('quantity', 1))
#         price = float(product_data.get('price', 0))
#         subtotal = price * quantity
        
#         # Get tax and shipping
#         tax_amount = float(product_data.get('tax_amount', 0))
#         # shipping_amount = float(product_data.get('shipping_amount', 0))
#         shipping_method = customer_info.get('shipping_method', 'Standard Shipping')
#         delivery_estimate = customer_info.get('delivery_estimate', '')
#         shipping_amount =customer_info.get('shipping_cost', 0)
#         total_amount = subtotal + tax_amount + shipping_amount

        

        
#         order = Order.objects.create(
#             page=self.gateway.page,
#             order_number=order_number,
#             customer_email=customer_info.get('email', ''),
#             customer_name=customer_info.get('name', ''),
#             phone=customer_info.get('phone', ''),
#             customer_address=customer_info.get('address', ''),
#             customer_city=customer_info.get('city', ''),
#             customer_state=customer_info.get('state', ''),
#             customer_zip=customer_info.get('zip', ''),
#             customer_country=customer_info.get('country', ''),
#             country_iso=customer_info.get('country_iso', ''),
#             delivery_address=customer_info.get('delivery_address', customer_info.get('address', '')),
#             delivery_city=customer_info.get('delivery_city', customer_info.get('city', '')),
#             delivery_state=customer_info.get('delivery_state', customer_info.get('state', '')),
#             delivery_zip=customer_info.get('delivery_zip', customer_info.get('zip', '')),
#             delivery_country=customer_info.get('country', 'US'),
#             delivery_notes=customer_info.get('delivery_notes', ''),
#             subtotal=subtotal,
#             tax_amount=tax_amount,
#             shipping_amount=shipping_amount,
#             total_amount=total_amount,
#             payment_method='social_media',
#             ip_address=customer_info.get('ip_address'),
#             user_agent=customer_info.get('user_agent', ''),
#             shipping_method=shipping_method,
#             shipping_delivery_estimate=delivery_estimate,

#         )
        
#         OrderItem.objects.create(
#             order=order,
#             product_id=str(product_data.get('id', '')),
#             product_title=product_data.get('title', ''),
#             product_description=product_data.get('description', ''),
#             product_price=price,
#             quantity=quantity,
#             total_price=total_amount,
#             selected_color=product_data.get('selected_color', ''),
#             selected_size=product_data.get('selected_size', ''),
#             product_variant=f"{product_data.get('selected_color', '')} {product_data.get('selected_size', '')}".strip(),
#             product_sku=product_data.get('sku', ''),
#             product_image=product_data.get('image_url', ''),
#             vid=product_data.get('vid', ''),
#         )
        
#         return order
    
#     def _create_order_from_cart(self, order_number, cart_data, customer_info):
#         """Create order from cart data"""
#         from ..models import Order, OrderItem
#         print(f"Customer info is {customer_info}")
#         print(f"Cart data info is {cart_data}")
#         shipping_method = customer_info.get('shipping_method', 'Standard Shipping')
#         delivery_estimate = customer_info.get('delivery_estimate', '')
#         shipping_amount =customer_info.get('shipping_cost', 0)
#         order = Order.objects.create(
#             page=self.gateway.page,
#             order_number=order_number,
#             customer_email=customer_info.get('email', ''),
#             customer_name=customer_info.get('name', ''),
#             phone=customer_info.get('phone', ''),
#             customer_address=customer_info.get('address', ''),
#             customer_city=customer_info.get('city', ''),
#             customer_state=customer_info.get('state', ''),
#             customer_zip=customer_info.get('zip', ''),
#             customer_country=customer_info.get('country', ''),
#             country_iso=customer_info.get('country_iso', ''),
#             delivery_address=customer_info.get('delivery_address', customer_info.get('address', '')),
#             delivery_city=customer_info.get('delivery_city', customer_info.get('city', '')),
#             delivery_state=customer_info.get('delivery_state', customer_info.get('state', '')),
#             delivery_zip=customer_info.get('delivery_zip', customer_info.get('zip', '')),
#             delivery_country=customer_info.get('country', 'US'),
#             delivery_notes=customer_info.get('delivery_notes', ''),
#             subtotal=float(cart_data.get('subtotal', 0)),
#             tax_amount=float(cart_data.get('tax_amount', 0)),
#             shipping_amount=shipping_amount,
#             discount_amount=float(cart_data.get('discount_amount', 0)),
#             total_amount=float(cart_data.get('total_amount', 0)),
#             payment_method='social_media',
#             ip_address=customer_info.get('ip_address'),
#             user_agent=customer_info.get('user_agent', ''),
            
#             shipping_method=shipping_method,
#             shipping_delivery_estimate=delivery_estimate,
#         )
        
#         for item in cart_data.get('items', []):
#             quantity = int(item.get('quantity', 1))
#             price = float(item.get('price', 0))
            
#             OrderItem.objects.create(
#                 order=order,
#                 product_id=str(item.get('id', '')),
#                 product_title=item.get('title', ''),
#                 product_description=item.get('description', ''),
#                 product_price=price,
#                 quantity=quantity,
#                 total_price=float(item.get('total_price', price * quantity)),
#                 selected_color=item.get('selected_color', ''),
#                 selected_size=item.get('selected_size', ''),
#                 product_variant=f"{item.get('selected_color', '')} {item.get('selected_size', '')}".strip(),
#                 product_sku=item.get('sku', ''),
#                 product_image=item.get('image_url', ''),
#                 vid=item.get('vid', ''),
#             )
        
#         return order
    
#     def format_whatsapp_message(self, order, customer_info, request):
#         """Format order details for WhatsApp"""
#         try:
#             if not self.gateway.whatsapp_number:
#                 logger.warning("WhatsApp number is missing")
#                 return None
            
#             # Clean the WhatsApp number
#             whatsapp_number = self.gateway.whatsapp_number.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
#             # Build message
#             message = self._get_message_template(order, customer_info, request)
            
#             # Create WhatsApp deep link
#             encoded_message = urllib.parse.quote(message)
#             whatsapp_link = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
            
#             logger.info(f"WhatsApp link generated for number: {whatsapp_number}")
            
#             return {
#                 'platform': 'whatsapp',
#                 'contact': self.gateway.whatsapp_number,
#                 'business_name': self.gateway.whatsapp_business_name or "Store",
#                 'message': message,
#                 'link': whatsapp_link
#             }
#         except Exception as e:
#             logger.error(f"Error formatting WhatsApp message: {str(e)}")
#             return None
    
#     def format_facebook_message(self, order, customer_info, request):
#         """Format order details for Facebook Messenger"""
#         try:
#             if not self.gateway.facebook_messenger_link and not self.gateway.facebook_username:
#                 logger.warning("Facebook credentials missing")
#                 return None
            
#             message = self._get_message_template(order, customer_info, request)
#             encoded_message = urllib.parse.quote(message)
            
#             # Create messenger link
#             if self.gateway.facebook_messenger_link:
#                 base_link = self.gateway.facebook_messenger_link
#             elif self.gateway.facebook_username:
#                 base_link = f"https://m.me/{self.gateway.facebook_username}"
#             else:
#                 return None
            
#             # Append message to URL if supported
#             if '?' in base_link:
#                 messenger_link = f"{base_link}&text={encoded_message}"
#             else:
#                 messenger_link = f"{base_link}?text={encoded_message}"
            
#             return {
#                 'platform': 'facebook',
#                 'page_id': self.gateway.facebook_page_id,
#                 'username': self.gateway.facebook_username,
#                 'message': message,
#                 'link': messenger_link
#             }
#         except Exception as e:
#             logger.error(f"Error formatting Facebook message: {str(e)}")
#             return None
    
#     def format_instagram_message(self, order, customer_info, request):
#         """Format order details for Instagram DM"""
#         try:
#             if not self.gateway.instagram_username:
#                 logger.warning("Instagram username missing")
#                 return None
            
#             message = self._get_instagram_message_template(order, customer_info, request)
            
#             # Instagram DM link (note: may redirect to app)
#             instagram_link = f"https://www.instagram.com/{self.gateway.instagram_username}/"
            
#             return {
#                 'platform': 'instagram',
#                 'username': self.gateway.instagram_username,
#                 'business_account': self.gateway.instagram_business_account,
#                 'message': message,
#                 'link': instagram_link,
#                 'instructions': "Copy this message and send via Instagram DM"
#             }
#         except Exception as e:
#             logger.error(f"Error formatting Instagram message: {str(e)}")
#             return None
    
#     def format_telegram_message(self, order, customer_info, request):
#         """Format order details for Telegram"""
#         try:
#             if not self.gateway.telegram_username:
#                 logger.warning("Telegram username missing")
#                 return None
            
#             message = self._get_message_template(order, customer_info, request)
#             encoded_message = urllib.parse.quote(message)
            
#             # Telegram deep link
#             telegram_username = self.gateway.telegram_username.replace('@', '')
#             telegram_link = f"https://t.me/{telegram_username}?text={encoded_message}"
            
#             return {
#                 'platform': 'telegram',
#                 'username': self.gateway.telegram_username,
#                 'message': message,
#                 'link': telegram_link
#             }
#         except Exception as e:
#             logger.error(f"Error formatting Telegram message: {str(e)}")
#             return None
    
#     def format_x_message(self, order, customer_info, request):
#         """Format order details for X.com (Twitter) DM"""
#         try:
#             if not self.gateway.x_username and not self.gateway.x_dm_link:
#                 logger.warning("X credentials missing")
#                 return None
            
#             message = self._get_x_message_template(order, customer_info, request)
            
#             # X.com DM link
#             if self.gateway.x_dm_link:
#                 x_link = self.gateway.x_dm_link
#             elif self.gateway.x_username:
#                 x_link = f"https://twitter.com/messages/compose?recipient_id={self.gateway.x_username}"
#             else:
#                 return None
            
#             return {
#                 'platform': 'x',
#                 'username': self.gateway.x_username,
#                 'message': message,
#                 'link': x_link,
#                 'instructions': "Copy this message and send via Direct Message"
#             }
#         except Exception as e:
#             logger.error(f"Error formatting X message: {str(e)}")
#             return None
    
#     def _get_message_template(self, order, customer_info, request):
#         """Get professional order message template"""
#         try:
#             # Build items list
#             items_text = ""
#             for item in order.items.all():
#                 variant = f" ({item.selected_color} {item.selected_size})".strip() if item.selected_color or item.selected_size else ""
#                 items_text += f"\n• {item.quantity}x {item.product_title}{variant}\n  ${item.product_price} each → ${item.total_price}"
            
#             # Use custom template if provided
#             if self.gateway.social_media_message_template:
#                 template = self.gateway.social_media_message_template
#                 # Replace placeholders
#                 template = template.replace('{{order_number}}', order.order_number)
#                 template = template.replace('{{customer_name}}', customer_info.get('name', 'N/A'))
#                 template = template.replace('{{customer_email}}', customer_info.get('email', 'N/A'))
#                 template = template.replace('{{customer_phone}}', customer_info.get('phone', 'N/A'))
#                 template = template.replace('{{total_amount}}', f"${order.total_amount}")
#                 template = template.replace('{{order_date}}', timezone.now().strftime('%Y-%m-%d %H:%M'))
#                 template = template.replace('{{items}}', items_text)
#                 return template
            
#             # Default professional template
#             message = f"""🛍️ *NEW ORDER #{order.order_number}*

# ━━━━━━━━━━━━━━━━━━━━━
# 👤 *CUSTOMER DETAILS*
# ━━━━━━━━━━━━━━━━━━━━━
# Name: {customer_info.get('name', 'N/A')}
# Email: {customer_info.get('email', 'N/A')}
# Phone: {customer_info.get('phone', 'N/A')}

# ━━━━━━━━━━━━━━━━━━━━━
# 📍 *DELIVERY ADDRESS*
# ━━━━━━━━━━━━━━━━━━━━━
# {customer_info.get('address', 'N/A')}
# {customer_info.get('city', 'N/A')}, {customer_info.get('state', 'N/A')} {customer_info.get('zip', 'N/A')}
# {customer_info.get('country', 'N/A')}

# ━━━━━━━━━━━━━━━━━━━━━
# 📦 *ORDER ITEMS*
# ━━━━━━━━━━━━━━━━━━━━━{items_text}

# ━━━━━━━━━━━━━━━━━━━━━
# 💰 *ORDER SUMMARY*
# ━━━━━━━━━━━━━━━━━━━━━
# Subtotal: ${order.subtotal}
# Shipping: ${order.shipping_amount}
# Tax: ${order.tax_amount}
# ━━━━━━━━━━━━━━━━━━━━━
# *TOTAL: ${order.total_amount}*
# ━━━━━━━━━━━━━━━━━━━━━

# 📝 *Delivery Notes:*
# {customer_info.get('delivery_notes', 'None')}

# ━━━━━━━━━━━━━━━━━━━━━
# ⏱️ Order placed: {timezone.now().strftime('%Y-%m-%d %H:%M UTC')}

# Please confirm receipt of this order and provide payment instructions.
# Thank you for choosing {self.gateway.page.brand_name}! 🙏"""
            
#             return message
#         except Exception as e:
#             logger.error(f"Error creating message template: {str(e)}")
#             return "Error creating order message. Please contact support."
    
#     def _get_instagram_message_template(self, order, customer_info, request):
#         """Instagram-friendly template (shorter, emoji-heavy)"""
#         items_summary = ""
#         for item in order.items.all():
#             items_summary += f"\n• {item.quantity}x {item.product_title[:20]}"
        
#         message = f"""🛍️ NEW ORDER #{order.order_number}

# 👤 {customer_info.get('name', 'N/A')}
# 📧 {customer_info.get('email', 'N/A')}
# 📞 {customer_info.get('phone', 'N/A')}

# 📍 {customer_info.get('address', 'N/A')}
# {customer_info.get('city', 'N/A')}, {customer_info.get('state', 'N/A')} {customer_info.get('zip', 'N/A')}

# 📦 ITEMS:{items_summary}

# 💰 TOTAL: ${order.total_amount}

# ⏱️ {timezone.now().strftime('%Y-%m-%d %H:%M')}"""
        
#         return message
    
#     def _get_x_message_template(self, order, customer_info, request):
#         """X.com/Twitter friendly template (very concise)"""
#         items_list = []
#         for item in order.items.all():
#             items_list.append(f"{item.quantity}x {item.product_title[:20]}")
#         items_summary = ", ".join(items_list)
        
#         try:
#             order_detail_url = request.build_absolute_uri(
#                 reverse('payments:customer_order_detail', args=[order.page.subdomain, order.order_number])
#             ) + f"?email={order.customer_email}"
#         except:
#             order_detail_url = "#"
        
#         message = f"""New Order #{order.order_number}
# Customer: {customer_info.get('name')}
# Items: {items_summary}
# Total: ${order.total_amount}
# Delivery: {customer_info.get('city')}, {customer_info.get('country')}
# Order details: {order_detail_url}"""
        
#         return message





# payments/services/social_media_service.py

import json
import urllib.parse
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
from payments.utils import check_and_deduct_stock

logger = logging.getLogger(__name__)


class SocialMediaService:
    """
    Service for handling social media payment integration
    """
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.page = gateway.page
        self.supported_platforms = {
            'whatsapp': self.format_whatsapp_message,
            'facebook': self.format_facebook_message,
            'instagram': self.format_instagram_message,
            'telegram': self.format_telegram_message,
            'x': self.format_x_message,
        }
        
        logger.info(f"Initializing SocialMediaService for gateway ID: {gateway.id}")
        logger.info(f"Enabled platforms: {gateway.social_media_platforms}")
    
    # ============ CURRENCY FORMATTING ============
    
    def format_price(self, amount):
        """
        Format price using the store's currency settings
        Returns formatted price like: $4.00, €4,00, XAF4000, etc.
        """
        if amount is None:
            return ''
        
        try:
            # Convert to float
            amount_float = float(amount)
            
            # Get currency settings directly from the page
            currency_symbol = self.page.currency_symbol
            currency_position = self.page.currency_position
            thousand_separator = self.page.thousand_separator
            decimal_separator = self.page.decimal_separator
            decimal_places = self.page.decimal_places
            
            # Format the number with proper decimal places
            if decimal_places == 0:
                # No decimals (like JPY, XAF)
                formatted = f"{int(round(amount_float)):,}"
                formatted = formatted.replace(',', thousand_separator)
            else:
                # With decimals
                format_string = f"{{:,.{decimal_places}f}}"
                formatted = format_string.format(amount_float)
                # Replace the separators
                formatted = formatted.replace(',', 'XXX').replace('.', 'YYY')
                formatted = formatted.replace('XXX', thousand_separator).replace('YYY', decimal_separator)
            
            # Add currency symbol based on position
            if currency_position == 'before':
                return f"{currency_symbol}{formatted}"
            elif currency_position == 'after':
                return f"{formatted}{currency_symbol}"
            elif currency_position == 'before_space':
                return f"{currency_symbol} {formatted}"
            elif currency_position == 'after_space':
                return f"{formatted} {currency_symbol}"
            else:
                return f"{currency_symbol}{formatted}"
                
        except Exception as e:
            logger.error(f"Price formatting failed: {e}")
            # Fallback
            try:
                return f"${float(amount):.2f}"
            except:
                return str(amount)
    
    def get_currency_code(self):
        """Get the store's currency code (USD, XAF, EUR, etc.)"""
        return self.page.currency_code
    
    def get_currency_symbol(self):
        """Get the store's currency symbol ($, FCFA, €, etc.)"""
        return self.page.currency_symbol
    
    # ============ PLATFORM VALIDATION ============
    
    def validate_platform_config(self, platform):
        """Validate that a platform is properly configured"""
        if platform == 'whatsapp':
            if not self.gateway.whatsapp_number:
                return False, "WhatsApp number is required"
            cleaned_number = ''.join(filter(str.isdigit, self.gateway.whatsapp_number))
            if len(cleaned_number) < 10:
                return False, "WhatsApp number must be at least 10 digits"
            return True, None
            
        elif platform == 'facebook':
            if not self.gateway.facebook_username and not self.gateway.facebook_messenger_link:
                return False, "Either Facebook username or messenger link is required"
            return True, None
            
        elif platform == 'instagram':
            if not self.gateway.instagram_username:
                return False, "Instagram username is required"
            return True, None
            
        elif platform == 'telegram':
            if not self.gateway.telegram_username:
                return False, "Telegram username is required"
            return True, None
            
        elif platform == 'x':
            if not self.gateway.x_username and not self.gateway.x_dm_link:
                return False, "Either X username or DM link is required"
            return True, None
            
        return False, f"Unknown platform: {platform}"
    
    # ============ ORDER CREATION ============
    
    def create_social_media_order(self, order_data, customer_info, request):
        """
        Create order and generate social media message
        """
        try:
            from ..models import Order, OrderItem, Transaction
            import uuid

            shipping_cost = order_data.get('shipping_cost', 0)
            shipping_rate = order_data.get('shipping_rate', {})
            
            customer_info['shipping_method'] = shipping_rate.get('name', 'Standard Shipping')
            customer_info['delivery_estimate'] = shipping_rate.get('delivery_estimate', '')
            customer_info['shipping_cost'] = shipping_cost
            
            enabled_platforms = self.gateway.social_media_platforms or []
            if not enabled_platforms:
                raise ValidationError("No social media platforms enabled. Please enable at least one platform.")
            
            configured_platforms = []
            platform_errors = []
            
            for platform in enabled_platforms:
                is_valid, error = self.validate_platform_config(platform)
                if is_valid:
                    configured_platforms.append(platform)
                else:
                    platform_errors.append(f"{platform}: {error}")
            
            if not configured_platforms:
                error_msg = "No social media platforms properly configured.\n" + "\n".join(platform_errors)
                raise ValidationError(error_msg)
            
            order_number = f"{self.gateway.social_media_order_prefix}{uuid.uuid4().hex[:8].upper()}"
            
            if order_data.get('checkout_type') == 'instant':
                order = self._create_order_from_product(
                    order_number, order_data.get('product', {}), customer_info
                )
            else:
                order = self._create_order_from_cart(
                    order_number, order_data.get('cart', {}), customer_info
                )
            
            transaction = Transaction.objects.create(
                order=order,
                payment_gateway=self.gateway,
                gateway_transaction_id=f"SOC-{order.order_number}",
                amount=order.total_amount,
                status='pending',
                currency=self.page.currency_code,
                gateway_response={
                    'payment_method': 'social_media',
                    'platforms': configured_platforms,
                    'created_at': order.created_at.isoformat()
                }
            )
            
            order.status = 'pending'
            order.save()
            
            platform_messages = {}
            for platform in configured_platforms:
                if platform in self.supported_platforms:
                    try:
                        formatter = self.supported_platforms[platform]
                        result = formatter(order, customer_info, request)
                        if result:
                            platform_messages[platform] = result
                            logger.info(f"Generated {platform} message successfully")
                    except Exception as e:
                        logger.error(f"Error formatting {platform} message: {str(e)}")
            
            if not platform_messages:
                raise ValidationError("Failed to generate messages for any configured platform")
            
            return {
                'success': True,
                'order_number': order.order_number,
                'transaction_id': transaction.id,
                'platform_messages': platform_messages,
                'customer_info': customer_info,
                'order_details': {
                    'order_number': order.order_number,
                    'subtotal': float(order.subtotal),
                    'tax_amount': float(order.tax_amount),
                    'shipping_amount': float(order.shipping_amount),
                    'discount_amount': float(order.discount_amount),
                    'total_amount': float(order.total_amount),
                    'customer_name': order.customer_name,
                    'customer_email': order.customer_email,
                    'phone': order.phone,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                },
                'message': 'Social media order created successfully'
            }
            
        except ValidationError as e:
            logger.error(f"Validation error in create_social_media_order: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_social_media_order: {str(e)}")
            raise ValidationError(f"Social media order creation failed: {str(e)}")
    
    def _create_order_from_product(self, order_number, product_data, customer_info):
        """Create order from single product"""
        from ..models import Order, OrderItem
        
        
    # Get product ID - try both 'id' and 'product_id'
        product_id = product_data.get('id') or product_data.get('product_id')
        quantity = product_data.get('quantity', 1)
        
        # ONE LINE - Validates AND deducts stock
        success, error = check_and_deduct_stock(self.page, [{'product_id': product_id, 'quantity': quantity}])
        if not success:
            raise ValidationError(error)        
        quantity = int(product_data.get('quantity', 1))
        price = float(product_data.get('price', 0))
        subtotal = price * quantity
        
        tax_amount = float(product_data.get('tax_amount', 0))
        shipping_method = customer_info.get('shipping_method', 'Standard Shipping')
        delivery_estimate = customer_info.get('delivery_estimate', '')
        shipping_amount = customer_info.get('shipping_cost', 0)
        total_amount = subtotal + tax_amount + shipping_amount
        
        order = Order.objects.create(
            page=self.gateway.page,
            order_number=order_number,
            customer_email=customer_info.get('email', ''),
            customer_name=customer_info.get('name', ''),
            phone=customer_info.get('phone', ''),
            customer_address=customer_info.get('address', ''),
            customer_city=customer_info.get('city', ''),
            customer_state=customer_info.get('state', ''),
            customer_zip=customer_info.get('zip', ''),
            customer_country=customer_info.get('country', ''),
            country_iso=customer_info.get('country_iso', ''),
            delivery_address=customer_info.get('delivery_address', customer_info.get('address', '')),
            delivery_city=customer_info.get('delivery_city', customer_info.get('city', '')),
            delivery_state=customer_info.get('delivery_state', customer_info.get('state', '')),
            delivery_zip=customer_info.get('delivery_zip', customer_info.get('zip', '')),
            delivery_country=customer_info.get('country', 'US'),
            delivery_notes=customer_info.get('delivery_notes', ''),
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            payment_method='social_media',
            ip_address=customer_info.get('ip_address'),
            user_agent=customer_info.get('user_agent', ''),
            shipping_method=shipping_method,
            shipping_delivery_estimate=delivery_estimate,
        )
        
        OrderItem.objects.create(
            order=order,
            product_id=str(product_data.get('id', '')),
            product_title=product_data.get('title', ''),
            product_description=product_data.get('description', ''),
            product_price=price,
            quantity=quantity,
            total_price=total_amount,
            selected_color=product_data.get('selected_color', ''),
            selected_size=product_data.get('selected_size', ''),
            product_variant=f"{product_data.get('selected_color', '')} {product_data.get('selected_size', '')}".strip(),
            product_sku=product_data.get('sku', ''),
            product_image=product_data.get('image_url', ''),
            vid=product_data.get('vid', ''),
        )

        try:
            from .email_service import EmailService # Import here to avoid circular imports
            EmailService.send_order_confirmation(order)
            # Notify the Store Owner
            EmailService.send_admin_order_notification(order)
        except Exception as e:
            # We don't want to crash the whole checkout if only the email fails
            print(f"Notification error: {e}")
        
        return order
    
    def _create_order_from_cart(self, order_number, cart_data, customer_info):
        """Create order from cart data"""
        from ..models import Order, OrderItem
    # Build items list for stock validation - handle all possible key names
        items = []
        for item in cart_data.get('items', []):
            # Try all possible keys for product ID
            product_id = (item.get('product_id') or 
                        item.get('id') or 
                        item.get('product'))
            quantity = item.get('quantity', 1)
            items.append({'product_id': product_id, 'quantity': quantity})
        
        # ONE LINE - Validates AND deducts stock
        success, error = check_and_deduct_stock(self.page, items)
        if not success:
            raise ValidationError(error)
    
        shipping_method = customer_info.get('shipping_method', 'Standard Shipping')
        delivery_estimate = customer_info.get('delivery_estimate', '')
        shipping_amount = customer_info.get('shipping_cost', 0)
        
        order = Order.objects.create(
            page=self.gateway.page,
            order_number=order_number,
            customer_email=customer_info.get('email', ''),
            customer_name=customer_info.get('name', ''),
            phone=customer_info.get('phone', ''),
            customer_address=customer_info.get('address', ''),
            customer_city=customer_info.get('city', ''),
            customer_state=customer_info.get('state', ''),
            customer_zip=customer_info.get('zip', ''),
            customer_country=customer_info.get('country', ''),
            country_iso=customer_info.get('country_iso', ''),
            delivery_address=customer_info.get('delivery_address', customer_info.get('address', '')),
            delivery_city=customer_info.get('delivery_city', customer_info.get('city', '')),
            delivery_state=customer_info.get('delivery_state', customer_info.get('state', '')),
            delivery_zip=customer_info.get('delivery_zip', customer_info.get('zip', '')),
            delivery_country=customer_info.get('country', 'US'),
            delivery_notes=customer_info.get('delivery_notes', ''),
            subtotal=float(cart_data.get('subtotal', 0)),
            tax_amount=float(cart_data.get('tax_amount', 0)),
            shipping_amount=shipping_amount,
            discount_amount=float(cart_data.get('discount_amount', 0)),
            total_amount=float(cart_data.get('total_amount', 0)),
            payment_method='social_media',
            ip_address=customer_info.get('ip_address'),
            user_agent=customer_info.get('user_agent', ''),
            shipping_method=shipping_method,
            shipping_delivery_estimate=delivery_estimate,
        )
        
        for item in cart_data.get('items', []):
            quantity = int(item.get('quantity', 1))
            price = float(item.get('price', 0))
            
            OrderItem.objects.create(
                order=order,
                product_id=str(item.get('id', '')),
                product_title=item.get('title', ''),
                product_description=item.get('description', ''),
                product_price=price,
                quantity=quantity,
                total_price=float(item.get('total_price', price * quantity)),
                selected_color=item.get('selected_color', ''),
                selected_size=item.get('selected_size', ''),
                product_variant=f"{item.get('selected_color', '')} {item.get('selected_size', '')}".strip(),
                product_sku=item.get('sku', ''),
                product_image=item.get('image_url', ''),
                vid=item.get('vid', ''),
            )

        try:
            from .email_service import EmailService # Import here to avoid circular imports
            EmailService.send_order_confirmation(order)
            # Notify the Store Owner
            EmailService.send_admin_order_notification(order)
        except Exception as e:
            # We don't want to crash the whole checkout if only the email fails
            print(f"Notification error: {e}")
        
        return order
    
    # ============ MESSAGE FORMATTING ============
    
    def format_whatsapp_message(self, order, customer_info, request):
        """Format order details for WhatsApp"""
        try:
            if not self.gateway.whatsapp_number:
                logger.warning("WhatsApp number is missing")
                return None
            
            whatsapp_number = self.gateway.whatsapp_number.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            message = self._get_message_template(order, customer_info, request)
            encoded_message = urllib.parse.quote(message)
            whatsapp_link = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
            
            return {
                'platform': 'whatsapp',
                'contact': self.gateway.whatsapp_number,
                'business_name': self.gateway.whatsapp_business_name or "Store",
                'message': message,
                'link': whatsapp_link
            }
        except Exception as e:
            logger.error(f"Error formatting WhatsApp message: {str(e)}")
            return None
    
    def format_facebook_message(self, order, customer_info, request):
        """Format order details for Facebook Messenger"""
        try:
            if not self.gateway.facebook_messenger_link and not self.gateway.facebook_username:
                logger.warning("Facebook credentials missing")
                return None
            
            message = self._get_message_template(order, customer_info, request)
            encoded_message = urllib.parse.quote(message)
            
            if self.gateway.facebook_messenger_link:
                base_link = self.gateway.facebook_messenger_link
            elif self.gateway.facebook_username:
                base_link = f"https://m.me/{self.gateway.facebook_username}"
            else:
                return None
            
            if '?' in base_link:
                messenger_link = f"{base_link}&text={encoded_message}"
            else:
                messenger_link = f"{base_link}?text={encoded_message}"
            
            return {
                'platform': 'facebook',
                'page_id': self.gateway.facebook_page_id,
                'username': self.gateway.facebook_username,
                'message': message,
                'link': messenger_link
            }
        except Exception as e:
            logger.error(f"Error formatting Facebook message: {str(e)}")
            return None
    
    def format_instagram_message(self, order, customer_info, request):
        """Format order details for Instagram DM"""
        try:
            if not self.gateway.instagram_username:
                logger.warning("Instagram username missing")
                return None
            
            message = self._get_instagram_message_template(order, customer_info, request)
            instagram_link = f"https://www.instagram.com/{self.gateway.instagram_username}/"
            
            return {
                'platform': 'instagram',
                'username': self.gateway.instagram_username,
                'business_account': self.gateway.instagram_business_account,
                'message': message,
                'link': instagram_link,
                'instructions': "Copy this message and send via Instagram DM"
            }
        except Exception as e:
            logger.error(f"Error formatting Instagram message: {str(e)}")
            return None
    
    def format_telegram_message(self, order, customer_info, request):
        """Format order details for Telegram"""
        try:
            if not self.gateway.telegram_username:
                logger.warning("Telegram username missing")
                return None
            
            message = self._get_message_template(order, customer_info, request)
            encoded_message = urllib.parse.quote(message)
            
            telegram_username = self.gateway.telegram_username.replace('@', '')
            telegram_link = f"https://t.me/{telegram_username}?text={encoded_message}"
            
            return {
                'platform': 'telegram',
                'username': self.gateway.telegram_username,
                'message': message,
                'link': telegram_link
            }
        except Exception as e:
            logger.error(f"Error formatting Telegram message: {str(e)}")
            return None
    
    def format_x_message(self, order, customer_info, request):
        """Format order details for X.com (Twitter) DM"""
        try:
            if not self.gateway.x_username and not self.gateway.x_dm_link:
                logger.warning("X credentials missing")
                return None
            
            message = self._get_x_message_template(order, customer_info, request)
            
            if self.gateway.x_dm_link:
                x_link = self.gateway.x_dm_link
            elif self.gateway.x_username:
                x_link = f"https://twitter.com/messages/compose?recipient_id={self.gateway.x_username}"
            else:
                return None
            
            return {
                'platform': 'x',
                'username': self.gateway.x_username,
                'message': message,
                'link': x_link,
                'instructions': "Copy this message and send via Direct Message"
            }
        except Exception as e:
            logger.error(f"Error formatting X message: {str(e)}")
            return None
    
    def _get_message_template(self, order, customer_info, request):
        """Get professional order message template with store currency formatting"""
        try:
            # Build items list with FORMATTED PRICES using store currency
            items_text = ""
            for item in order.items.all():
                variant = ""
                if item.selected_color or item.selected_size:
                    variant = f" ({item.selected_color} {item.selected_size})".strip()
                
                # Format prices using store currency
                item_price = self.format_price(item.product_price)
                item_total = self.format_price(item.total_price)
                
                items_text += f"\n• {item.quantity}x {item.product_title}{variant}\n  {item_price} each → {item_total}"
            
            # Format order totals with store currency
            subtotal = self.format_price(order.subtotal)
            shipping = self.format_price(order.shipping_amount)
            tax = self.format_price(order.tax_amount)
            total = self.format_price(order.total_amount)
            currency_code = self.get_currency_code()
            
            # Use custom template if provided
            if self.gateway.social_media_message_template:
                template = self.gateway.social_media_message_template
                template = template.replace('{{order_number}}', order.order_number)
                template = template.replace('{{customer_name}}', customer_info.get('name', 'N/A'))
                template = template.replace('{{customer_email}}', customer_info.get('email', 'N/A'))
                template = template.replace('{{customer_phone}}', customer_info.get('phone', 'N/A'))
                template = template.replace('{{total_amount}}', total)
                template = template.replace('{{subtotal}}', subtotal)
                template = template.replace('{{shipping}}', shipping)
                template = template.replace('{{tax}}', tax)
                template = template.replace('{{currency_code}}', currency_code)
                template = template.replace('{{order_date}}', timezone.now().strftime('%Y-%m-%d %H:%M'))
                template = template.replace('{{items}}', items_text)
                return template
            
            # Default professional template with STORE CURRENCY
            message = f"""🛍️ *NEW ORDER #{order.order_number}*

━━━━━━━━━━━━━━━━━━━━━
👤 *CUSTOMER DETAILS*
━━━━━━━━━━━━━━━━━━━━━
Name: {customer_info.get('name', 'N/A')}
Email: {customer_info.get('email', 'N/A')}
Phone: {customer_info.get('phone', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━
📍 *DELIVERY ADDRESS*
━━━━━━━━━━━━━━━━━━━━━
{customer_info.get('address', 'N/A')}
{customer_info.get('city', 'N/A')}, {customer_info.get('state', 'N/A')} {customer_info.get('zip', 'N/A')}
{customer_info.get('country', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━
📦 *ORDER ITEMS*
━━━━━━━━━━━━━━━━━━━━━{items_text}

━━━━━━━━━━━━━━━━━━━━━
💰 *ORDER SUMMARY ({currency_code})*
━━━━━━━━━━━━━━━━━━━━━
Subtotal: {subtotal}
Shipping: {shipping}
Tax: {tax}
━━━━━━━━━━━━━━━━━━━━━
*TOTAL: {total}*
━━━━━━━━━━━━━━━━━━━━━

📝 *Delivery Notes:*
{customer_info.get('delivery_notes', 'None')}

━━━━━━━━━━━━━━━━━━━━━
⏱️ Order placed: {timezone.now().strftime('%Y-%m-%d %H:%M UTC')}

Please confirm receipt of this order and provide payment instructions.
Thank you for choosing {self.gateway.page.brand_name}! 🙏"""
            
            return message
        except Exception as e:
            logger.error(f"Error creating message template: {str(e)}")
            return "Error creating order message. Please contact support."
    
    def _get_instagram_message_template(self, order, customer_info, request):
        """Instagram-friendly template with store currency"""
        items_summary = ""
        for item in order.items.all():
            item_price = self.format_price(item.product_price)
            items_summary += f"\n• {item.quantity}x {item.product_title[:20]} ({item_price})"
        
        total = self.format_price(order.total_amount)
        currency_code = self.get_currency_code()
        
        message = f"""🛍️ NEW ORDER #{order.order_number}

👤 {customer_info.get('name', 'N/A')}
📧 {customer_info.get('email', 'N/A')}
📞 {customer_info.get('phone', 'N/A')}

📍 {customer_info.get('address', 'N/A')}
{customer_info.get('city', 'N/A')}, {customer_info.get('state', 'N/A')} {customer_info.get('zip', 'N/A')}

📦 ITEMS:{items_summary}

💰 TOTAL: {total} {currency_code}

⏱️ {timezone.now().strftime('%Y-%m-%d %H:%M')}"""
        
        return message
    
    def _get_x_message_template(self, order, customer_info, request):
        """X.com/Twitter friendly template with store currency"""
        items_list = []
        for item in order.items.all():
            item_price = self.format_price(item.product_price)
            items_list.append(f"{item.quantity}x {item.product_title[:20]} ({item_price})")
        items_summary = ", ".join(items_list)
        
        total = self.format_price(order.total_amount)
        currency_code = self.get_currency_code()
        
        try:
            order_detail_url = request.build_absolute_uri(
                reverse('payments:customer_order_detail', args=[order.page.subdomain, order.order_number])
            ) + f"?email={order.customer_email}"
        except:
            order_detail_url = "#"
        
        message = f"""New Order #{order.order_number}
Customer: {customer_info.get('name')}
Items: {items_summary}
Total: {total} {currency_code}
Delivery: {customer_info.get('city')}, {customer_info.get('country')}
Order details: {order_detail_url}"""
        
        return message