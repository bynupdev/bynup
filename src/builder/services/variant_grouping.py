# builder/services/variant_grouping.py

import hashlib
import requests
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class VariantGroupingService:
    """
    Handles variant grouping and creates products from groups.
    Each created product gets its own variants from the group.
    """
    
    def __init__(self, product):
        self.product = product
        self.display_mode = self._get_or_create_display_mode()
    
    def _get_or_create_display_mode(self):
        from builder.models import ProductDisplayMode
        mode, created = ProductDisplayMode.objects.get_or_create(
            product=self.product,
            defaults={'mode': 'single', 'group_by': 'image'}
        )
        return mode
    
    def process_and_create_products(self):
        """
        Main method: Process variants and create product records from groups.
        Each group becomes a product with its own variants.
        """
        variants = self.product.variants.all()
        
        if not variants:
            return {
                'success': False,
                'error': 'No variants found for this product'
            }
        
        # Clean up existing grouped products
        from builder.models import GroupedProduct
        existing_groups = GroupedProduct.objects.filter(original_product=self.product)
        
        for group in existing_groups:
            if group.product:
                # Delete the product and its variants
                try:
                    # Delete variants first
                    group.product.variants.all().delete()
                    group.product.delete()
                except Exception as e:
                    logger.warning(f"Could not delete product {group.product.id}: {e}")
            group.delete()
        
        # Determine grouping mode and create products
        if self.display_mode.mode == 'flattened':
            result = self._create_products_from_flattened(variants)
        elif self.display_mode.mode == 'single':
            result = self._create_products_from_single(variants)
        else:  # grouped
            result = self._create_products_from_groups(variants)
        
        # Deactivate original product if products were created
        if result.get('success') and result.get('created_count', 0) > 0:
            self.product.status = 'archived'
            self.product.is_active = False
            self.product.save()
            logger.info(f"Original product {self.product.id} deactivated")
        
        return result
    
    def _create_products_from_flattened(self, variants):
        """Create one product per variant, each with its own variant"""
        created_products = []
        errors = []
        
        for variant in variants:
            try:
                # Create product from this variant
                product = self._create_product_from_variant(
                    variant, 
                    f"variant_{variant.id}",
                    display_name=self._get_variant_display_name(variant),
                    variant_ids=[variant.id],
                    is_flattened=True
                )
                if product:
                    created_products.append(product.id)
                else:
                    errors.append(f"Failed to create product for variant {variant.id}")
            except Exception as e:
                errors.append(f"Error creating product for variant {variant.id}: {str(e)}")
        
        return {
            'success': len(created_products) > 0,
            'mode': 'flattened',
            'created_count': len(created_products),
            'product_ids': created_products,
            'errors': errors,
            'message': f'Created {len(created_products)} products from variants' + 
                      (f' ({len(errors)} errors)' if errors else '')
        }
    
    def _create_products_from_single(self, variants):
        """Create one product with all variants as its variants"""
        # Create a single product that represents all variants
        display_name = self.product.title
        
        # Get the first variant for pricing
        first_variant = variants.first()
        prices = [v.price for v in variants if v.price]
        
        product = self._create_product_from_variant(
            first_variant, 
            'all',
            display_name=display_name,
            variant_ids=[v.id for v in variants],
            is_single_mode=True
        )
        
        if product:
            return {
                'success': True,
                'mode': 'single',
                'created_count': 1,
                'product_ids': [product.id],
                'errors': [],
                'message': f'Created single product with {len(variants)} variants'
            }
        
        return {
            'success': False,
            'error': 'Failed to create single product',
            'created_count': 0,
            'product_ids': [],
            'errors': ['Failed to create product']
        }
    
    def _create_products_from_groups(self, variants):
        """Create products from groups (by image or attribute)"""
        # Detect groups based on mode
        if self.display_mode.group_by == 'image':
            groups = self._group_by_image(variants)
        else:
            groups = self._group_by_primary_attribute(variants)
        
        created_products = []
        errors = []
        
        for group_key, group_variants in groups.items():
            if not group_variants:
                continue
                
            try:
                # Get the first variant as representative
                first_variant = group_variants[0]
                
                # Generate display name
                display_name = self._get_group_display_name(group_variants)
                
                # Get variant IDs
                variant_ids = [v.id for v in group_variants]
                
                # Create product from this group
                product = self._create_product_from_variant(
                    first_variant,
                    group_key,
                    display_name=display_name,
                    variant_ids=variant_ids,
                    is_grouped=True
                )
                
                if product:
                    created_products.append(product.id)
                else:
                    errors.append(f"Failed to create product for group: {display_name}")
            except Exception as e:
                errors.append(f"Error creating group {group_key}: {str(e)}")
        
        return {
            'success': len(created_products) > 0,
            'mode': 'grouped',
            'group_by': self.display_mode.group_by,
            'created_count': len(created_products),
            'product_ids': created_products,
            'errors': errors,
            'message': f'Created {len(created_products)} products from groups' +
                      (f' ({len(errors)} errors)' if errors else '')
        }
    
    # builder/services/variant_grouping.py

    def _create_product_from_variant(self, variant, group_key, display_name=None, 
                                    variant_ids=None, is_grouped=False, 
                                    is_single_mode=False, is_flattened=False):
        """
        Create a product from a variant or group of variants.
        FIXED: Properly saves the variant image as the main product image.
        """
        from builder.models import Product, ProductVariant, ProductInventory, GroupedProduct
        from django.core.files.base import ContentFile
        from django.core.files import File
        import time
        import random
        
        try:
            with transaction.atomic():
                # Generate a unique slug
                base_slug = slugify(display_name or self.product.title)
                slug = base_slug
                counter = 1
                while Product.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                # Get all variants in this group
                if variant_ids:
                    group_variants = list(ProductVariant.objects.filter(id__in=variant_ids))
                else:
                    group_variants = [variant]
                
                # Get the first variant as the primary
                first_variant = group_variants[0] if group_variants else variant
                
                # Calculate price (min price from variants)
                prices = [float(v.price) for v in group_variants if v.price]
                price = min(prices) if prices else float(self.product.price or 0)
                
                # Get CJ VID (first variant with CJ VID)
                cj_vid = None
                for v in group_variants:
                    if v.cj_vid:
                        cj_vid = v.cj_vid
                        break
                
                # Calculate total quantity
                total_quantity = sum(v.quantity or 0 for v in group_variants)
                
                # Generate unique SKU for the product
                base_sku = first_variant.sku if first_variant and first_variant.sku else f"GP-{self.product.id}"
                timestamp = int(time.time()) % 1000000
                random_suffix = random.randint(100, 999)
                unique_sku = f"{base_sku}-{group_key[:6]}-{timestamp}-{random_suffix}"
                if len(unique_sku) > 100:
                    unique_sku = unique_sku[:100]
                
                # ========== CREATE THE PRODUCT ==========
                product = Product.objects.create(
                    page=self.product.page,
                    title=f"{self.product.title} - {display_name}" if display_name else self.product.title,
                    slug=slug,
                    description=self.product.description or '',
                    short_description=self.product.short_description or '',
                    category=self.product.category,
                    price=Decimal(str(price)),
                    compare_at_price=self.product.compare_at_price,
                    status='active',
                    is_active=True,
                    cj_vid=cj_vid,
                    cj_pid=self.product.cj_pid,
                    colors=self.product.colors,
                    sizes=self.product.sizes,
                    has_variants=len(group_variants) > 1,
                    quantity=total_quantity,
                    track_quantity=True,
                    weight=self.product.weight,
                    requires_shipping=self.product.requires_shipping,
                    free_shipping=self.product.free_shipping,
                    meta_title=f"{self.product.title} - {display_name}" if display_name else self.product.title,
                    meta_description=self.product.meta_description or '',
                    vendor=self.product.vendor,
                    collection=self.product.collection,
                    tags=self.product.tags or [],
                    visible_on_store=True,
                    featured=False,
                    sku=unique_sku,
                    use_custom_shipping=self.product.use_custom_shipping,
                    custom_shipping_type=self.product.custom_shipping_type,
                    custom_shipping_price=self.product.custom_shipping_price,
                    shipping_per_item=self.product.shipping_per_item,
                    ships_separately=self.product.ships_separately,
                    shipping_note=self.product.shipping_note,
                    image_url=self.product.image_url,
                )
                
                # ============================================================
                # ========== SAVE THE MAIN PRODUCT IMAGE FROM VARIANT ==========
                # ============================================================
                print(f"\n📸 Saving main image for product: {product.title}")
                
                # Try multiple sources for the image
                image_source = None
                image_url = None
                
                # 1. Try the first variant's image
                if first_variant and first_variant.image:
                    image_source = first_variant.image
                    if hasattr(first_variant.image, 'url'):
                        image_url = first_variant.image.url
                        print(f"   Found image in first variant: {image_url}")
                
                # 2. Try any variant in the group with an image
                if not image_source:
                    for v in group_variants:
                        if v.image:
                            image_source = v.image
                            if hasattr(v.image, 'url'):
                                image_url = v.image.url
                                print(f"   Found image in variant {v.id}: {image_url}")
                            break
                
                # 3. Try the original product's main image
                if not image_source and self.product.main_image:
                    image_source = self.product.main_image
                    if hasattr(self.product.main_image, 'url'):
                        image_url = self.product.main_image.url
                        print(f"   Using original product image: {image_url}")
                
                # Save the image if we found one
                if image_source and image_url:
                    try:
                        print(f"   Downloading image from: {image_url}")
                        
                        # Download the image
                        response = requests.get(image_url, timeout=15, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        
                        if response.status_code == 200:
                            # Determine file extension from URL or content-type
                            content_type = response.headers.get('content-type', '')
                            if 'jpeg' in content_type or 'jpg' in content_type:
                                ext = 'jpg'
                            elif 'png' in content_type:
                                ext = 'png'
                            elif 'webp' in content_type:
                                ext = 'webp'
                            else:
                                # Try to get from URL
                                url_parts = image_url.split('.')
                                ext = url_parts[-1].split('?')[0] if len(url_parts) > 1 else 'jpg'
                                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                    ext = 'jpg'
                            
                            # Generate filename
                            file_name = f"group_{product.id}_{group_key[:6]}.{ext}"
                            
                            # Save the image - THIS IS THE KEY PART
                            product.main_image.save(file_name, ContentFile(response.content), save=True)
                            print(f"   ✅ Main image saved successfully: {file_name}")
                            
                            # Also save as gallery image
                            try:
                                from builder.models import ProductImages
                                gallery_img = ProductImages.objects.create(
                                    product=product,
                                    image=product.main_image
                                )
                                print(f"   ✅ Gallery image saved")
                            except Exception as e:
                                print(f"   ⚠️ Could not save gallery image: {e}")
                            
                        else:
                            print(f"   ⚠️ Failed to download image: HTTP {response.status_code}")
                            
                    except requests.exceptions.Timeout:
                        print(f"   ⚠️ Timeout downloading image from {image_url}")
                    except requests.exceptions.RequestException as e:
                        print(f"   ⚠️ Request error downloading image: {e}")
                    except Exception as e:
                        print(f"   ⚠️ Error saving main image: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"   ⚠️ No image found for product")
                
                # ============================================================
                # ========== CREATE INVENTORY ==========
                # ============================================================
                inventory, _ = ProductInventory.objects.get_or_create(
                    sku=unique_sku,
                    defaults={
                        'quantity': total_quantity,
                        'track_quantity': True,
                        'low_stock_threshold': 5,
                        'allow_backorders': False,
                    }
                )
                product.inventory = inventory
                product.save()
                
                # ============================================================
                # ========== CREATE VARIANTS WITH UNIQUE SKUS ==========
                # ============================================================
                created_variants = []
                
                for idx, original_variant in enumerate(group_variants):
                    # Generate UNIQUE SKU for this variant
                    variant_sku = original_variant.sku or f"VAR-{product.id}"
                    variant_sku = f"{variant_sku}-{group_key[:4]}-{idx}-{int(time.time()) % 10000}"
                    if len(variant_sku) > 100:
                        variant_sku = variant_sku[:100]
                    
                    # Check if SKU already exists
                    while ProductVariant.objects.filter(sku=variant_sku).exists():
                        variant_sku = f"{variant_sku}-{random.randint(10, 99)}"
                        if len(variant_sku) > 100:
                            variant_sku = variant_sku[:100]
                    
                    # Create the variant
                    new_variant = ProductVariant.objects.create(
                        product=product,
                        options=original_variant.options.copy() if original_variant.options else {},
                        sku=variant_sku,
                        barcode=original_variant.barcode,
                        option1=original_variant.option1,
                        option2=original_variant.option2,
                        option3=original_variant.option3,
                        price=original_variant.price,
                        compare_at_price=original_variant.compare_at_price,
                        cost_per_item=original_variant.cost_per_item,
                        quantity=original_variant.quantity,
                        track_quantity=original_variant.track_quantity,
                        low_stock_threshold=original_variant.low_stock_threshold,
                        weight=original_variant.weight,
                        length=original_variant.length,
                        width=original_variant.width,
                        height=original_variant.height,
                        cj_vid=original_variant.cj_vid,
                    )
                    
                    # Copy variant image if it exists
                    if original_variant.image:
                        try:
                            if hasattr(original_variant.image, 'url') and original_variant.image.url:
                                variant_image_url = original_variant.image.url
                                print(f"   📸 Copying variant image {idx}: {variant_image_url}")
                                
                                response = requests.get(variant_image_url, timeout=10, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                })
                                
                                if response.status_code == 200:
                                    # Generate filename for variant image
                                    url_parts = variant_image_url.split('.')
                                    ext = url_parts[-1].split('?')[0] if len(url_parts) > 1 else 'jpg'
                                    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                        ext = 'jpg'
                                    
                                    file_name = f"variant_{new_variant.id}_{idx}.{ext}"
                                    new_variant.image.save(file_name, ContentFile(response.content), save=True)
                                    print(f"   ✅ Variant image {idx} saved")
                        except Exception as e:
                            print(f"   ⚠️ Could not copy variant image {idx}: {e}")
                    
                    new_variant.save()
                    created_variants.append(new_variant.id)
                    print(f"   ✅ Created variant {new_variant.id} with SKU: {variant_sku}")
                
                # Update product with variant info
                product.has_variants = len(created_variants) > 1
                product.variant_options = {
                    'variants': created_variants,
                    'count': len(created_variants)
                }
                product.save()
                
                # ============================================================
                # ========== CREATE THE GROUPING RECORD ==========
                # ============================================================
                GroupedProduct.objects.create(
                    original_product=self.product,
                    product=product,
                    variant_ids=variant_ids or [variant.id],
                    group_key=group_key,
                    group_display_name=display_name or self.product.title,
                    original_status=self.product.status
                )
                
                print(f"✅ Created product from group: {product.title} (ID: {product.id}) with {len(created_variants)} variants")
                return product
                
        except Exception as e:
            print(f"❌ Error creating product from group: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def _group_by_image(self, variants):
        """Group variants by identical images"""
        groups = defaultdict(list)
        
        for variant in variants:
            image_url = self._get_variant_image_url(variant)
            if image_url:
                # Use hash of image URL as key
                key = hashlib.md5(image_url.encode()).hexdigest()
                groups[key].append(variant)
            else:
                # No image - each variant gets its own group
                groups[f"no_image_{variant.id}"].append(variant)
        
        return dict(groups)
    
    def _group_by_primary_attribute(self, variants):
        """Group variants by primary attribute"""
        primary_attr = self.display_mode.primary_attribute or 'Color'
        groups = defaultdict(list)
        
        for variant in variants:
            value = self._get_attribute_value(variant, primary_attr)
            groups[value].append(variant)
        
        return dict(groups)
    
    def _get_variant_image_url(self, variant):
        """Get image URL from variant"""
        if variant.image and hasattr(variant.image, 'url'):
            return variant.image.url
        return None
    
    def _get_variant_display_name(self, variant):
        """Generate display name for a variant"""
        options = variant.options
        if options:
            return ' / '.join([f"{k}: {v}" for k, v in options.items()])
        if variant.sku:
            return variant.sku
        return f"Variant {variant.id}"
    
    def _get_group_display_name(self, variants):
        """Generate display name for a group"""
        if not variants:
            return "Variant Group"
        
        # Find common attributes
        common = {}
        for v in variants:
            for key, value in v.options.items():
                if key not in common:
                    common[key] = set()
                common[key].add(value)
        
        # Use Color or Style if only one value
        for key in ['Color', 'color', 'Style', 'style']:
            if key in common and len(common[key]) == 1:
                return list(common[key])[0]
        
        # Otherwise combine
        parts = []
        for key, vals in common.items():
            if len(vals) == 1:
                parts.append(f"{key}: {list(vals)[0]}")
        
        if parts:
            return ' / '.join(parts[:2])
        
        return "Variant Group"
    
    def _get_attribute_value(self, variant, attr_name):
        """Get attribute value from variant"""
        if attr_name in variant.options:
            return variant.options[attr_name]
        
        attr_lower = attr_name.lower()
        if attr_lower == 'color':
            return variant.option2 or variant.option1 or 'Default'
        if attr_lower == 'size':
            return variant.option1 or variant.option2 or 'Default'
        
        for key, value in variant.options.items():
            if key.lower() == attr_lower:
                return value
        
        return 'Default'
    
    def restore_original(self):
        """Restore the original product and delete all grouped products"""
        from builder.models import GroupedProduct
        
        with transaction.atomic():
            groups = GroupedProduct.objects.filter(original_product=self.product)
            deleted_count = 0
            
            for group in groups:
                if group.product and group.product.id != self.product.id:
                    try:
                        # Delete variants first
                        group.product.variants.all().delete()
                        group.product.delete()
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Could not delete product {group.product.id}: {e}")
                group.delete()
            
            # Restore original product
            self.product.status = 'active'
            self.product.is_active = True
            self.product.save()
            
            logger.info(f"✅ Restored original product {self.product.id}, deleted {deleted_count} grouped products")
        
        return self.product
    
    def get_grouped_products_data(self):
        """Get data about all grouped products for display"""
        from builder.models import GroupedProduct
        
        groups = GroupedProduct.objects.filter(
            original_product=self.product
        ).select_related('product')
        
        data = []
        for group in groups:
            variant_count = group.product.variants.count() if group.product else 0
            data.append({
                'id': group.id,
                'product_id': group.product.id if group.product else None,
                'title': group.product.title if group.product else group.group_display_name,
                'display_name': group.group_display_name,
                'price': float(group.product.price) if group.product and group.product.price else None,
                'image_url': group.product.main_image.url if group.product and group.product.main_image else None,
                'variant_count': variant_count,
                'total_stock': sum(v.quantity for v in group.product.variants.all()) if group.product else 0,
                'group_key': group.group_key,
                'created_at': group.created_at,
                'is_active': group.product.is_active if group.product else False,
            })
        
        return data


class VariantGroupManager:
    """
    Public API for variant grouping operations.
    This is the main class that other parts of the application should use.
    """
    
    def __init__(self, product):
        self.product = product
        self.service = VariantGroupingService(product)
    
    def process_groups_to_products(self):
        """Process groups and create actual product records with variants"""
        return self.service.process_and_create_products()
    
    def restore_original(self):
        """Restore the original product and delete grouped products"""
        return self.service.restore_original()
    
    def get_display_mode(self):
        """Get the current display mode"""
        return self.service.display_mode
    
    def update_display_mode(self, mode, group_by=None, primary_attribute=None):
        """Update the display mode and save to database"""
        self.service.display_mode.mode = mode
        if group_by:
            self.service.display_mode.group_by = group_by
        if primary_attribute:
            self.service.display_mode.primary_attribute = primary_attribute
        self.service.display_mode.save()
        return self.service.display_mode
    
    def get_grouped_products(self):
        """Get all grouped products for this product"""
        from builder.models import GroupedProduct
        return GroupedProduct.objects.filter(
            original_product=self.product
        ).select_related('product')
    
    def get_grouped_products_data(self):
        """Get formatted data about grouped products"""
        return self.service.get_grouped_products_data()
    
    def get_original_product(self):
        """Get the original product"""
        return self.product
    
    def has_grouped_products(self):
        """Check if this product has grouped products"""
        return self.get_grouped_products().exists()
    
    def get_variant_count(self):
        """Get the number of variants"""
        return self.product.variants.count()
    
    def get_all_attributes(self):
        """Get all attributes from all variants"""
        all_attrs = {}
        for variant in self.product.variants.all():
            for key, value in variant.options.items():
                if key not in all_attrs:
                    all_attrs[key] = []
                if value not in all_attrs[key]:
                    all_attrs[key].append(value)
        return all_attrs