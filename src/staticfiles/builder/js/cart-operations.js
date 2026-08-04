
/* ======================================================
   VARIANT DATA (Injected via Django template loop)
====================================================== */
const VARIANTS = [
    {% for variant in variants %}
    {
        product_id: "{{ variant.product_id }}",
        option1: "{{ variant.option1|escapejs }}",
        cj_vid: "{{ variant.cj_vid }}"
    }{% if not forloop.last %},{% endif %}
    {% endfor %}
];


/* ======================================================
   CART BUTTON HANDLERS
====================================================== */
document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.increment-cart').forEach(btn => {
        btn.addEventListener('click', function () {
            
            window.cartManager?.incrementCartItem(this.dataset.productId, 1);
        });
    });

    document.querySelectorAll('.decrement-cart').forEach(btn => {
        btn.addEventListener('click', function () {
            window.cartManager?.decrementCartItem(this.dataset.productId, 1);
        });
    });

    document.querySelectorAll('.remove-cart-item').forEach(btn => {
        btn.addEventListener('click', function () {
            window.cartManager?.removeFromCart(this.dataset.productId);
        });
    });

    document.getElementById('clearCartBtn')?.addEventListener('click', function () {
        window.cartManager?.clearCart();
    });

});


/* ======================================================
   COLLECT CART DATA
====================================================== */
function getCartData() {

    const items = [];
    let subtotal = 0;

    document.querySelectorAll('.cart-item').forEach(item => {

        const title = item.querySelector('.product-title')?.textContent || '';
        const description = item.querySelector('.product-description')?.textContent || '';
        const price = parseFloat(
            item.querySelector('.product-price')?.textContent.replace('$', '')
        ) || 0;

        const quantity = parseInt(
            item.querySelector('.quantity-input')?.textContent
        ) || 1;

        const selected_color = item.querySelector('.product-color')?.textContent.replace('Color:', '').trim() || '';

        const selected_size = item.querySelector('.product-size')?.textContent.replace('Size:', '').trim() || '';

        const id = item.querySelector('.product-id')?.value;
        const cj_vid = item.querySelector('.cj-vid')?.value || '';

        const total = price * quantity;
        subtotal += total;

        items.push({
            title,
            description,
            id,
            cj_vid,
            price,
            quantity,
            selected_color,
            selected_size,
            total_price: total
        });
    });

    const shipping = subtotal > 0 ? 5.00 : 0;
    const tax = subtotal * 0.08;

    return {
        items,
        subtotal,
        shipping_amount: shipping,
        tax_amount: tax,
        total_amount: subtotal + shipping + tax,
        // is_buy_now: false
    };
}


/* ======================================================
   VARIANT MATCHING (REPLACES cj_vid)
====================================================== */
function resolveVariantCJVID(item) {

    if (!item.selected_color || !item.selected_size) {
        return item.cj_vid;
    }

    const merged = `${item.selected_color}-${item.selected_size}`.toLowerCase();
    const mergedParts = merged.split('-');
    const partCount = mergedParts.length;

    const productVariants = VARIANTS.filter(
        v => String(v.product_id) === String(item.id)
    );

    for (let v of productVariants) {
        if (!v.option1) continue;

        const optionParts = v.option1.toLowerCase().split('-');

        if (
            optionParts.length >= partCount &&
            optionParts.slice(-partCount).join('-') === merged
        ) {
            item.cj_vid = v.cj_vid;
            return item.cj_vid;
        }
    }

    showVariantPopup(item, productVariants);
    throw new Error('Variant not found');
}


/* ======================================================
   SMART AVAILABLE OPTIONS POPUP
====================================================== */
function showVariantPopup(item, variants) {

    const colorSet = new Set();
    const sizeSet = new Set();
    const combinations = [];

    variants.forEach(v => {
        if (!v.option1) return;

        const parts = v.option1.split('-');
        if (parts.length < 2) return;

        const color = parts[parts.length - 2];
        const size = parts[parts.length - 1];

        colorSet.add(color);
        sizeSet.add(size);
        combinations.push(`${color}-${size}`);
    });

    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position:fixed;
        inset:0;
        background:rgba(0,0,0,.45);
        z-index:9998;
    `;

    const modal = document.createElement('div');
    modal.style.cssText = `
        position:fixed;
        top:50%;
        left:50%;
        transform:translate(-50%,-50%);
        background:#fff;
        border-radius:14px;
        padding:22px;
        width:90%;
        max-width:440px;
        box-shadow:0 20px 60px rgba(0,0,0,.25);
        z-index:9999;
        font-family:system-ui;
    `;

    modal.innerHTML = `
        <h3 style="margin-top:0">Variant Not Available</h3>
        <p>
            No match for
            <strong>${item.selected_color}-${item.selected_size}</strong>
        </p>

        <p><strong>Available Colors:</strong><br>
            ${Array.from(colorSet).join(', ')}
        </p>

        <p><strong>Available Sizes:</strong><br>
            ${Array.from(sizeSet).join(', ')}
        </p>

        <p><strong>Valid Combinations:</strong></p>
        <div style="max-height:120px; overflow:auto;">
            ${combinations.join('<br>')}
        </div>

        <button id="closeVariantPopup"
            style="
                margin-top:16px;
                padding:10px 18px;
                background:#111;
                color:#fff;
                border:none;
                border-radius:8px;
                cursor:pointer;">
            Close
        </button>
    `;

    modal.querySelector('#closeVariantPopup').onclick = () => {
        overlay.remove();
        modal.remove();
    };

    document.body.appendChild(overlay);
    document.body.appendChild(modal);
}


/* ======================================================
   CHECKOUT REDIRECT
====================================================== */
function redirectCartToPaymentSelection() {

    const cartData = getCartData();

    if (!cartData.items.length) {
        alert('Your cart is empty');
        return;
    }

    try {
        cartData.items.forEach(item => {
            resolveVariantCJVID(item);
        });
    } catch {
        return;
    }

    // redirectToPayment(cartData)

    const hostname = window.location.hostname;
    const page_domain = document.getElementById('page-subdomain').value;

    const subdomain = hostname.includes('localhost')
        ? page_domain
        : hostname.split('.')[0];

    const params = new URLSearchParams({
        type: 'cart',
        cart: JSON.stringify(cartData)
    });

    window.location.href =
        `/payments/select-payment/${subdomain}/?${params.toString()}`;
}
