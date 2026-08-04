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
        
        this.collectProductData();
        this.setupCartIcon();
        this.initializeButtons();
        this.initializeVariantSelection();
        
        await this.loadCartData();
        
        console.log(`📦 Cart Manager ready with ${this.products.size} products`);
    }

    // ======================================================
    // FIXED: Collect product data from product details page
    // ======================================================
    collectProductData() {
        var self = this;
        
        // Method 1: Collect from product details container
        var productContainer = document.querySelector('.product-container') || 
                               document.querySelector('[data-product-id]');
        
        if (productContainer) {
            var productId = productContainer.dataset.productId || 
                           productContainer.getAttribute('data-product-id');
            
            if (productId) {
                var titleEl = document.querySelector('.product-title') || 
                              document.querySelector('h1');
                var priceEl = document.querySelector('.product-price') || 
                              document.querySelector('[data-product-price]');
                var imageEl = document.getElementById('mainProductImage') || 
                              document.querySelector('.main-image img') ||
                              document.querySelector('#main-product-image');
                
                var productData = {
                    id: productId,
                    title: titleEl ? titleEl.textContent.trim() : 'Product',
                    price: self.parsePrice(priceEl ? priceEl.textContent : ''),
                    image: imageEl ? imageEl.src : null,
                    element: productContainer,
                    isProductDetails: true,
                    hasVariants: productContainer.dataset.hasVariants === 'true' || false,
                    availableColors: productContainer.dataset.availableColors || '',
                    availableSizes: productContainer.dataset.availableSizes || ''
                };
                
                if (productContainer.dataset.productPrice) {
                    productData.price = parseFloat(productContainer.dataset.productPrice) || productData.price;
                }
                
                self.products.set(productId.toString(), productData);
                console.log('📦 Collected product details:', productData.title, '(ID:', productId + ')');
            }
        }
        
        // Method 2: Collect from product cards with data attributes
        var productElements = document.querySelectorAll('[data-product-id]');
        productElements.forEach(function(element) {
            var pid = element.dataset.productId;
            if (self.products.has(pid)) return;
            
            var productData = {
                id: pid,
                title: element.dataset.productTitle || 
                      (element.querySelector('[data-product-title]') ? element.querySelector('[data-product-title]').textContent : 'Product'),
                price: parseFloat(element.dataset.productPrice) || 
                      self.parsePrice(element.querySelector('[data-product-price]') ? element.querySelector('[data-product-price]').textContent : '') || 
                      0,
                image: element.dataset.productImage || 
                      (element.querySelector('[data-product-image]') ? element.querySelector('[data-product-image]').src : null),
                element: element,
                hasVariants: element.dataset.hasVariants === 'true' || false,
                availableColors: element.dataset.availableColors || '',
                availableSizes: element.dataset.availableSizes || ''
            };
            
            self.products.set(pid, productData);
            console.log('📦 Collected product:', productData.title, '(ID:', pid + ')');
        });

        // Method 3: Collect from backend data passed via JavaScript
        if (window.productsData) {
            window.productsData.forEach(function(product) {
                var pid = product.id.toString();
                if (self.products.has(pid)) return;
                
                self.products.set(pid, {
                    id: pid,
                    title: product.title || product.name || 'Product',
                    price: parseFloat(product.price) || 0,
                    image: product.image_url || product.main_image || null,
                    element: null,
                    hasVariants: product.hasVariants || (product.variants && product.variants.length > 0) || false,
                    availableColors: product.availableColors || '',
                    availableSizes: product.availableSizes || ''
                });
            });
            console.log('📦 Loaded', window.productsData.length, 'products from backend data');
        }
        
        // Method 4: Look for product data in script variables
        if (window.productData) {
            var p = window.productData;
            var pid = p.id.toString();
            if (!self.products.has(pid)) {
                self.products.set(pid, {
                    id: pid,
                    title: p.title || p.name || 'Product',
                    price: parseFloat(p.price) || 0,
                    image: p.image || p.main_image || null,
                    element: null,
                    hasVariants: p.variants && p.variants.length > 0,
                    availableColors: '',
                    availableSizes: ''
                });
                console.log('📦 Loaded product from window.productData:', p.title);
            }
        }
        
        // If no products found, try to create one from the page
        if (self.products.size === 0) {
            self.createProductFromPage();
        }
    }
    
    // ======================================================
    // FIXED: Create product from page if no data found
    // ======================================================
    createProductFromPage() {
        var self = this;
        var productId = self.getProductIdFromPage();
        if (!productId) return;
        
        var titleEl = document.querySelector('.product-title') || document.querySelector('h1');
        var priceEl = document.querySelector('.product-price') || document.querySelector('[data-product-price]');
        var imageEl = document.getElementById('mainProductImage') || document.querySelector('.main-image img');
        
        var productData = {
            id: productId,
            title: titleEl ? titleEl.textContent.trim() : 'Product',
            price: self.parsePrice(priceEl ? priceEl.textContent : ''),
            image: imageEl ? imageEl.src : null,
            element: document.querySelector('.product-container') || document.body,
            isProductDetails: true,
            hasVariants: false,
            availableColors: '',
            availableSizes: ''
        };
        
        self.products.set(productId.toString(), productData);
        console.log('📦 Created product from page:', productData.title, '(ID:', productId + ')');
    }
    
    // ======================================================
    // FIXED: Get product ID from page
    // ======================================================
    getProductIdFromPage() {
        var container = document.querySelector('[data-product-id]');
        if (container && container.dataset.productId) {
            return container.dataset.productId;
        }
        
        if (window.productData && window.productData.id) {
            return window.productData.id;
        }
        
        var path = window.location.pathname;
        var match = path.match(/\/product\/(\d+)/);
        if (match) {
            return match[1];
        }
        
        var productIdEl = document.querySelector('[data-product-id]');
        if (productIdEl) {
            return productIdEl.getAttribute('data-product-id');
        }
        
        return null;
    }

    // ======================================================
    // FIXED: Parse price from various formats
    // ======================================================
    parsePrice(priceText) {
        if (!priceText) return 0;
        var cleaned = priceText.replace(/[^\d.]/g, '');
        var match = cleaned.match(/(\d+\.?\d*)/);
        return match ? parseFloat(match[1]) : 0;
    }

    // ======================================================
    // FIXED: Get selected variants from the page
    // ======================================================
    getSelectedVariants(productId) {
        var product = this.products.get(productId);
        if (!product) return { color: '', size: '', options: {} };
        
        var selectedColor = '';
        var selectedSize = '';
        var selectedOptions = {};
        
        // Check for dynamic variant system
        var variantContainer = document.getElementById('variant-attributes-container');
        if (variantContainer) {
            var activeVariants = variantContainer.querySelectorAll('.active');
            activeVariants.forEach(function(el) {
                var parentSection = el.closest('[data-attribute]');
                var attrName = parentSection ? parentSection.getAttribute('data-attribute') : null;
                var value = el.getAttribute('data-value');
                if (attrName && value) {
                    selectedOptions[attrName] = value;
                    if (isColorAttribute(attrName)) {
                        selectedColor = value;
                    } else {
                        selectedSize = value;
                    }
                }
            });
        }
        
        // Try to get from variant selections state
        if (window.variantSelections && window.variantSelections[productId]) {
            var selections = window.variantSelections[productId];
            for (var key in selections) {
                if (selections[key]) {
                    selectedOptions[key] = selections[key];
                    if (isColorAttribute(key)) {
                        selectedColor = selections[key];
                    } else {
                        selectedSize = selections[key];
                    }
                }
            }
        }
        
        return {
            color: selectedColor || '',
            size: selectedSize || '',
            options: selectedOptions
        };
    }

    // ======================================================
    // FIXED: Add to cart with variant support
    // ======================================================
    async addToCart(productId, quantity = 1) {
        try {
            var product = this.products.get(productId.toString());
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            console.log('🛒 Adding to cart:', product.title, '(ID:', productId + ')');
            
            var variants = this.getSelectedVariants(productId);
            var selectedColor = variants.color;
            var selectedSize = variants.size;
            var selectedOptions = variants.options;
            
            var requestData = {
                product_id: parseInt(productId),
                quantity: quantity || 1,
                selected_color: selectedColor,
                selected_size: selectedSize
            };
            
            if (selectedOptions && Object.keys(selectedOptions).length > 0) {
                requestData.selected_options = selectedOptions;
            }

            var response = await fetch('/builder/cart/add/' + this.subdomain + '/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(requestData)
            });

            var data = await response.json();

            if (data.success) {
                this.showNotification(data.message || 'Added to cart!', 'success');
                this.updateCartUI(data);
                await this.loadCartData();
            } else {
                this.showNotification(data.error || 'Error adding to cart', 'error');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showNotification('Error adding item to cart', 'error');
        }
    }

    // ======================================================
    // FIXED: Add to wishlist
    // ======================================================
    async addToWishlist(productId) {
        try {
            var product = this.products.get(productId.toString());
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            console.log('❤️ Adding to wishlist:', product.title);

            var response = await fetch('/builder/wishlist/add/' + this.subdomain + '/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: parseInt(productId)
                })
            });

            var data = await response.json();

            if (data.success) {
                this.showNotification(data.message || 'Added to wishlist!', 'success');
                this.updateCartUI(data);
            } else {
                this.showNotification(data.error || 'Error adding to wishlist', 'error');
            }
        } catch (error) {
            console.error('Error adding to wishlist:', error);
            this.showNotification('Error adding item to wishlist', 'error');
        }
    }

    // ======================================================
    // FIXED: Remove from wishlist
    // ======================================================
    async removeFromWishlist(productId) {
        try {
            var product = this.products.get(productId.toString());
            if (!product) {
                this.showNotification('Product not found', 'error');
                return;
            }

            console.log('🗑️ Removing from wishlist:', product.title);

            var response = await fetch('/builder/wishlist/remove/' + this.subdomain + '/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: parseInt(productId)
                })
            });

            var data = await response.json();

            if (data.success) {
                this.showNotification(data.message || 'Removed from wishlist', 'success');
                this.updateCartUI(data);
            } else {
                this.showNotification(data.error || 'Error removing from wishlist', 'error');
            }
        } catch (error) {
            console.error('Error removing from wishlist:', error);
            this.showNotification('Error removing item from wishlist', 'error');
        }
    }

    // ======================================================
    // FIXED: Load cart data
    // ======================================================
    async loadCartData() {
        try {
            var response = await fetch('/builder/cart/data/' + this.subdomain + '/');
            var data = await response.json();
            
            if (data.success !== false) {
                this.updateCartUI(data);
            }
        } catch (error) {
            console.error('Error loading cart data:', error);
        }
    }

    // ======================================================
    // FIXED: Update cart UI
    // ======================================================
    updateCartUI(data) {
        var cartItemsCount = data.cart_items_count || 0;
        var wishlistCount = data.wishlist_count || 0;

        document.querySelectorAll('.cart-counter').forEach(function(element) {
            element.textContent = cartItemsCount;
            element.style.display = cartItemsCount > 0 ? 'inline' : 'none';
        });

        document.querySelectorAll('.wishlist-counter').forEach(function(element) {
            element.textContent = wishlistCount;
            element.style.display = wishlistCount > 0 ? 'inline' : 'none';
        });

        document.querySelectorAll('.cart-badge').forEach(function(element) {
            element.textContent = cartItemsCount;
        });

        console.log('🔄 Counters updated - Cart Items:', cartItemsCount, 'Wishlist:', wishlistCount);
    }

    // ======================================================
    // FIXED: Remove from cart
    // ======================================================
    async removeFromCart(productId) {
        try {
            var response = await fetch('/builder/cart/remove/' + this.subdomain + '/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    product_id: parseInt(productId)
                })
            });

            var data = await response.json();

            if (data.success) {
                this.showNotification('Item removed from cart', 'success');
                this.updateCartUI(data);
                await this.loadCartData();
            } else {
                this.showNotification(data.error || 'Error removing from cart', 'error');
            }
        } catch (error) {
            console.error('Error removing from cart:', error);
            this.showNotification('Error removing item from cart', 'error');
        }
    }

    // ======================================================
    // FIXED: Initialize variant selection
    // ======================================================
    initializeVariantSelection() {
        var self = this;
        
        document.querySelectorAll('.color-option').forEach(function(option) {
            option.addEventListener('click', function() {
                var parent = this.closest('.variant-options');
                if (parent) {
                    parent.querySelectorAll('.color-option').forEach(function(c) {
                        c.classList.remove('active');
                    });
                }
                this.classList.add('active');
                var selectedColor = this.getAttribute('data-color');
                console.log('🎨 Selected color:', selectedColor);
            });
        });
        
        document.querySelectorAll('.size-option:not(.disabled), .variant-btn:not(.disabled)').forEach(function(option) {
            option.addEventListener('click', function() {
                var parent = this.closest('.variant-options') || this.closest('.size-options');
                if (parent) {
                    parent.querySelectorAll('.size-option, .variant-btn').forEach(function(s) {
                        s.classList.remove('active');
                    });
                }
                this.classList.add('active');
                var selectedSize = this.getAttribute('data-size') || this.textContent.trim();
                console.log('📏 Selected size:', selectedSize);
            });
        });
        
        var variantContainer = document.getElementById('variant-attributes-container');
        if (variantContainer) {
            variantContainer.addEventListener('click', function(e) {
                var target = e.target.closest('.color-option, .variant-btn');
                if (target) {
                    var parent = target.closest('.variant-options');
                    if (parent) {
                        parent.querySelectorAll('.color-option, .variant-btn').forEach(function(el) {
                            el.classList.remove('active');
                        });
                    }
                    target.classList.add('active');
                }
            });
        }
    }

    // ======================================================
    // FIXED: Initialize buttons
    // ======================================================
    initializeButtons() {
        var self = this;
        
        document.querySelectorAll('[data-add-to-cart]').forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                var productId = this.dataset.addToCart;
                var quantity = parseInt(this.dataset.quantity) || 1;
                self.addToCart(productId, quantity);
            });
        });

        document.querySelectorAll('[data-add-to-wishlist]').forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                var productId = this.dataset.addToWishlist;
                self.addToWishlist(productId);
            });
        });

        document.querySelectorAll('[data-remove-from-wishlist]').forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                var productId = this.dataset.removeFromWishlist;
                self.removeFromWishlist(productId);
            });
        });
    }

    // ======================================================
    // FIXED: Setup cart icon
    // ======================================================
    setupCartIcon() {
        var cartBadge = document.querySelector('.cart-badge') || 
                        document.querySelector('.cart-counter');
        if (!cartBadge) {
            var nav = document.querySelector('nav');
            if (nav) {
                var cartIcon = document.createElement('span');
                cartIcon.className = 'cart-counter';
                cartIcon.style.cssText = 'display:none; background:red; color:white; border-radius:50%; padding:2px 8px; font-size:12px; margin-left:5px;';
                nav.appendChild(cartIcon);
            }
        }
    }

    // ======================================================
    // FIXED: Show notification
    // ======================================================
    showNotification(message, type) {
        var isSuccess = type === 'success';
        document.querySelectorAll('.cart-notification').forEach(function(n) {
            n.remove();
        });
        
        var notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.style.cssText = 
            'position: fixed; top: 100px; right: 20px; ' +
            'background: ' + (isSuccess ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8') + '; ' +
            'color: white; ' +
            'padding: 12px 20px; border-radius: 8px; z-index: 10000; ' +
            'animation: slideInRight 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.15); ' +
            'font-weight: 600; font-size: 14px; min-width: 250px;';
        notification.innerHTML = 
            '<i class="fas ' + (isSuccess ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle') + '" style="margin-right: 8px;"></i> ' + message;
        document.body.appendChild(notification);
        
        setTimeout(function() {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                notification.style.transition = 'opacity 0.3s';
                setTimeout(function() {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 3000);
    }

    // ======================================================
    // FIXED: Get CSRF token
    // ======================================================
    getCSRFToken() {
        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    // ======================================================
    // FIXED: Add product manually
    // ======================================================
    addProduct(productData) {
        this.products.set(productData.id.toString(), productData);
        console.log('📦 Manually added product:', productData.title);
    }

    // ======================================================
    // FIXED: Get product by ID
    // ======================================================
    getProduct(productId) {
        return this.products.get(productId.toString());
    }
}

// ======================================================
// FIXED: Helper function to check if attribute is color
// ======================================================
function isColorAttribute(attrName) {
    var colorKeywords = ['color', 'colour', 'shade', 'tone', 'hue', 'pigment'];
    var lowerName = attrName.toLowerCase();
    for (var i = 0; i < colorKeywords.length; i++) {
        if (lowerName.indexOf(colorKeywords[i]) !== -1) {
            return true;
        }
    }
    return false;
}

// ======================================================
// FIXED: Auto-initialize when DOM is loaded
// ======================================================
document.addEventListener('DOMContentLoaded', function() {
    if (window.cartManager) {
        console.log('🛒 Cart Manager already initialized');
        return;
    }
    
    var subdomain = document.body.dataset.subdomain || 
                    document.body.dataset.pageSubdomain ||
                    getSubdomainFromHostname();
    
    window.cartManager = new CartManager(subdomain, {
        autoDiscover: true,
        autoCreateButtons: true
    });
    
    console.log('🛒 Cart Manager initialized for subdomain:', subdomain);
});

function getSubdomainFromHostname() {
    var hostname = window.location.hostname;
    
    if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
        var parts = hostname.split('.');
        if (parts.length > 1 && parts[0] !== 'localhost' && parts[0] !== '127') {
            return parts[0];
        }
    } else {
        var parts = hostname.split('.');
        if (parts.length >= 2) {
            return parts[0];
        }
    }
    
    return 'default';
}