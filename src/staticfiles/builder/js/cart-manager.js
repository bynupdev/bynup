class CartManager {
    constructor(subdomain, options = {}) {
        this.subdomain = subdomain;
        this.csrfToken = this.getCSRFToken();
        this.products = new Map();
        this.options = {
            autoDiscover: true,
            autoCreateButtons: true,
            ...options
        };
        
        this.ensureSession();
        this.initializeCart();
    }



    ensureSession() {
        // Create a session if one doesn't exist
        if (!this.getSessionId()) {
            this.createSession();
        }
    }

    getSessionId() {
        return localStorage.getItem(`cart_session_${this.subdomain}`);
    }

    createSession() {
        const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem(`cart_session_${this.subdomain}`, sessionId);
        return sessionId;
    }

    async initializeCart() {
        console.log('🛒 Initializing Cart Manager...');
        
        // Collect product data from the page
        this.collectProductData();
        
        // Initialize cart functionality
        this.setupCartIcon();
        this.initializeButtons();

        this.initializeVariantSelection();
        
        // Load current cart state from backend
        await this.loadCartData();
        
        console.log(`📦 Cart Manager ready with ${this.products.size} products`);
    }


    initializeVariantSelection() {
    // Color Variant Selection
    const colorOptions = document.querySelectorAll('.color-option');
    
    colorOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove active class from all color options
            colorOptions.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked color option
            this.classList.add('active');
            
            // In a real implementation, you would update product images based on color
            const selectedColor = this.getAttribute('data-color');
            console.log(`Selected color: ${selectedColor}`);
            
            // NEW: Store selected color in product data if applicable
            // const productId = this.closest('[data-product-id]')?.dataset.productId;
            // if (productId) {
            //     const product = this.cartManager?.products.get(productId);
            //     if (product) {
            //         product.selectedColor = selectedColor;
            //     }
            // }
        });
    });
    
    // Size Variant Selection
    const sizeOptions = document.querySelectorAll('.size-option:not(.disabled)');
    
    sizeOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove active class from all size options
            sizeOptions.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked size option
            this.classList.add('active');
            
            // In a real implementation, you would check stock availability
            const selectedSize = this.getAttribute('data-size');
            console.log(`Selected size: ${selectedSize}`);
            
            // NEW: Store selected size in product data if applicable
            const productId = this.closest('[data-product-id]')?.dataset.productId;
            if (productId) {
                const product = this.cartManager?.products.get(productId);
                if (product) {
                    product.selectedSize = selectedSize;
                }
            }
        });
    });
}

    collectProductData() {
        // Method 1: Collect from product cards with data attributes
        document.querySelectorAll('[data-product-id]').forEach(element => {
            const productId = element.dataset.productId;
            const productData = {
                id: productId,
                title: element.dataset.productTitle || 
                      element.querySelector('[data-product-title]')?.textContent || 
                      'Product',
                price: parseFloat(element.dataset.productPrice) || 
                      this.parsePrice(element.querySelector('[data-product-price]')?.textContent) || 
                      0,
                image: element.dataset.productImage || 
                      element.querySelector('[data-product-image]')?.src || 
                      null,
                element: element,
                hasVariants: element.dataset.hasVariants === 'true' || false,
                availableColors: element.dataset.availableColors || '',
                availableSizes: element.dataset.availableSizes || ''
            };
            
            this.products.set(productId, productData);
            console.log(`📦 Collected product: ${productData.title} (ID: ${productId})`);
            
            // Auto-create buttons if enabled
            if (this.options.autoCreateButtons) {
                this.createCartButtons(element, productId);
            }
        });

        // Method 2: Collect from backend data passed via JavaScript
        if (window.productsData) {
            window.productsData.forEach(product => {
                this.products.set(product.id.toString(), {
                    id: product.id.toString(),
                    title: product.title,
                    price: parseFloat(product.price),
                    image: product.image_url || null,
                    element: null,
                    hasVariants: element.dataset.hasVariants === 'true' || false,
                    availableColors: element.dataset.availableColors || '',
                    availableSizes: element.dataset.availableSizes || ''
                });
            });
            console.log(`📦 Loaded ${window.productsData.length} products from backend data`);
        }
    }

    createCartButtons(element, productId) {
        const buttonsContainer = element.querySelector('.cart-buttons') || 
                                this.createButtonsContainer(element);
        
        if (!buttonsContainer.querySelector('.add-to-cart-btn')) {
            buttonsContainer.innerHTML = `
                <button style="display:none;" class="btn btn-sm btn-primary add-to-cart-btn" 
                        data-product-id="${productId}">
                    <i class="fas fa-cart-plus"></i> Add to Cart
                </button>
                <button style="display:none;"  class="btn btn-sm btn-outline-danger add-to-wishlist-btn ms-1" 
                        data-product-id="${productId}">
                    <i class="fas fa-heart"></i> Wishlist
                </button>
            `;
            
            // Add event listeners
            buttonsContainer.querySelector('.add-to-cart-btn').addEventListener('click', (e) => {
                e.preventDefault();
                this.addToCart(productId, 1);
            });
            
            buttonsContainer.querySelector('.add-to-wishlist-btn').addEventListener('click', (e) => {
                e.preventDefault();
                this.addToWishlist(productId);
            });
        }
    }

    createButtonsContainer(element) {
        const container = document.createElement('div');
        container.className = 'cart-buttons mt-2';
        element.appendChild(container);
        return container;
    }

    setupCartIcon() {
        if (!document.querySelector('.cart-icon-container')) {
            const nav = document.querySelector('nav') || document.body;
            const cartIcon = document.createElement('div');
            cartIcon.className = 'cart-icon-container';
            cartIcon.innerHTML = `
                <div class="position-relative d-inline-block me-3" style="display: none;">
                    <a href="/builder/cart/${this.subdomain}/" class="btn btn-outline-primary position-relative">
                        <i class="fas fa-shopping-cart" style="display: none;"></i>
                        <span class="cart-counter position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" 
                              style="display: none;">0</span>
                    </a>
                </div>
                <div class="position-relative d-inline-block" style="display: none;>
                    <a href="/builder/wishlist/${this.subdomain}/" class="btn btn-outline-danger position-relative">
                        <i class="fas fa-heart"></i>
                        <span class="wishlist-counter position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" 
                              style="display: none;">0</span>
                    </a>
                </div>
            `;
            
            if (nav) {
                nav.insertBefore(cartIcon, nav.firstChild);
            } else {
                document.body.insertBefore(cartIcon, document.body.firstChild);
            }
        }
    }

    initializeButtons() {
        // Initialize manual buttons
        document.querySelectorAll('[data-add-to-cart]').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const productId = button.dataset.addToCart;
                const quantity = parseInt(button.dataset.quantity) || 1;
                this.addToCart(productId, quantity);
            });
        });

        document.querySelectorAll('[data-add-to-wishlist]').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const productId = button.dataset.addToWishlist;
                this.addToWishlist(productId);
            });
        });

         document.querySelectorAll('[data-remove-from-wishlist]').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const productId = button.dataset.removeFromWishlist;
                this.removeFromWishlist(productId);
            });
        });
    }

    async addToCart(productId, quantity = 1) {

        try {
            const product = this.products.get(productId);
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            console.log(`🛒 Adding to cart: ${product.title} (ID: ${productId})`);
            let selectedColor = '';
            let selectedSize = '';
             
            // Check for selected color
            const activeColor = document.querySelector('.color-option.active');
            if (activeColor) {
                selectedColor = activeColor.getAttribute('data-color');
                console.log(`🎨 Selected color: ${selectedColor}`);
            }
            
            // Check for selected size
            const activeSize = document.querySelector('.size-option.active:not(.disabled)');
            if (activeSize) {
                selectedSize = activeSize.getAttribute('data-size');
                console.log(`📏 Selected size: ${selectedSize}`);
            }
        

             console.log(`📏 Selected size: ${selectedSize} and color ${selectedColor}`);

            const response = await fetch(`/builder/cart/add/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity,
                    selected_color: selectedColor,
                    selected_size: selectedSize
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateCartUI(data);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showNotification('Error adding item to cart', 'error');
        }
    }

    async addToWishlist(productId) {
        try {
            const product = this.products.get(productId);
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            console.log(`❤️ Adding to wishlist: ${product.title} (ID: ${productId})`);

            const response = await fetch(`/builder/wishlist/add/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: productId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateCartUI(data);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error adding to wishlist:', error);
            this.showNotification('Error adding item to wishlist', 'error');
        }
    }

    async loadCartData() {
        try {
            const response = await fetch(`/builder/cart/data/${this.subdomain}/`);
            const data = await response.json();
            
            if (data.success !== false) {
                this.updateCartUI(data);
            }
        } catch (error) {
            console.error('Error loading cart data:', error);
        }
    }

    clearCartDisplay() {
        // Clear cart dropdown
        const dropdown = document.getElementById('cart-dropdown');
        if (dropdown) {
            dropdown.innerHTML = '<div class="dropdown-item text-muted">Your cart is empty</div>';
        }

        // Clear cart page items
        document.querySelectorAll('[data-cart-item]').forEach(item => item.remove());
        document.querySelectorAll('[data-cart-item-id]').forEach(item => item.remove());
        
        // Update counters to zero
        this.updateCounters({
            cart_items_count: 0,
            wishlist_count: 0
        });
    }

    updateCounters(data) {
        const cartItemsCount = data.cart_items_count || 0;
        const wishlistCount = data.wishlist_count || 0;

        document.querySelectorAll('.cart-counter').forEach(element => {
            element.textContent = cartItemsCount;
            element.style.display = cartItemsCount > 0 ? 'inline' : 'none';
        });

        document.querySelectorAll('.wishlist-counter').forEach(element => {
            element.textContent = wishlistCount;
            element.style.display = wishlistCount > 0 ? 'inline' : 'none';
        });
    }

    updateCartDropdown(cartItems) {
        const dropdown = document.getElementById('cart-dropdown');
        if (!dropdown) return;

        if (!cartItems || cartItems.length === 0) {
            dropdown.innerHTML = '<div class="dropdown-item text-muted">Your cart is empty</div>';
            return;
        }

        let html = '';
        cartItems.forEach(item => {
            const product = this.products.get(item.product_id.toString());
            html += `
                <div class="dropdown-item d-flex align-items-center">
                    ${item.image_url ? 
                        `<img src="${item.image_url}" alt="${item.title}" class="me-2" style="width: 40px; height: 40px; object-fit: cover;">` 
                        : ''}
                    <div class="flex-grow-1">
                        <div class="fw-bold">${product ? product.title : item.title}</div>
                        <small>$${item.price} x ${item.quantity}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-danger remove-from-cart" 
                            data-product-id="${item.product_id}">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
        });

        html += `
            <div class="dropdown-divider"></div>
            <div class="dropdown-item">
                <a href="/builder/cart/${this.subdomain}/" class="btn btn-primary w-100">
                    View Cart (${cartItems.length})
                </a>
            </div>
        `;

        dropdown.innerHTML = html;

        // Add event listeners to remove buttons
        dropdown.querySelectorAll('.remove-from-cart').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.removeFromCart(button.dataset.productId);
            });
        });
    }

    async removeFromCart(productId) {
        try {
            const response = await fetch(`/builder/cart/remove/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: productId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Item removed from cart', 'success');
                this.updateCartUI(data);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error removing from cart:', error);
            this.showNotification('Error removing item from cart', 'error');
        }
    }

    parsePrice(priceText) {
        if (!priceText) return 0;
        const match = priceText.match(/\$?(\d+\.?\d*)/);
        return match ? parseFloat(match[1]) : 0;
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        document.querySelectorAll('.cart-notification').forEach(n => n.remove());
        
        const notification = document.createElement('div');
        notification.className = `cart-notification alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    // Method to manually add a product (useful for dynamic content)
    addProduct(productData) {
        this.products.set(productData.id.toString(), productData);
        console.log(`📦 Manually added product: ${productData.title}`);
    }

    // Method to get product by ID
    getProduct(productId) {
        return this.products.get(productId.toString());
    }

     async incrementCartItem(productId, amount = 1) {
        try {
            const product = this.products.get(productId);
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            console.log(`➕ Incrementing cart item: ${product.title} by ${amount}`);

            const response = await fetch(`/builder/cart/increment/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: productId,
                    amount: amount
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateCartUI(data);
                this.updateCartItemDisplay(productId, data.item_quantity);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error incrementing cart item:', error);
            this.showNotification('Error updating cart item', 'error');
        }
    }

    async decrementCartItem(productId, amount = 1) {
        try {
            const product = this.products.get(productId);
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            console.log(`➖ Decrementing cart item: ${product.title} by ${amount}`);

            const response = await fetch(`/builder/cart/decrement/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: productId,
                    amount: amount
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateCartUI(data);
                this.updateCartItemDisplay(productId, data.item_quantity);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error decrementing cart item:', error);
            this.showNotification('Error updating cart item', 'error');
        }
    }

    async updateCartItemQuantity(productId, quantity) {
        try {
            const product = this.products.get(productId);
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            console.log(`✏️ Updating cart item: ${product.title} to ${quantity}`);

            const response = await fetch(`/builder/cart/update/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateCartUI(data);
                this.updateCartItemDisplay(productId, data.item_quantity);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error updating cart item:', error);
            this.showNotification('Error updating cart item', 'error');
        }
    }

    async removeFromCart(productId) {
        try {
            const product = this.products.get(productId);
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            console.log(`🗑️ Removing from cart: ${product.title}`);

            const response = await fetch(`/builder/cart/remove/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: productId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateCartUI(data);
                this.removeCartItemDisplay(productId);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error removing from cart:', error);
            this.showNotification('Error removing item from cart', 'error');
        }
    }

    async removeFromWishlist(productId) {
        

        try {
            const product = this.products.get(productId);
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            
            console.log(`🗑️ Removing from wishlist: ${product.title}`);

            const response = await fetch(`/builder/wishlist/remove/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: productId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateCartUI(data);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error removing from wishlist:', error);
            this.showNotification('Error removing item from wishlist', 'error');
        }
    }

   async clearCart() {
        try {
            if (!confirm('Are you sure you want to clear your entire cart?')) {
                return;
            }

            console.log('🧹 Clearing entire cart');

            const response = await fetch(`/builder/cart/clear/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({})
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateCartUI(data);
                this.clearCartDisplay();
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error clearing cart:', error);
            this.showNotification('Error clearing cart', 'error');
        }
    }

    async clearWishlist() {
        try {
            if (!confirm('Are you sure you want to clear your entire wishlist?')) {
                return;
            }

            console.log('🧹 Clearing entire wishlist');

            const response = await fetch(`/builder/wishlist/clear/${this.subdomain}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({})
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateCartUI(data);
                this.clearwishlistDisplay();
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error clearing wishlist:', error);
            this.showNotification('Error clearing wishlist', 'error');
        }
    }

        updateCartUI(data) {
        // Update to show number of ITEMS, not total quantity
        const cartItemsCount = data.cart_items_count || 0; // Number of distinct items
        const wishlistCount = data.wishlist_count || 0;

        // Update cart counters - use cart_items_count instead of cart_total
        document.querySelectorAll('.cart-counter').forEach(element => {
            element.textContent = cartItemsCount;
            element.style.display = cartItemsCount > 0 ? 'inline' : 'none';
        });

        // Update wishlist counters
        document.querySelectorAll('.wishlist-counter').forEach(element => {
            element.textContent = wishlistCount;
            element.style.display = wishlistCount > 0 ? 'inline' : 'none';
        });

        // Update any other counter elements
        document.querySelectorAll('[data-cart-total]').forEach(element => {
            element.textContent = cartItemsCount;
        });

        document.querySelectorAll('[data-wishlist-count]').forEach(element => {
            element.textContent = wishlistCount;
        });

        console.log(`🔄 Counters updated - Cart Items: ${cartItemsCount}, Wishlist: ${wishlistCount}`);
    }




    updateCartItemDisplay(productId, quantity) {
        // Update quantity display in cart dropdown and cart page
        const quantityElement = document.querySelector(`[data-cart-item="${productId}"] .cart-item-quantity`);
        if (quantityElement) {
            quantityElement.textContent = quantity;
        }

        // Update input fields
        const quantityInput = document.querySelector(`[data-cart-item="${productId}"] input[type="number"]`);
        if (quantityInput) {
            quantityInput.value = quantity;
        }

        // Remove item if quantity is 0
        if (quantity === 0) {
            this.removeCartItemDisplay(productId);
        }
    }

    removeCartItemDisplay(productId) {
        // Remove item from cart dropdown
        const cartItem = document.querySelector(`[data-cart-item="${productId}"]`);
        if (cartItem) {
            cartItem.remove();
        }

        // Remove item from cart page
        const cartPageItem = document.querySelector(`[data-cart-item-id="${productId}"]`);
        if (cartPageItem) {
            cartPageItem.remove();
        }
    }

    clearCartDisplay() {
        // Clear cart dropdown
        const dropdown = document.getElementById('cart-dropdown');
        if (dropdown) {
            dropdown.innerHTML = '<div class="dropdown-item text-muted">Your cart is empty</div>';
        }

        // Clear cart page items
        document.querySelectorAll('[data-cart-item]').forEach(item => item.remove());
        document.querySelectorAll('[data-cart-item-id]').forEach(item => item.remove());
    }

    clearwishlistDisplay() {
        // Clear cart dropdown
        const dropdown = document.getElementById('wishlist-dropdown');
        if (dropdown) {
            dropdown.innerHTML = '<div class="dropdown-item text-muted">Your wishlist is empty</div>';
        }

        // Clear cart page items
        document.querySelectorAll('[data-wishlist-item]').forEach(item => item.remove());
        document.querySelectorAll('[data-wishlist-item-id]').forEach(item => item.remove());
    }

    // Add quantity controls to product cards
    addQuantityControls(element, productId) {
        // const controlsContainer = document.createElement('div');
        // controlsContainer.className = 'quantity-controls d-flex align-items-center mt-2';
        // controlsContainer.innerHTML = `
        //     <div class="btn-group btn-group-sm" role="group">
        //         <button type="button" class="btn btn-outline-secondary decrement-quantity" 
        //                 data-product-id="${productId}">
        //             <i class="fas fa-minus"></i>
        //         </button>
        //         <span class="btn btn-outline-primary quantity-display" 
        //               data-product-id="${productId}">1</span>
        //         <button type="button" class="btn btn-outline-secondary increment-quantity" 
        //                 data-product-id="${productId}">
        //             <i class="fas fa-plus"></i>
        //         </button>
        //     </div>
        //     <button class="btn btn-sm btn-primary add-to-cart-with-quantity ms-2" 
        //             data-product-id="${productId}">
        //         <i class="fas fa-cart-plus"></i> Add
        //     </button>
        // `;

        // element.appendChild(controlsContainer);

        // Add event listeners
        controlsContainer.querySelector('.increment-quantity').addEventListener('click', (e) => {
            e.preventDefault();
            this.incrementQuantity(productId);
        });

        controlsContainer.querySelector('.decrement-quantity').addEventListener('click', (e) => {
            e.preventDefault();
            this.decrementQuantity(productId);
        });

        controlsContainer.querySelector('.add-to-cart-with-quantity').addEventListener('click', (e) => {
            e.preventDefault();
            const quantity = parseInt(controlsContainer.querySelector('.quantity-display').textContent);
            this.addToCart(productId, quantity);
        });
    }

    incrementQuantity(productId) {
        const display = document.querySelector(`.quantity-display[data-product-id="${productId}"]`);
        if (display) {
            let quantity = parseInt(display.textContent) + 1;
            display.textContent = quantity;
        }
    }

    decrementQuantity(productId) {
        const display = document.querySelector(`.quantity-display[data-product-id="${productId}"]`);
        if (display) {
            let quantity = parseInt(display.textContent) - 1;
            if (quantity < 1) quantity = 1;
            display.textContent = quantity;
        }
    }

    getSelectedVariants(productId) {
        const product = this.products.get(productId);
        if (!product) return { color: '', size: '' };
        
        let selectedColor = '';
        let selectedSize = '';
        
        // Try to get from active elements first
        const activeColor = document.querySelector('.color-option.active');
        if (activeColor) {
            selectedColor = activeColor.getAttribute('data-color');
        }
        
        const activeSize = document.querySelector('.size-option.active:not(.disabled)');
        if (activeSize) {
            selectedSize = activeSize.getAttribute('data-size');
        }
        
        // Fallback to product stored data
        if (!selectedColor && product.selectedColor) {
            selectedColor = product.selectedColor;
        }
        
        if (!selectedSize && product.selectedSize) {
            selectedSize = product.selectedSize;
        }
        
        return {
            color: selectedColor || '',
            size: selectedSize || ''
        };
    }
}




// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get subdomain from current URL or data attribute
    const subdomain = document.body.dataset.subdomain || 
                     getSubdomainFromHostname();
    
    // Get products data passed from backend
    const productsData = window.productsData || [];
    
    // Initialize cart manager
    window.cartManager = new CartManager(subdomain, {
        autoDiscover: true,
        autoCreateButtons: true
    });
    
    console.log('🛒 Cart Manager initialized for subdomain:', subdomain);
});

function getSubdomainFromHostname() {
    const hostname = window.location.hostname;
    
    if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
        const parts = hostname.split('.');
        if (parts.length > 1 && parts[0] !== 'localhost' && parts[0] !== '127') {
            return parts[0];
        }
    } else {
        const parts = hostname.split('.');
        if (parts.length >= 2) {
            return parts[0];
        }
    }
    
    return 'default';
}