# cj_utils.py
import logging
from typing import Dict, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def validate_cj_api_response(response: Dict) -> bool:
    """
    Validate CJ API response structure.
    
    Args:
        response: API response dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(response, dict):
        logger.error("API response is not a dictionary")
        return False
    
    if 'code' not in response:
        logger.error("API response missing 'code' field")
        return False
    
    if response.get('code') != 200:
        error_msg = response.get('msg', 'Unknown error')
        logger.error(f"API error {response.get('code')}: {error_msg}")
        return False
    
    if 'data' not in response:
        logger.warning("API response missing 'data' field")
    
    return True

def normalize_product_data(raw_data: Dict) -> Dict:
    """
    Normalize CJ product data to a consistent format.
    
    Args:
        raw_data: Raw product data from CJ API
        
    Returns:
        Normalized product data
    """
    try:
        normalized = {
            'id': raw_data.get('pid', ''),
            'name': raw_data.get('productNameEn', ''),
            'name_local': raw_data.get('productNameLocal', ''),
            'description': raw_data.get('descriptionEn', ''),
            'description_local': raw_data.get('descriptionLocal', ''),
            'main_image': raw_data.get('mainImage', ''),
            'gallery_images': raw_data.get('galleryImages', []),
            'price': Decimal(str(raw_data.get('price', 0))),
            'original_price': Decimal(str(raw_data.get('originalPrice', 0))),
            'category_id': raw_data.get('categoryId', ''),
            'category_name': raw_data.get('categoryName', ''),
            'weight': float(raw_data.get('weight', 0)),
            'package_size': raw_data.get('packageSize', {}),
            'moq': raw_data.get('moq', 1),
            'stock': raw_data.get('stock', 0),
            'sellable': raw_data.get('sellable', True),
            'warehouse': raw_data.get('warehouse', 'CN'),
            'has_variants': raw_data.get('hasVariants', False),
            'variant_count': raw_data.get('variantCount', 0),
            'created_time': raw_data.get('createdTime', ''),
            'updated_time': raw_data.get('updatedTime', ''),
            'raw_data': raw_data  # Keep original for reference
        }
        
        # Calculate display price with rounding
        if normalized['price']:
            normalized['display_price'] = apply_psychological_pricing(normalized['price'])
        
        return normalized
        
    except Exception as e:
        logger.error(f"Failed to normalize product data: {str(e)}")
        return {}

def apply_psychological_pricing(price: Decimal, margin: Decimal = Decimal('0.00')) -> Decimal:
    """
    Apply psychological pricing rounding.
    
    Args:
        price: Base price
        margin: Additional margin percentage
        
    Returns:
        Rounded price
    """
    if margin:
        price = price * (1 + margin / 100)
    
    rounded = price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Get fractional part
    fractional = rounded - Decimal(int(rounded))
    
    if fractional < Decimal('0.95'):
        result = Decimal(int(rounded)) + Decimal('0.95')
    else:
        result = Decimal(int(rounded)) + Decimal('0.99')
    
    return result.quantize(Decimal('0.01'))

def validate_order_data(order_data: Dict) -> Tuple[bool, str]:
    """
    Validate order data before submission.
    
    Args:
        order_data: Order data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['orderNo', 'shippingCountryCode', 'productList', 'buyerInfo']
    
    for field in required_fields:
        if field not in order_data:
            return False, f"Missing required field: {field}"
    
    # Validate buyer info
    buyer_info = order_data['buyerInfo']
    required_buyer_fields = ['name', 'phone', 'address']
    
    for field in required_buyer_fields:
        if field not in buyer_info:
            return False, f"Missing buyer info field: {field}"
    
    # Validate product list
    product_list = order_data['productList']
    if not isinstance(product_list, list) or len(product_list) == 0:
        return False, "Product list must be a non-empty array"
    
    for product in product_list:
        if 'pid' not in product:
            return False, "Product missing 'pid' field"
        if 'quantity' not in product or product['quantity'] < 1:
            return False, "Product must have quantity >= 1"
    
    return True, ""

def calculate_profit(selling_price: Decimal, cost_price: Decimal) -> Dict:
    """
    Calculate profit and margin.
    
    Args:
        selling_price: Selling price
        cost_price: Cost price
        
    Returns:
        Dict with profit and margin
    """
    if cost_price <= 0:
        return {
            'profit': Decimal('0.00'),
            'margin_percent': Decimal('0.00'),
            'margin_amount': Decimal('0.00')
        }
    
    profit = selling_price - cost_price
    margin_percent = (profit / cost_price) * 100
    
    return {
        'profit': profit.quantize(Decimal('0.01')),
        'margin_percent': margin_percent.quantize(Decimal('0.01')),
        'margin_amount': profit.quantize(Decimal('0.01'))
    }