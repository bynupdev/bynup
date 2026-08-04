


import re
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import PublishedPage
from django.db.models import F

class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        host = request.get_host().lower()
        
        # Remove port for matching
        host_without_port = host.split(':')[0]
        
        # Check if it's a custom domain
        custom_domain_page = self.get_custom_domain_page(host_without_port)
        if custom_domain_page:
            request.published_page = custom_domain_page
            request.domain_type = 'custom'
        else:
            # Check if it's a subdomain
            subdomain = self.extract_subdomain(host_without_port)
            if subdomain and subdomain not in ['www', 'admin', 'api', 'static']:
                request.subdomain = subdomain
                try:
                    request.published_page = PublishedPage.objects.get(
                        subdomain=subdomain, 
                        is_published=True
                    )
                    request.domain_type = 'subdomain'
                except PublishedPage.DoesNotExist:
                    request.published_page = None
                    request.domain_type = None
            else:
                request.subdomain = None
                request.published_page = None
                request.domain_type = None
        response = self.get_response(request)
        return response
    
    def extract_subdomain(self, host):
        """Extract subdomain from host"""
        if 'localhost' in host or '127.0.0.1' in host:
            # Development: subdomain.localhost
            parts = host.split('.')
            if len(parts) >= 2 and parts[0] != 'localhost' and parts[0] != '127':
                return parts[0]
        else:
            # Production: subdomain.yourdomain.com
            parts = host.split('.')
            if len(parts) >= 3:
                return parts[0]
        return None
    
    def get_custom_domain_page(self, host):
        """Check if host matches any custom domain"""
        try:
            return PublishedPage.objects.get(
                custom_domain=host,
                is_custom_domain_active=True,
                is_published=True
            )
        except PublishedPage.DoesNotExist:
            return None
        





# builder/middleware.py
from django.db.models import F

class TrackProductViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Only track if we have a published page context
        if hasattr(request, 'published_page') and request.published_page:
            self.track_product_view(request)
        
        return response
    
    # builder/middleware.py

    def track_product_view(self, request):
        """Track product detail page views"""
        from .models import RecentlyViewedProduct, Product
        from django.utils import timezone
        from datetime import timedelta
        
        path = request.path
        
        # Check for product detail page with slug
        if '/product/' in path and not '/products/' in path:
            try:
                # Extract slug from URL
                import re
                # Match pattern like /product/some-product-slug/
                match = re.search(r'/product/([a-zA-Z0-9-]+)/?', path)
                if match:
                    slug = match.group(1)
                    
                    # Get product by slug
                    try:
                        product = Product.objects.get(slug=slug, page=request.published_page)
                        
                        session_key = request.session.session_key
                        if not session_key:
                            request.session.create()
                            session_key = request.session.session_key
                        
                        # Increment view count
                        product.view_count = product.view_count + 1
                        product.save(update_fields=['view_count'])
                        print(f"✅ View count updated for product {product.title}: {product.view_count}")
                        
                        # Track recently viewed
                        recent_threshold = timezone.now() - timedelta(hours=1)
                        
                        existing = RecentlyViewedProduct.objects.filter(
                            page=request.published_page,
                            product=product,
                            session_key=session_key,
                            viewed_at__gte=recent_threshold
                        ).exists()
                        
                        if not existing:
                            RecentlyViewedProduct.objects.create(
                                page=request.published_page,
                                product=product,
                                session_key=session_key,
                                user=request.user if request.user.is_authenticated else None
                            )
                            
                            # Cleanup old records
                            to_keep = 20
                            recent_views = RecentlyViewedProduct.objects.filter(
                                page=request.published_page,
                                session_key=session_key
                            ).order_by('-viewed_at')
                            
                            if recent_views.count() > to_keep:
                                ids_to_delete = recent_views[to_keep:].values_list('id', flat=True)
                                RecentlyViewedProduct.objects.filter(id__in=list(ids_to_delete)).delete()
                                
                    except Product.DoesNotExist:
                        print(f"❌ Product with slug '{slug}' not found")
                        
            except Exception as e:
                print(f"❌ Error tracking product view: {e}")