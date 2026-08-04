class CheckoutManager {
    constructor(subdomain) {
        this.subdomain = subdomain;
        this.stripe = null;
        this.initializeStripe();
    }
    
    async initializeStripe() {
        // Stripe will be initialized when needed with the correct public key
        console.log('Checkout manager initialized for:', this.subdomain);
    }
    
    async initStripeWithKey(publicKey) {
        if (!window.Stripe) {
            console.error('Stripe.js not loaded');
            return null;
        }
        
        this.stripe = window.Stripe(publicKey);
        return this.stripe;
    }
    
    // Instant Checkout - Buy Now Button
    async handleBuyNow(productData, customerInfo = {}) {
        try {
            console.log('Starting instant checkout for:', productData);
            
            const response = await fetch(`/payments/checkout/instant/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    product: productData,
                    customer: customerInfo
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Checkout failed');
            }
            
            // Initialize Stripe with the public key
            await this.initStripeWithKey(result.public_key);
            
            // Redirect to Stripe Checkout
            const { error } = await this.stripe.redirectToCheckout({
                sessionId: result.session_id
            });
            
            if (error) {
                throw new Error(error.message);
            }
            
        } catch (error) {
            console.error('Instant checkout error:', error);
            this.showError(error.message);
        }
    }
    
    // Cart Checkout - Proceed to Checkout Button
    async handleCartCheckout(cartData, customerInfo = {}) {
        try {
            console.log('Starting cart checkout for:', cartData);
            
            const response = await fetch(`/payments/checkout/cart/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    cart: cartData,
                    customer: customerInfo
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Checkout failed');
            }
            
            // Initialize Stripe with the public key
            await this.initStripeWithKey(result.public_key);
            
            // Redirect to Stripe Checkout
            const { error } = await this.stripe.redirectToCheckout({
                sessionId: result.session_id
            });
            
            if (error) {
                throw new Error(error.message);
            }
            
        } catch (error) {
            console.error('Cart checkout error:', error);
            this.showError(error.message);
        }
    }
    
    // Get checkout status
    async getCheckoutStatus(orderNumber) {
        try {
            const response = await fetch(`/payments/checkout/status/${this.subdomain}/${orderNumber}/`);
            return await response.json();
        } catch (error) {
            console.error('Status check error:', error);
            return { error: error.message };
        }
    }
    
    // Utility methods
    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
    
    showError(message) {
        // Simple error display - you can enhance this with your preferred UI
        alert('Checkout Error: ' + message);
    }
    
    showSuccess(message) {
        alert('Success: ' + message);
    }
}

// Global checkout manager instance
window.checkoutManager = null;

// Initialize checkout manager
function initCheckoutManager(subdomain) {
    window.checkoutManager = new CheckoutManager(subdomain);
    return window.checkoutManager;
}