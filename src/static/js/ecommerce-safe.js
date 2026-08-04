class EcommerceManager {
    constructor(subdomain) {
        this.subdomain = subdomain;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupHTMXConfig();
        this.setupErrorHandling();
    }

    setupEventListeners() {
        // Handle quick add to cart from any page
        document.addEventListener('click', (e) => {
            const quickAddBtn = e.target.closest('[data-quick-add-to-cart]');
            if (quickAddBtn) {
                e.preventDefault();
                const productId = quickAddBtn.dataset.productId;
                const quantity = parseInt(quickAddBtn.dataset.quantity || 1);
                this.quickAddToCart(productId, quantity);
            }
        });
    }

    setupHTMXConfig() {
        // Configure HTMX with better error handling
        htmx.config.useTemplateFragments = true;
        htmx.config.selfRequestsOnly = false;
        
        // Add CSRF token to all HTMX requests
        document.body.addEventListener('htmx:configRequest', (event) => {
            event.detail.headers['X-CSRFToken'] = this.getCSRFToken();
        });

        // Handle HTMX errors
        document.body.addEventListener('htmx:responseError', (event) => {
            console.error('HTMX Error:', event.detail);
            this.showToast('An error occurred. Please try again.', 'error');
        });

        document.body.addEventListener('htmx:targetError', (event) => {
            console.error('HTMX Target Error:', event.detail);
            // Fallback: reload the page
            window.location.reload();
        });

        // Show loading states
        document.body.addEventListener('htmx:beforeRequest', (e) => {
            const target = e.detail.target;
            if (target) {
                target.style.opacity = '0.7';
                target.style.pointerEvents = 'none';
            }
        });

        document.body.addEventListener('htmx:afterRequest', (e) => {
            const target = e.detail.target;
            if (target) {
                target.style.opacity = '1';
                target.style.pointerEvents = 'auto';
            }
        });

        // Handle successful swaps
        document.body.addEventListener('htmx:afterSwap', (e) => {
            if (e.detail.target.id === 'cart-content' || e.detail.target.id === 'wishlist-content') {
                this.showToast('Updated successfully!', 'success');
            }
        });
    }

    setupErrorHandling() {
        // Global error handler for HTMX
        window.addEventListener('error', (e) => {
            if (e.message.includes('htmx')) {
                console.error('HTMX Global Error:', e);
                this.showToast('Something went wrong. Please refresh the page.', 'error');
            }
        });
    }

    async quickAddToCart(productId, quantity = 1) {
        const btn = document.querySelector(`[data-quick-add-to-cart="${productId}"]`);
        if (!btn) return;

        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        btn.disabled = true;

        try {
            const response = await fetch(`/ecommerce/cart/add/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showToast(`${data.product_name} added to cart!`, 'success');
                
                // If we're on the cart page, refresh the cart content
                if (window.location.href.includes('page=cart')) {
                    this.refreshCartContent();
                }
                
                // If we're on the wishlist page, refresh wishlist (item might be removed)
                if (window.location.href.includes('page=wishlist')) {
                    this.refreshWishlistContent();
                }
            } else {
                this.showToast('Error: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showToast('Error adding product to cart', 'error');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }

    async refreshCartContent() {
        try {
            const response = await fetch(`/ecommerce/cart/partial/${this.subdomain}/`);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const html = await response.text();
            const cartContent = document.getElementById('cart-content');
            if (cartContent) {
                cartContent.outerHTML = html;
            }
        } catch (error) {
            console.error('Error refreshing cart:', error);
            this.showToast('Error refreshing cart', 'error');
        }
    }

    async refreshWishlistContent() {
        try {
            const response = await fetch(`/ecommerce/wishlist/partial/${this.subdomain}/`);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const html = await response.text();
            const wishlistContent = document.getElementById('wishlist-content');
            if (wishlistContent) {
                wishlistContent.outerHTML = html;
            }
        } catch (error) {
            console.error('Error refreshing wishlist:', error);
            this.showToast('Error refreshing wishlist', 'error');
        }
    }

    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        const toastId = 'toast-' + Date.now();
        const typeClass = {
            'success': 'text-bg-success',
            'error': 'text-bg-danger',
            'info': 'text-bg-info',
            'warning': 'text-bg-warning'
        }[type] || 'text-bg-info';

        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center ${typeClass} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        
        // Use Bootstrap Toast if available, otherwise simple timeout
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
            toast.show();
        } else {
            // Fallback: show for 3 seconds then remove
            setTimeout(() => {
                if (toastElement.parentNode) {
                    toastElement.parentNode.removeChild(toastElement);
                }
            }, 3000);
        }

        // Remove toast from DOM after hide
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    getCSRFToken() {
        // Try multiple ways to get CSRF token
        const tokenFromInput = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        const tokenFromMeta = document.querySelector('meta[name="csrf-token"]')?.content;
        
        return tokenFromInput || tokenFromMeta || '';
    }
}

// Safe initialization with error handling
function initializeEcommerce() {
    try {
        const subdomain = window.pageSubdomain || 
                         document.querySelector('[data-page-subdomain]')?.dataset.pageSubdomain;
        
        if (subdomain) {
            window.ecommerceManager = new EcommerceManager(subdomain);
            console.log('Ecommerce manager initialized successfully');
        } else {
            console.warn('No subdomain found for ecommerce manager');
        }
    } catch (error) {
        console.error('Error initializing ecommerce manager:', error);
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEcommerce);
} else {
    initializeEcommerce();
}

// HTMX initialization with error handling
document.addEventListener('htmx:load', function() {
    try {
        const subdomain = window.pageSubdomain || 
                         document.querySelector('[data-page-subdomain]')?.dataset.pageSubdomain;
        
        if (subdomain && !window.ecommerceManager) {
            window.ecommerceManager = new EcommerceManager(subdomain);
        }
    } catch (error) {
        console.error('Error in htmx:load:', error);
    }
});