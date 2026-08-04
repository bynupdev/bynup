# import uuid
# from django.utils import timezone
# from user_agents import parse
# import geoip2.database
# import os
# from django.conf import settings
# from .models import WebsiteAnalytics, PageView, Event, TrafficSource, GeographicData

# class AnalyticsMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # Initialize GeoIP database
#         geoip_path = os.path.join(settings.BASE_DIR, 'geoip')
#         self.geoip_reader = None
#         if os.path.exists(os.path.join(geoip_path, 'GeoLite2-City.mmdb')):
#             try:
#                 self.geoip_reader = geoip2.database.Reader(os.path.join(geoip_path, 'GeoLite2-City.mmdb'))
#             except:
#                 self.geoip_reader = None

#     def __call__(self, request):
#         response = self.get_response(request)
        
#         # Only track for published pages
#         if hasattr(request, 'published_page') and request.published_page:
#             self.track_page_view(request, request.published_page)
            
#         return response

#     def get_client_ip(self, request):
#         x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#         if x_forwarded_for:
#             ip = x_forwarded_for.split(',')[0]
#         else:
#             ip = request.META.get('REMOTE_ADDR')
#         return ip

#     def get_geo_data(self, ip_address):
#         if not self.geoip_reader or ip_address in ['127.0.0.1', 'localhost']:
#             return None, None
            
#         try:
#             response = self.geoip_reader.city(ip_address)
#             return response.country.name, response.city.name
#         except:
#             return None, None

#     def get_traffic_source(self, request):
#         referrer = request.META.get('HTTP_REFERER', '')
        
#         if not referrer:
#             return 'direct', 'direct'
        
#         # Parse referrer to determine source
#         if 'google' in referrer or 'bing' in referrer or 'yahoo' in referrer:
#             return 'organic', self.extract_search_engine(referrer)
#         elif 'facebook' in referrer or 'twitter' in referrer or 'instagram' in referrer:
#             return 'social', self.extract_social_media(referrer)
#         else:
#             return 'referral', self.extract_domain(referrer)

#     def extract_search_engine(self, referrer):
#         if 'google' in referrer:
#             return 'google'
#         elif 'bing' in referrer:
#             return 'bing'
#         elif 'yahoo' in referrer:
#             return 'yahoo'
#         return 'other'

#     def extract_social_media(self, referrer):
#         if 'facebook' in referrer:
#             return 'facebook'
#         elif 'twitter' in referrer:
#             return 'twitter'
#         elif 'instagram' in referrer:
#             return 'instagram'
#         elif 'linkedin' in referrer:
#             return 'linkedin'
#         return 'other'

#     def extract_domain(self, referrer):
#         from urllib.parse import urlparse
#         domain = urlparse(referrer).netloc
#         return domain

#     def get_or_create_session(self, request):
#         if 'analytics_session' not in request.session:
#             request.session['analytics_session'] = str(uuid.uuid4())
#         if 'analytics_visitor' not in request.session:
#             request.session['analytics_visitor'] = str(uuid.uuid4())
            
#         return request.session['analytics_session'], request.session['analytics_visitor']

#     def track_page_view(self, request, published_page):
#         try:
#             # Get or create analytics record
#             analytics, created = WebsiteAnalytics.objects.get_or_create(page=published_page)
            
#             # Get session and visitor IDs
#             session_id, visitor_id = self.get_or_create_session(request)
            
#             # Parse user agent
#             user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
#             device_type = 'mobile' if user_agent.is_mobile else 'tablet' if user_agent.is_tablet else 'desktop'
#             browser = user_agent.browser.family
#             os = user_agent.os.family
            
#             # Get geographic data
#             ip_address = self.get_client_ip(request)
#             country, city = self.get_geo_data(ip_address)
            
#             # Get traffic source
#             source_type, source_name = self.get_traffic_source(request)
            
#             # Create page view
#             page_view = PageView.objects.create(
#                 analytics=analytics,
#                 session_id=session_id,
#                 visitor_id=visitor_id,
#                 page_url=request.path,
#                 referrer=request.META.get('HTTP_REFERER'),
#                 device_type=device_type,
#                 browser=browser,
#                 operating_system=os,
#                 country=country,
#                 city=city
#             )
            
#             # Update traffic sources
#             self.update_traffic_source(analytics, source_type, source_name)
            
#             # Update geographic data
#             if country:
#                 self.update_geographic_data(analytics, country, city)
            
#             # Update main analytics metrics
#             self.update_analytics_metrics(analytics)
            
#         except Exception as e:
#             print(f"Analytics tracking error: {e}")

#     def update_traffic_source(self, analytics, source_type, source_name):
#         today = timezone.now().date()
#         traffic_source, created = TrafficSource.objects.get_or_create(
#             analytics=analytics,
#             date=today,
#             source_type=source_type,
#             source_name=source_name,
#             defaults={'visits': 1, 'unique_visitors': 1}
#         )
        
#         if not created:
#             traffic_source.visits += 1
#             traffic_source.save()

#     def update_geographic_data(self, analytics, country, city):
#         today = timezone.now().date()
#         geo_data, created = GeographicData.objects.get_or_create(
#             analytics=analytics,
#             date=today,
#             country=country,
#             city=city,
#             defaults={'visits': 1}
#         )
        
#         if not created:
#             geo_data.visits += 1
#             geo_data.save()

#     def update_analytics_metrics(self, analytics):
#         # Calculate total visits
#         total_visits = PageView.objects.filter(analytics=analytics).count()
        
#         # Calculate unique visitors
#         unique_visitors = PageView.objects.filter(analytics=analytics).values('visitor_id').distinct().count()
        
#         # Calculate bounce rate (sessions with only one page view)
#         from django.db.models import Count
#         session_views = PageView.objects.filter(analytics=analytics).values('session_id').annotate(
#             view_count=Count('id')
#         )
#         bounce_sessions = sum(1 for session in session_views if session['view_count'] == 1)
#         total_sessions = session_views.count()
#         bounce_rate = (bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
#         analytics.total_visits = total_visits
#         analytics.unique_visitors = unique_visitors
#         analytics.bounce_rate = bounce_rate
#         analytics.save()



# analytics/middleware.py
# analytics/middleware.py
# analytics/middleware.py
import uuid
import time
from django.utils import timezone
from django.core.cache import cache
from django.db import models, connection
from user_agents import parse
import requests
import os
from django.conf import settings
from .models import WebsiteAnalytics, PageView

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize GeoIP database
        geoip_path = os.path.join(settings.BASE_DIR, 'geoip')
        self.geoip_reader = None
        if os.path.exists(os.path.join(geoip_path, 'GeoLite2-City.mmdb')):
            try:
                import geoip2.database
                self.geoip_reader = geoip2.database.Reader(os.path.join(geoip_path, 'GeoLite2-City.mmdb'))
            except Exception as e:
                print(f"GeoIP initialization error: {e}")
                self.geoip_reader = None

    def __call__(self, request):
        # DO NOT track here - this gets called twice (once in, once out)
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        This method is called exactly ONCE per request, just before the view is executed.
        This is the most reliable place to track page views.
        """
        # Only track for published pages
        if not hasattr(request, 'published_page') or not request.published_page:
            return None
        
        # Skip if request method is not GET (ignore POST, OPTIONS, etc.)
        if request.method != 'GET':
            return None
        
        # Skip static/media files
        if self._should_ignore_path(request.path):
            return None
        
        # Track the page view
        self.track_page_view(request, request.published_page)
        
        return None
    
    def _should_ignore_path(self, path):
        """Ignore static files, favicon, and other non-page requests"""
        ignore_patterns = [
            '/static/', '/media/', '/favicon.ico', 
            '/robots.txt', '/sitemap.xml', '/admin/',
            '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', 
            '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot',
            '/api/', '/webhooks/'  # Add any API/webhook paths
        ]
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in ignore_patterns)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    # def get_geo_data(self, ip_address):
    #     if not self.geoip_reader or ip_address in ['127.0.0.1', 'localhost', '::1']:
    #         return None, None
    #     try:
    #         response = self.geoip_reader.city(ip_address)
    #         return response.country.name, response.city.name
    #     except Exception:
    #         return None, None

    def get_geo_data(self, ip_address):
        """Get country and city from IP using free API with caching"""
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            return None, None
        
        # Cache results for 24 hours to reduce API calls
        cache_key = f"geoip_{ip_address}"
        cached = cache.get(cache_key)
        if cached:
            return cached.get('country'), cached.get('city')
        
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    result = (data.get('country'), data.get('city'))
                    cache.set(cache_key, {'country': result[0], 'city': result[1]}, 86400)
                    return result
        except Exception:
            pass
        
        return None, None

    def get_or_create_session(self, request):
        if not request.session.session_key:
            request.session.create()
            
        if 'analytics_session' not in request.session:
            request.session['analytics_session'] = str(uuid.uuid4())
        if 'analytics_visitor' not in request.session:
            request.session['analytics_visitor'] = str(uuid.uuid4())
            
        return request.session['analytics_session'], request.session['analytics_visitor']

    def _get_page_name(self, request):
        """Extract a human-readable page name from the request."""
        path = request.path.strip('/')
        
        if hasattr(request, 'resolver_match') and request.resolver_match:
            url_name = request.resolver_match.url_name
            if url_name:
                name_map = {
                    'public_page': 'home',
                    'product_list': 'products',
                    'product_detail': 'product_detail',
                    'view_cart': 'cart',
                    'view_wishlist': 'wishlist',
                }
                return name_map.get(url_name, url_name)
                
        if path == '' or path == 'home':
            return 'home'
        elif 'product' in path:
            return 'products'
        elif 'cart' in path:
            return 'cart'
        else:
            return path.split('/')[0] if path else 'other'

    def track_page_view(self, request, published_page):
        try:
            # Create a UNIQUE tracking ID for this request
            # Using request object's memory address is a hack but works to identify unique requests
            request_id = str(id(request))
            
            # Use a very specific cache key
            cache_key = f"analytics_view_{published_page.id}_{request_id}"
            
            # If already tracked for this exact request object, skip
            if cache.get(cache_key):
                print(f"⏭️ Skipping duplicate tracking for request {request_id}")
                return
            
            # Mark as tracked with a short TTL (just long enough to prevent duplicates)
            cache.set(cache_key, True, 5)
            
            # Additional check: prevent tracking the same path from same session within 3 seconds
            session_key = request.session.session_key or 'no_session'
            path_key = f"analytics_path_{published_page.id}_{session_key}_{request.path}"
            
            if cache.get(path_key):
                print(f"⏭️ Skipping rapid duplicate path: {request.path}")
                return
            
            cache.set(path_key, True, 3)
            
            print(f"✅ Tracking page view: {published_page.brand_name} - {request.path}")
            
            # Get or create analytics record
            analytics, created = WebsiteAnalytics.objects.get_or_create(page=published_page)
            
            # Get session and visitor IDs
            session_id, visitor_id = self.get_or_create_session(request)
            
            # Determine page name
            page_name = self._get_page_name(request)
            is_homepage = (page_name == 'home')
            
            # Parse user agent
            user_agent_string = request.META.get('HTTP_USER_AGENT', '')
            user_agent = parse(user_agent_string)
            
            if user_agent.is_mobile:
                device_type = 'mobile'
            elif user_agent.is_tablet:
                device_type = 'tablet'
            else:
                device_type = 'desktop'
                
            browser = user_agent.browser.family or 'Unknown'
            os_name = user_agent.os.family or 'Unknown'
            
            # Get geographic data
            ip_address = self.get_client_ip(request)
            country, city = self.get_geo_data(ip_address)
            
            # Check if this is the first page view of the session
            first_view = not PageView.objects.filter(
                analytics=analytics, 
                session_id=session_id
            ).exists()
            
            # Create page view record
            PageView.objects.create(
                analytics=analytics,
                session_id=session_id,
                visitor_id=visitor_id,
                page_url=request.path,
                page_name=page_name,
                referrer=request.META.get('HTTP_REFERER', ''),
                device_type=device_type,
                browser=browser,
                operating_system=os_name,
                country=country,
                city=city
            )
            
            # Use a single atomic UPDATE for all counters
            with connection.cursor() as cursor:
                # Base update - always increment total_visits
                sql = """
                    UPDATE analytics_websiteanalytics 
                    SET total_visits = total_visits + 1
                """
                params = []
                
                # Add unique_visitors increment if conditions met
                if first_view and is_homepage:
                    sql += ", unique_visitors = unique_visitors + 1"
                
                sql += " WHERE id = %s"
                params.append(analytics.id)
                
                cursor.execute(sql, params)
                
                # Verify the update worked
                cursor.execute("SELECT total_visits FROM analytics_websiteanalytics WHERE id = %s", [analytics.id])
                new_count = cursor.fetchone()[0]
                print(f"   📊 Total visits now: {new_count}")
            
        except Exception as e:
            print(f"❌ Analytics tracking error: {e}")
            import traceback
            traceback.print_exc()

    # # In your analytics middleware, temporarily add:
    # def track_page_view(self, request, published_page):
    #     ip = self.get_client_ip(request)
    #     country, city = self.get_geo_data(ip)
    #     print(f"IP: {ip} -> Country: {country}, City: {city}")