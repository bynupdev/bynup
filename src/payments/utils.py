# payments/utils.py

import logging

logger = logging.getLogger(__name__)

def check_and_deduct_stock(page, items):
    """
    Validates stock and deducts BEFORE order creation.
    Returns (success, error_message)
    """
    from builder.models import Product
    
    print("\n" + "="*60)
    print("🔍 STOCK VALIDATION DEBUG")
    print("="*60)
    print(f"Page: {page.brand_name} (ID: {page.id})")
    print(f"Items to check: {len(items)}")
    print("-"*60)
    
    # First pass: validate everything
    for i, item in enumerate(items, 1):
        product_id = item.get('product_id') or item.get('id')  # Try both keys
        
        # If still no product_id, check if item itself is the ID
        if not product_id and isinstance(item, (int, str)):
            product_id = item
            
        quantity = item.get('quantity', 1) if isinstance(item, dict) else 1
        
        print(f"\n📦 Item {i}:")
        print(f"   Raw item data: {item}")
        print(f"   Product ID: {product_id}")
        print(f"   Requested Quantity: {quantity}")
        
        if not product_id:
            print(f"   ❌ NO PRODUCT ID FOUND - Cannot validate!")
            print("="*60)
            print("❌ VALIDATION FAILED - Missing product ID")
            print("="*60 + "\n")
            return False, "Product information is missing or invalid"
        
        try:
            product = Product.objects.filter(page=page, id=product_id).first()
        except Exception as e:
            print(f"   ❌ Error fetching product: {e}")
            return False, f"Error checking product: {e}"
        
        if not product:
            print(f"   ❌ Product ID {product_id} not found in database")
            print("="*60)
            print("❌ VALIDATION FAILED - Product not found")
            print("="*60 + "\n")
            return False, f"Product with ID {product_id} not found"
        
        print(f"   Product Title: {product.title}")
        print(f"   Current Stock: {product.quantity}")
        print(f"   Track Quantity: {product.track_quantity}")
        print(f"   Allow Backorders: {product.allow_backorders}")
        print(f"   Status: {product.status}")
        
        # Check conditions
        if product.track_quantity:
            print(f"   ✅ Product tracks inventory")
            
            if not product.allow_backorders:
                print(f"   ✅ Backorders NOT allowed")
                
                if product.quantity < quantity:
                    print(f"   ❌ INSUFFICIENT STOCK! Have: {product.quantity}, Need: {quantity}")
                    print("="*60)
                    print("❌ VALIDATION FAILED - Order BLOCKED")
                    print("="*60 + "\n")
                    return False, f"'{product.title}' has insufficient stock. Available: {product.quantity}, Requested: {quantity}"
                else:
                    print(f"   ✅ Sufficient stock: {product.quantity} >= {quantity}")
            else:
                print(f"   ℹ️ Backorders allowed - skipping stock check")
        else:
            print(f"   ℹ️ Does not track inventory - skipping stock check")
    
    print("\n" + "-"*60)
    print("✅ ALL STOCK CHECKS PASSED - Proceeding with deduction")
    print("-"*60)
    
    # Second pass: deduct stock
    for i, item in enumerate(items, 1):
        product_id = item.get('product_id') or item.get('id')
        if not product_id and isinstance(item, (int, str)):
            product_id = item
            
        quantity = item.get('quantity', 1) if isinstance(item, dict) else 1
        
        product = Product.objects.filter(page=page, id=product_id).first()
        
        if product and product.track_quantity:
            old_quantity = product.quantity
            product.quantity -= quantity
            
            if product.quantity <= 0 and not product.allow_backorders:
                old_status = product.status
                product.status = 'out_of_stock'
                print(f"\n📦 Item {i}: {product.title}")
                print(f"   Stock: {old_quantity} → {product.quantity}")
                print(f"   Status: {old_status} → {product.status}")
            else:
                print(f"\n📦 Item {i}: {product.title}")
                print(f"   Stock: {old_quantity} → {product.quantity}")
            
            product.save()
    
    print("\n" + "="*60)
    print("✅ STOCK DEDUCTED SUCCESSFULLY")
    print("="*60 + "\n")
    
    return True, None