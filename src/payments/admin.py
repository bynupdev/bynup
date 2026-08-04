from django.contrib import admin
from .models import *
from django.utils.html import format_html


from django import forms # Make sure this import is at the top

class PaymentGatewayAdminForm(forms.ModelForm):
    class Meta:
        model = PaymentGateway
        fields = '__all__'
        widgets = {
            # Stripe
            'test_secret_key': forms.PasswordInput(render_value=True),
            'live_secret_key': forms.PasswordInput(render_value=True),
            'webhook_secret': forms.PasswordInput(render_value=True),
            
            # PayPal
            'paypal_client_secret': forms.PasswordInput(render_value=True),
            'paypal_live_client_secret': forms.PasswordInput(render_value=True),
            
            # Cryptomus
            'cryptomus_api_key': forms.PasswordInput(render_value=True),
            'cryptomus_webhook_secret': forms.PasswordInput(render_value=True),
            
            # Telegram
            'telegram_bot_token': forms.PasswordInput(render_value=True),
        }

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    form = PaymentGatewayAdminForm
    list_display = ('page', 'gateway_type', 'is_active', 'is_test_mode')
    list_filter = ('gateway_type', 'is_active', 'is_test_mode')
    search_fields = ('page__brand_name', 'page__subdomain')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('page', 'gateway_type', 'is_active', 'is_test_mode')
        }),
        ('Pay on Delivery Settings', {
            'fields': (
                'pod_minimum_amount',
                'pod_maximum_amount',
                'pod_available_zones',
                'pod_instructions',
                'pod_requires_confirmation'
            ),
            'classes': ('collapse',)  # Collapsible section
        }),
        ('Stripe Settings', {
            'fields': (
                'test_public_key',
                'test_secret_key',
                'live_public_key',
                'live_secret_key',
                'webhook_secret'
            ),
            'classes': ('collapse',)
        }),
        ('PayPal Settings', {
            'fields': (
                'paypal_client_id',
                'paypal_client_secret',
                'paypal_live_client_id',
                'paypal_live_client_secret'
            ),
            'classes': ('collapse',)
        }),
        ('Crytomus Settings', {
            'fields': (
                'cryptomus_api_key',
                'cryptomus_merchant_uuid',
                'cryptomus_webhook_secret'
                
            ),
            'classes': ('collapse',)
        }),
        ('Social Media Settings', {
            'fields': (
                'social_media_platforms',
                'whatsapp_number',
                'whatsapp_business_name',
                'facebook_page_id',
                'facebook_messenger_link',
                'facebook_username',
                'instagram_username',
                'instagram_business_account',
                'telegram_username',
                'telegram_bot_token',
                'telegram_chat_id',
                'x_username',
                'x_dm_link',
                'social_media_order_prefix',
                'social_media_auto_send',
                'social_media_message_template'
                
                
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['order_number', 'page', 'customer_email', 'total_amount', 'status', 'created_at']
#     list_filter = ['status', 'created_at']
#     search_fields = ['order_number', 'customer_email', 'customer_name']

# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ['order', 'payment_gateway', 'amount', 'status', 'created_at']
#     list_filter = ['status', 'payment_gateway__gateway_type']
#     search_fields = ['gateway_transaction_id', 'order__order_number']

# admin.site.register(OrderItem)



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_title', 'product_price', 'quantity', 'total_price']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ['gateway_transaction_id', 'amount', 'status', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'customer_email', 'status_badge', 
                    'payment_status_badge', 'total_amount', 'created_at', 'page_display']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at', 'page']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'status_history']
    inlines = [OrderItemInline, TransactionInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'page', 'status', 'payment_status', 'payment_method')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'phone', 
                      'customer_address', 'customer_city', 'customer_state', 
                      'customer_zip', 'customer_country')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_city', 'delivery_state',
                      'delivery_zip', 'delivery_country', 'delivery_notes',
                      'delivery_date', 'delivery_time_slot')
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 
                      'discount_amount', 'total_amount', 'shipping_method', 'shipping_delivery_estimate', 'shipping_carrier')

        }),
        ('Notes', {
            'fields': ('customer_notes', 'internal_notes')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'referrer', 'utm_source',
                      'utm_medium', 'utm_campaign', 'status_history')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'processed_at',
                      'shipped_at', 'delivered_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        color = {
            'pending': 'warning',
            'pending_pod': 'warning',
            'processing': 'info',
            'ready_for_delivery': 'primary',
            'out_for_delivery': 'primary',
            'completed': 'success',
            'cancelled': 'danger',
            'refunded': 'secondary',
            'failed': 'dark',
        }.get(obj.status, 'secondary')
        
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        color = {
            'pending': 'warning',
            'paid': 'success',
            'partially_paid': 'info',
            'refunded': 'secondary',
            'failed': 'danger',
        }.get(obj.payment_status, 'secondary')
        
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment'
    
    def page_display(self, obj):
        return obj.page.brand_name
    page_display.short_description = 'Store'
    
    actions = ['mark_as_completed', 'mark_as_cancelled', 'export_selected_orders']
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed', payment_status='paid')
        self.message_user(request, f'{updated} orders marked as completed.')
    mark_as_completed.short_description = "Mark selected orders as completed"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} orders marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected orders as cancelled"
    
    def export_selected_orders(self, request, queryset):
        # Implement CSV export
        pass
    export_selected_orders.short_description = "Export selected orders to CSV"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product_title', 'order', 'quantity', 'product_price', 'total_price']
    list_filter = ['order__page', 'order__created_at']
    search_fields = ['product_title', 'order__order_number']
    readonly_fields = ['order', 'product_title', 'product_price', 'quantity', 'total_price']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['gateway_transaction_id', 'order', 'payment_gateway', 
                    'amount', 'status_badge', 'created_at']
    list_filter = ['status', 'payment_gateway__gateway_type', 'created_at']
    search_fields = ['gateway_transaction_id', 'order__order_number']
    readonly_fields = ['created_at', 'processed_at']
    
    def status_badge(self, obj):
        color = {
            'pending': 'warning',
            'success': 'success',
            'failed': 'danger',
            'refunded': 'secondary',
        }.get(obj.status, 'secondary')
        
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    
admin.site.register(TaxClass)
admin.site.register(TaxRate)
admin.site.register(TaxExemptCustomer)
admin.site.register(TaxReport)
admin.site.register(TaxTransaction)


admin.site.register(ShippingZone)
admin.site.register(ShippingRate)
admin.site.register(ShippingAddress)
admin.site.register(Plan)
admin.site.register(Subscription)
