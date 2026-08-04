class PaymentGatewayHelper:
    """Helper class for payment gateway integration"""
    
    def __init__(self, page):
        self.page = page
        self.currency = page.currency_code
    
    def get_stripe_amount(self, amount):
        """Convert amount to Stripe format (cents for most currencies)"""
        try:
            amount_float = float(amount)
            
            # Special handling for zero-decimal currencies
            zero_decimal_currencies = ['JPY', 'KRW', 'VND', 'IDR']
            if self.currency in zero_decimal_currencies:
                return int(amount_float)
            
            # Most currencies need amount in cents/smallest unit
            return int(amount_float * 100)
        except (ValueError, TypeError):
            return 0
    
    def get_paypal_amount(self, amount):
        """Convert amount to PayPal format"""
        try:
            # PayPal expects string with 2 decimal places
            return f"{float(amount):.2f}"
        except (ValueError, TypeError):
            return "0.00"
    
    def get_razorpay_amount(self, amount):
        """Convert amount to Razorpay format (paise for INR)"""
        try:
            amount_float = float(amount)
            if self.currency == 'INR':
                # Razorpay expects paise (multiply by 100)
                return int(amount_float * 100)
            return int(amount_float * 100)
        except (ValueError, TypeError):
            return 0
    
    def get_square_amount(self, amount):
        """Convert amount to Square format (cents for USD)"""
        try:
            return int(float(amount) * 100)
        except (ValueError, TypeError):
            return 0
    
    def get_currency_code_for_gateway(self, gateway):
        """Get currency code for specific gateway"""
        # Check if there's a custom mapping
        if self.page.payment_currency_mapping and gateway in self.page.payment_currency_mapping:
            return self.page.payment_currency_mapping[gateway]
        
        # Return store currency by default
        return self.currency