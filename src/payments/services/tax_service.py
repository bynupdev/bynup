# services/tax_service.py
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from payments.models import TaxExemptCustomer 
import logging
import re

logger = logging.getLogger(__name__)

class TaxCalculationError(Exception):
    """Custom exception for tax calculation errors"""
    pass


class TaxService:
    """
    Core service for tax calculations and management
    """
    
    def __init__(self, page):
        self.page = page
        self.cache = {}  # Cache for frequently accessed data
        
    
    # services/tax_service.py

    def calculate_tax(self, items, customer_data, shipping_cost=0, debug=False):
        """
        Calculate tax for cart items - LOOKS UP TAX CLASS FROM DATABASE
        """
        try:
            print("\n" + "="*50)
            print("TAX CALCULATION DEBUG")
            print("="*50)
            print(f"Customer: {customer_data}")
            print(f"Shipping: {shipping_cost}")
            print(f"Items received: {len(items)}")
            
            # Import Product here to avoid circular imports
            from builder.models import Product
            
            total_tax = Decimal('0.00')
            breakdown = []
            debug_info = []
            
            # Get page settings
            settings = self.page.settings.get('tax', {})
            prices_include_tax = settings.get('prices_include_tax', False)
            
            # Process each item
            for i, item in enumerate(items):
                print(f"\nProcessing item {i+1}: {item.get('title')}")
                
                # LOOK UP TAX CLASS FROM DATABASE USING PRODUCT ID
                product_id = item.get('product_id') or item.get('id')
                tax_class_id = None
                
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id)
                        tax_class_id = product.tax_class_id
                        print(f"  → Found product in DB: {product.title}")
                        print(f"  → Tax class ID: {tax_class_id}")
                        print(f"  → Tax class name: {product.tax_class.name if product.tax_class else 'None'}")
                    except Product.DoesNotExist:
                        print(f"  → Product {product_id} not found in database")
                
                # If no tax class found, use default
                if not tax_class_id:
                    default_class = self.page.tax_classes.filter(is_default=True).first()
                    if default_class:
                        tax_class_id = default_class.id
                        print(f"  → Using default tax class: {default_class.name}")
                
                # Create enriched item with tax_class_id
                enriched_item = {
                    'product_id': product_id,
                    'title': item.get('title', ''),
                    'price': Decimal(str(item.get('price', 0))),
                    'quantity': int(item.get('quantity', 1)),
                    'tax_class_id': tax_class_id
                }
                
                # Calculate tax for this item
                item_tax = self._calculate_item_tax(
                    item=enriched_item,
                    customer_data=customer_data,
                    prices_include_tax=prices_include_tax
                )
                
                if item_tax and item_tax['tax_amount'] > 0:
                    print(f"  → Tax calculated: ${item_tax['tax_amount']}")
                    total_tax += Decimal(str(item_tax['tax_amount']))
                    breakdown.append(item_tax)
                else:
                    print(f"  → No tax applicable for this item")
            
            # Calculate tax on shipping if applicable
            settings = self.page.settings.get('tax', {})
            tax_shipping = settings.get('tax_shipping', False)
            
            if tax_shipping and shipping_cost > 0:
                print(f"\nCalculating shipping tax on ${shipping_cost}")
                shipping_tax = self._calculate_shipping_tax(
                    shipping_cost=shipping_cost,
                    customer_data=customer_data
                )
                
                if shipping_tax and shipping_tax['tax_amount'] > 0:
                    print(f"  → Shipping tax: ${shipping_tax['tax_amount']}")
                    total_tax += Decimal(str(shipping_tax['tax_amount']))
                    breakdown.append(shipping_tax)
            
            # Round to 2 decimal places
            total_tax = total_tax.quantize(Decimal('0.01'))
            print(f"\n✅ TOTAL TAX: ${total_tax}")
            print("="*50 + "\n")
            
            result = {
                'tax_total': float(total_tax),
                'breakdown': breakdown,
                'is_exempt': False
            }
            
            if debug:
                result['debug_info'] = debug_info
                result['calculation_time'] = timezone.now().isoformat()
            
            return result
            
        except Exception as e:
            print(f"❌ TAX CALCULATION ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            raise TaxCalculationError(f"Failed to calculate tax: {str(e)}")


    def _calculate_item_tax(self, item, customer_data, prices_include_tax=False):
        """Calculate tax for a single item"""
        try:
            # Get tax_class_id from item
            tax_class_id = item.get('tax_class_id')
            
            if not tax_class_id:
                print(f"  → No tax class ID for item {item.get('title')}")
                return None
            
            print(f"  → Getting applicable tax rates for tax_class_id: {tax_class_id}")
            
            # Get applicable tax rates
            rates = self._get_applicable_tax_rates(
                tax_class_id=tax_class_id,
                customer_data=customer_data
            )
            
            if not rates:
                print(f"  → No applicable tax rates found for tax class {tax_class_id}")
                # Print all rates for debugging
                all_rates = self.page.tax_rates.filter(is_active=True)
                print(f"  → All active rates in system: {all_rates.count()}")
                for r in all_rates:
                    print(f"      {r.name}: {r.country_code} {r.state_code} - {r.rate}%")
                return None
            
            # Calculate taxable amount
            item_subtotal = Decimal(str(item['price'])) * Decimal(str(item['quantity']))
            item_tax = Decimal('0.00')
            applied_rates = []
            
            print(f"  → Found {len(rates)} applicable rates")
            print(f"  → Item subtotal: ${item_subtotal}")
            
            # Sort by priority (lower numbers first)
            rates = sorted(rates, key=lambda x: x.priority)
            
            for rate in rates:
                if prices_include_tax:
                    # Tax is included in price - back-calculate
                    tax_amount = item_subtotal - (item_subtotal / (1 + (rate.rate / 100)))
                else:
                    # Tax is added to price
                    tax_amount = item_subtotal * (rate.rate / 100)
                
                print(f"      Rate {rate.name}: {rate.rate}% = ${tax_amount}")
                
                # Handle compound tax
                if rate.is_compound:
                    # Add to taxable base for next rates
                    item_subtotal += tax_amount
                
                item_tax += tax_amount
                
                applied_rates.append({
                    'rate_id': rate.id,
                    'rate_name': rate.name,
                    'rate_percentage': float(rate.rate),
                    'tax_amount': float(tax_amount.quantize(Decimal('0.01'))),
                    'jurisdiction': self._format_jurisdiction(rate)
                })
            
            print(f"  → Total tax for item: ${item_tax}")
            
            return {
                'product_id': item.get('product_id'),
                'product_title': item.get('title', 'Unknown'),
                'taxable_amount': float(item_subtotal.quantize(Decimal('0.01'))),
                'tax_amount': float(item_tax.quantize(Decimal('0.01'))),
                'rates_applied': applied_rates
            }
            
        except Exception as e:
            print(f"Error in _calculate_item_tax: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        
    def _calculate_shipping_tax(self, shipping_cost, customer_data):
        """Calculate tax on shipping"""
        try:
            # Get default tax class for shipping
            default_tax_class = self.page.tax_classes.filter(is_default=True).first()
            
            if not default_tax_class or not default_tax_class.is_shipping_taxable:
                return None
            
            # Get applicable tax rates for shipping
            rates = self._get_applicable_tax_rates(
                tax_class_id=default_tax_class.id,
                customer_data=customer_data,
                is_shipping=True
            )
            
            if not rates:
                return None
            
            shipping_tax = Decimal('0.00')
            applied_rates = []
            
            for rate in rates:
                tax_amount = shipping_cost * (rate.rate / 100)
                shipping_tax += tax_amount
                
                applied_rates.append({
                    'rate_id': rate.id,
                    'rate_name': f"Shipping - {rate.name}",
                    'rate_percentage': float(rate.rate),
                    'tax_amount': float(tax_amount.quantize(Decimal('0.01'))),
                    'jurisdiction': self._format_jurisdiction(rate)
                })
            
            return {
                'product_id': 'shipping',
                'product_title': 'Shipping',
                'taxable_amount': float(shipping_cost.quantize(Decimal('0.01'))),
                'tax_amount': float(shipping_tax.quantize(Decimal('0.01'))),
                'rates_applied': applied_rates
            }
            
        except Exception as e:
            logger.error(f"Shipping tax calculation error: {str(e)}")
            return None
    
    def _get_applicable_tax_rates(self, tax_class_id, customer_data, is_shipping=False):
        """Get all applicable tax rates for a given jurisdiction"""
        try:
            country = customer_data.get('country', '').upper()
            state = customer_data.get('state', '').upper()
            city = customer_data.get('city', '')
            postal_code = customer_data.get('postal_code', '')
            
            # Start with rates for this tax class
            queryset = self.page.tax_rates.filter(
                tax_class_id=tax_class_id,
                is_active=True,
                valid_from__lte=timezone.now()
            ).filter(
                models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=timezone.now())
            )
            
            # Filter by jurisdiction
            if country:
                queryset = queryset.filter(
                    models.Q(country_code=country) | models.Q(country_code='')
                )
            
            if state:
                queryset = queryset.filter(
                    models.Q(state_code=state) | models.Q(state_code='')
                )
            
            if city:
                queryset = queryset.filter(
                    models.Q(city=city) | models.Q(city='')
                )
            
            if postal_code and not is_shipping:
                # Handle postal code matching
                postal_rates = queryset.filter(jurisdiction_type='postal_code')
                for rate in postal_rates:
                    if rate.postal_code_match_pattern:
                        if re.match(rate.postal_code_match_pattern, postal_code):
                            pass  # Rate is already included
                    elif rate.postal_code == postal_code:
                        pass  # Exact match
                    else:
                        queryset = queryset.exclude(id=rate.id)
            
            # Apply shipping filter if needed
            if is_shipping:
                queryset = queryset.filter(is_shipping_taxable=True)
            
            return queryset.order_by('priority')
            
        except Exception as e:
            logger.error(f"Error getting applicable tax rates: {str(e)}")
            return []
    
    def _is_tax_exempt(self, email):
        """Check if customer is tax exempt"""
        if not email:
            return False
        
        try:
            exempt = TaxExemptCustomer.objects.filter(
                page=self.page,
                email=email,
                is_active=True,
                exempt_from__lte=timezone.now()
            ).filter(
                models.Q(exempt_until__isnull=True) | models.Q(exempt_until__gte=timezone.now())
            ).exists()
            
            return exempt
            
        except Exception as e:
            logger.error(f"Error checking tax exemption: {str(e)}")
            return False
    
    def _format_jurisdiction(self, rate):
        """Format jurisdiction for display"""
        parts = []
        if rate.country_code:
            parts.append(rate.country_code)
        if rate.state_code:
            parts.append(rate.state_code)
        if rate.city:
            parts.append(rate.city)
        if rate.postal_code:
            parts.append(rate.postal_code)
        
        return ' - '.join(parts) if parts else 'Global'
    
    def save_tax_transaction(self, order, tax_result):
        """Save tax calculation for auditing"""
        try:
            from ..models import TaxTransaction
            
            for item_tax in tax_result.get('breakdown', []):
                for rate_applied in item_tax.get('rates_applied', []):
                    TaxTransaction.objects.create(
                        order=order,
                        tax_class_id=rate_applied.get('rate_id'),
                        tax_rate_id=rate_applied.get('rate_id'),
                        taxable_amount=item_tax['taxable_amount'],
                        tax_amount=item_tax['tax_amount'],
                        rate_applied=rate_applied['rate_percentage'],
                        jurisdiction_type='custom',
                        jurisdiction_name=rate_applied['jurisdiction'],
                        status='applied',
                        applied_at=timezone.now()
                    )
        except Exception as e:
            logger.error(f"Error saving tax transaction: {str(e)}")
    
    def validate_tax_rate(self, rate_data):
        """Validate tax rate data before saving"""
        errors = []
        
        # Check rate value
        if rate_data.get('rate', 0) < 0 or rate_data.get('rate', 0) > 100:
            errors.append("Rate must be between 0 and 100")
        
        # Validate dates
        if rate_data.get('valid_until'):
            if rate_data['valid_until'] <= rate_data.get('valid_from', timezone.now()):
                errors.append("Valid until date must be after valid from date")
        
        # Check for duplicate rates
        existing = TaxRate.objects.filter(
            page=self.page,
            tax_class_id=rate_data.get('tax_class_id'),
            country_code=rate_data.get('country_code', ''),
            state_code=rate_data.get('state_code', ''),
            city=rate_data.get('city', '')
        ).exclude(id=rate_data.get('id'))
        
        if existing.exists():
            errors.append("A tax rate for this jurisdiction already exists")
        
        return errors


    # Debbug code
    # In services/tax_service.py - update calculate_tax method

    def calculate_tax(self, items, customer_data, shipping_cost=0, debug=False):
        """
        Calculate tax for cart items - LOOKS UP TAX CLASS FROM DATABASE
        """
        try:
            print("\n" + "="*50)
            print("TAX CALCULATION DEBUG")
            print("="*50)
            print(f"Customer: {customer_data}")
            print(f"Shipping: {shipping_cost}")
            print(f"Items received from frontend: {len(items)}")
            
            # Import Product here to avoid circular imports
            from builder.models import Product
            
            # Check if customer is tax exempt
            if self._is_tax_exempt(customer_data.get('email')):
                print("⚠️ Customer is tax exempt")
                return {
                    'tax_total': Decimal('0.00'),
                    'breakdown': [],
                    'is_exempt': True,
                    'message': 'Customer is tax exempt'
                }
            
            total_tax = Decimal('0.00')
            breakdown = []
            debug_info = []
            
            # Get page settings
            settings = self.page.settings.get('tax', {})
            prices_include_tax = settings.get('prices_include_tax', False)
            tax_shipping = settings.get('tax_shipping', False)
            
            # Calculate tax per item
            for i, frontend_item in enumerate(items):
                print(f"\nProcessing item {i+1}: {frontend_item.get('title')}")
                
                # Get product_id from frontend item (could be 'id' or 'product_id')
                product_id = frontend_item.get('product_id') or frontend_item.get('id')
                print(f"  → Product ID from frontend: {product_id}")
                
                # LOOK UP PRODUCT IN DATABASE
                tax_class_id = None
                product_title = frontend_item.get('title', 'Unknown')
                
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id)
                        print(f"  → Found product in DB: {product.title}")
                        print(f"  → Product tax_class_id: {product.tax_class_id}")
                        print(f"  → Tax class name: {product.tax_class.name if product.tax_class else 'None'}")
                        
                        if product.tax_class:
                            tax_class_id = product.tax_class.id
                        else:
                            print(f"  → WARNING: Product has no tax class assigned!")
                            
                    except Product.DoesNotExist:
                        print(f"  → ERROR: Product {product_id} not found in database")
                    except Exception as e:
                        print(f"  → ERROR looking up product: {str(e)}")
                else:
                    print(f"  → WARNING: No product ID provided in frontend item")
                
                # If no tax class found, try to use default
                if not tax_class_id:
                    default_class = self.page.tax_classes.filter(is_default=True).first()
                    if default_class:
                        tax_class_id = default_class.id
                        print(f"  → Using default tax class: {default_class.name} (ID: {tax_class_id})")
                    else:
                        print(f"  → No default tax class found!")
                
                # Create enriched item with tax_class_id
                enriched_item = {
                    'product_id': product_id,
                    'title': product_title,
                    'price': Decimal(str(frontend_item.get('price', 0))),
                    'quantity': int(frontend_item.get('quantity', 1)),
                    'tax_class_id': tax_class_id
                }
                
                print(f"  → Enriched item tax_class_id: {enriched_item['tax_class_id']}")
                
                # Calculate tax for this item
                if enriched_item['tax_class_id']:
                    item_tax = self._calculate_item_tax(
                        item=enriched_item,
                        customer_data=customer_data,
                        prices_include_tax=prices_include_tax
                    )
                    
                    if item_tax:
                        print(f"  → Tax calculated: ${item_tax['tax_amount']}")
                        total_tax += Decimal(str(item_tax['tax_amount']))
                        breakdown.append(item_tax)
                        
                        if debug:
                            debug_info.append(item_tax)
                    else:
                        print(f"  → No tax applicable for this item (calculation returned None)")
                else:
                    print(f"  → Skipping item - no tax class ID available")
            
            # Calculate tax on shipping if applicable
            if tax_shipping and shipping_cost > 0:
                print(f"\nCalculating shipping tax on ${shipping_cost}")
                shipping_tax = self._calculate_shipping_tax(
                    shipping_cost=shipping_cost,
                    customer_data=customer_data
                )
                
                if shipping_tax:
                    print(f"  → Shipping tax: ${shipping_tax['tax_amount']}")
                    total_tax += Decimal(str(shipping_tax['tax_amount']))
                    breakdown.append(shipping_tax)
                    
                    if debug:
                        debug_info.append(shipping_tax)
            
            # Round to 2 decimal places
            total_tax = total_tax.quantize(Decimal('0.01'))
            print(f"\n✅ TOTAL TAX: ${total_tax}")
            print("="*50 + "\n")
            
            result = {
                'tax_total': float(total_tax),
                'breakdown': breakdown,
                'is_exempt': False
            }
            
            if debug:
                result['debug_info'] = debug_info
                result['calculation_time'] = timezone.now().isoformat()
            
            return result
            
        except Exception as e:
            print(f"❌ TAX CALCULATION ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            raise TaxCalculationError(f"Failed to calculate tax: {str(e)}")