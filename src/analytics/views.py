
# analytics/views.py
# analytics/views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse, parse_qs
import json

from builder.models import PublishedPage
from .models import (
    WebsiteAnalytics, PageView, Event, 
    TrafficSource, GeographicData, Conversion
)
from payments.decorators import *


# =============================================
# PAGE NAME EXTRACTION FROM REFERRER ONLY
# =============================================

def extract_page_name_from_referrer(referrer):
    """
    Extract a clean page name from the referrer URL.
    ONLY uses referrer because page_url has unreliable data.
    
    Examples:
        '' -> 'direct'
        'http://ecom12b.localhost:8000/?page=about' -> 'about'
        'http://ecom12b.localhost:8000/?page=products' -> 'products'
        'http://ecom12b.localhost:8000/?page=cart' -> 'cart'
        'http://ecom12b.localhost:8000/?page=contact' -> 'contact'
        'http://ecom12b.localhost:8000/' -> 'home'
        None -> 'direct'
    """
    if not referrer:
        return 'direct'
    
    try:
        # Parse the URL
        parsed = urlparse(referrer)
        query_params = parse_qs(parsed.query)
        
        # Check for 'page' query parameter (your site uses this for navigation)
        if 'page' in query_params:
            page_name = query_params['page'][0].lower().strip()
            return page_name
        
        # If no page parameter, check if it's the homepage
        path = parsed.path.strip('/')
        if not path or path == '':
            return 'home'
        
        # Try to extract from path for non-query-parameter URLs
        if 'product' in path:
            return 'product_detail' if '/' in path else 'products'
        elif 'cart' in path:
            return 'cart'
        elif 'wishlist' in path:
            return 'wishlist'
        elif 'blog' in path:
            return 'blog'
        elif 'contact' in path:
            return 'contact'
        elif 'about' in path:
            return 'about'
        elif 'checkout' in path:
            return 'checkout'
        else:
            return 'other'
            
    except Exception as e:
        print(f"Error parsing referrer '{referrer}': {e}")
        return 'other'


def get_display_name(page_name):
    """Convert a page name to a human-readable display name"""
    display_names = {
        'home': 'Home',
        'products': 'Products',
        'product_detail': 'Product Detail',
        'cart': 'Shopping Cart',
        'wishlist': 'Wishlist',
        'blog': 'Blog',
        'contact': 'Contact',
        'about': 'About Us',
        'checkout': 'Checkout',
        'account': 'Account',
        'terms': 'Terms & Conditions',
        'privacy': 'Privacy Policy',
        'shipping': 'Shipping Policy',
        'direct': 'Direct Traffic',
        'other': 'Other'
    }
    
    if page_name in display_names:
        return display_names[page_name]
    
    # Capitalize and replace underscores
    return page_name.replace('_', ' ').title()


# =============================================
# HELPER FUNCTIONS
# =============================================

def calculate_percentage_change(current, previous):
    """Calculate percentage change between two values"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 1)


def format_duration(duration):
    """Format timedelta to readable string"""
    if not duration:
        return "0s"
    
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def get_source_name_from_referrer(referrer):
    """Extract source name from referrer URL"""
    if not referrer:
        return 'direct'
    
    from urllib.parse import urlparse
    
    referrer_lower = referrer.lower()
    if 'google' in referrer_lower:
        return 'google'
    elif 'facebook' in referrer_lower:
        return 'facebook'
    elif 'twitter' in referrer_lower or 'x.com' in referrer_lower:
        return 'twitter'
    elif 'instagram' in referrer_lower:
        return 'instagram'
    elif 'linkedin' in referrer_lower:
        return 'linkedin'
    elif 'bing' in referrer_lower:
        return 'bing'
    elif 'yahoo' in referrer_lower:
        return 'yahoo'
    else:
        domain = urlparse(referrer).netloc
        return domain if domain else 'other'


# =============================================
# DASHBOARD VIEW
# =============================================


@login_required
@business_required
def analytics_dashboard(request, subdomain):
    """Main analytics dashboard"""
    page = get_object_or_404(PublishedPage, subdomain=subdomain, user=request.user)
    analytics, created = WebsiteAnalytics.objects.get_or_create(page=page)
    
    # Date range - last 30 days by default
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get all data
    time_series_data = get_time_series_data(analytics, start_date, end_date)
    traffic_sources = get_traffic_sources(analytics, start_date, end_date)
    geographic_data = get_geographic_data(analytics, start_date, end_date)
    device_data = get_device_breakdown(analytics, start_date, end_date)
    top_pages = get_top_pages(analytics, start_date, end_date)
    real_time_data = get_real_time_data(analytics)
    overview_data = get_overview_data(analytics, start_date, end_date)
    
    context = {
        'page': page,
        'analytics': analytics,
        'overview': overview_data,
        'time_series_data': time_series_data,
        'traffic_sources': traffic_sources,
        'geographic_data': geographic_data,
        'device_data': device_data,
        'top_pages': top_pages,
        'real_time_data': real_time_data,
        'date_range': {
            'start': start_date,
            'end': end_date
        }
    }
    
    return render(request, 'builder/analytics_dashboard.html', context)


# =============================================
# OVERVIEW DATA (ONLY PAGE VIEWS DIVIDED BY 2)
# =============================================

def get_overview_data(analytics, start_date, end_date):
    """Get overview metrics with corrected bounce rate and session duration"""
    from django.db.models import Min, Max, Count
    
    page_views = PageView.objects.filter(
        analytics=analytics,
        timestamp__date__range=[start_date, end_date]
    )
    
    # PAGE VIEWS: Divide by 2 to correct for double counting
    total_visits = page_views.count() // 2
    
    # UNIQUE VISITORS: Accurate, no division needed
    unique_visitors = page_views.values('visitor_id').distinct().count()
    
    # Get session-level data
    sessions = page_views.values('session_id').annotate(
        raw_views=Count('id'),
        first_view=Min('timestamp'),
        last_view=Max('timestamp')
    )
    
    total_sessions = sessions.count()
    
    # BOUNCE RATE
    if total_sessions > 0:
        bounce_sessions = 0
        total_duration = timedelta(0)
        sessions_with_duration = 0
        
        for session in sessions:
            actual_views = session['raw_views'] // 2
            
            # Bounce if only 1 page view
            if actual_views <= 1:
                bounce_sessions += 1
            # Calculate duration for multi-page sessions
            elif session['first_view'] and session['last_view']:
                duration = session['last_view'] - session['first_view']
                if duration < timedelta(hours=2):  # Cap at 2 hours
                    total_duration += duration
                    sessions_with_duration += 1
        
        bounce_rate = (bounce_sessions / total_sessions) * 100
        avg_duration = total_duration / sessions_with_duration if sessions_with_duration > 0 else timedelta(0)
    else:
        bounce_rate = 0
        avg_duration = timedelta(0)
    
    avg_duration_str = format_duration(avg_duration)
    
    # Percentage change from previous period
    period_days = (end_date - start_date).days
    prev_start_date = start_date - timedelta(days=period_days)
    prev_end_date = start_date - timedelta(days=1)
    
    prev_visits = PageView.objects.filter(
        analytics=analytics,
        timestamp__date__range=[prev_start_date, prev_end_date]
    ).count() // 2
    
    visits_change = calculate_percentage_change(total_visits, prev_visits)
    
    return {
        'total_visits': total_visits,
        'unique_visitors': unique_visitors,
        'bounce_rate': round(bounce_rate, 1),
        'avg_session_duration': avg_duration_str,
        'visits_change': visits_change,
        'total_sessions': total_sessions,
        'period': f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    }

# =============================================
# TIME SERIES DATA (ONLY VISITS DIVIDED BY 2)
# =============================================

def get_time_series_data(analytics, start_date, end_date):
    """Get time series data for charts - only visits divided by 2"""
    daily_data = PageView.objects.filter(
        analytics=analytics,
        timestamp__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        visits=Count('id'),
        visitors=Count('visitor_id', distinct=True)
    ).order_by('date')
    
    # Fill missing dates
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date)
        current_date += timedelta(days=1)
    
    visits_data = []
    visitors_data = []
    
    for date in date_range:
        daily_record = next((item for item in daily_data if item['date'] == date), None)
        
        if daily_record:
            # VISITS: Divide by 2
            visits_count = daily_record['visits'] // 2
            # VISITORS: Accurate, no division
            visitors_count = daily_record['visitors']
        else:
            visits_count = 0
            visitors_count = 0
        
        visits_data.append({
            'date': date.isoformat(),
            'visits': visits_count
        })
        
        visitors_data.append({
            'date': date.isoformat(),
            'visitors': visitors_count
        })
    
    return {
        'visits': visits_data,
        'visitors': visitors_data
    }


# =============================================
# TRAFFIC SOURCES (ONLY VISITS DIVIDED BY 2)
# =============================================

def get_traffic_sources(analytics, start_date, end_date):
    """Get traffic source breakdown - only visits divided by 2"""
    sources = TrafficSource.objects.filter(
        analytics=analytics,
        date__range=[start_date, end_date]
    ).values('source_type', 'source_name').annotate(
        total_visits=Sum('visits'),
        total_visitors=Sum('unique_visitors')
    ).order_by('-total_visits')
    
    result = []
    for source in sources:
        # VISITS: Divide by 2
        visits = (source['total_visits'] or 0) // 2
        # VISITORS: Accurate, no division
        visitors = (source['total_visitors'] or 0)
        
        result.append({
            'source_type': source['source_type'],
            'source_name': source['source_name'],
            'visits': visits,
            'visitors': visitors,
            'display_name': source['source_name'].title() if source['source_name'] != 'direct' else 'Direct'
        })
    
    return result


# =============================================
# GEOGRAPHIC DATA (ONLY VISITS DIVIDED BY 2)
# =============================================

def get_geographic_data(analytics, start_date, end_date):
    """Get geographic visitor data with divide by 2 correction"""
    
    # DEBUG: First check if we have any data at all
    total_views_with_country = PageView.objects.filter(
        analytics=analytics,
        timestamp__date__range=[start_date, end_date],
        country__isnull=False
    ).count()
    
    print(f"🌍 Total page views with country data: {total_views_with_country}")
    
    # Get country counts directly from PageView (more reliable)
    from django.db.models import Count
    
    geo_data = PageView.objects.filter(
        analytics=analytics,
        timestamp__date__range=[start_date, end_date],
        country__isnull=False
    ).values('country').annotate(
        visits=Count('id')
    ).order_by('-visits')[:10]
    
    print(f"🌍 Geo data from PageView: {list(geo_data)}")
    
    result = []
    for item in geo_data:
        if item['country']:
            # VISITS: Divide by 2
            visits = item['visits'] // 2
            result.append({
                'country': item['country'],
                'visits': visits
            })
    
    print(f"🌍 Final result: {result}")
    
    return result

# =============================================
# DEVICE BREAKDOWN (ONLY VISITS DIVIDED BY 2)
# =============================================

def get_device_breakdown(analytics, start_date, end_date):
    """Get device type breakdown - only visits divided by 2"""
    devices = PageView.objects.filter(
        analytics=analytics,
        timestamp__date__range=[start_date, end_date]
    ).values('device_type').annotate(
        visits=Count('id'),
        visitors=Count('visitor_id', distinct=True)
    ).order_by('-visits')
    
    result = []
    for device in devices:
        if device['device_type']:
            # VISITS: Divide by 2
            visits = device['visits'] // 2
            # VISITORS: Accurate, no division
            visitors = device['visitors']
            
            display_name = {
                'desktop': 'Desktop',
                'tablet': 'Tablet',
                'mobile': 'Mobile'
            }.get(device['device_type'], device['device_type'].title())
            
            result.append({
                'device_type': device['device_type'],
                'display_name': display_name,
                'visits': visits,
                'visitors': visitors
            })
    
    return result


# =============================================
# TOP PAGES - EXTRACTED FROM REFERRER ONLY
# =============================================

# analytics/views.py

def get_top_pages(analytics, start_date, end_date):
    """
    Get top visited pages - page names extracted FROM REFERRER ONLY.
    Uses the same counting logic as total visits (divide by 2).
    """
    # Get all page views for the period
    page_views = PageView.objects.filter(
        analytics=analytics,
        timestamp__date__range=[start_date, end_date]
    )
    
    # Count visits by extracted page name from referrer
    page_counts = {}
    visitor_sets = {}
    
    for view in page_views:
        # EXTRACT PAGE NAME FROM REFERRER ONLY
        page_name = extract_page_name_from_referrer(view.referrer)
        
        if page_name not in page_counts:
            page_counts[page_name] = 0
            visitor_sets[page_name] = set()
        
        # Count EVERY page view (this matches total_visits counting)
        page_counts[page_name] += 1
        visitor_sets[page_name].add(view.visitor_id)
    
    # Convert to list, apply divide by 2 (same as total_visits), and sort
    result = []
    for page_name, raw_visits in page_counts.items():
        # VISITS: Divide by 2 to correct for double counting (matches total_visits)
        corrected_visits = raw_visits // 2
        
        # UNIQUE VISITORS: No division needed
        unique_visitors = len(visitor_sets[page_name])
        
        # Only include pages with visits > 0 after correction
        if corrected_visits > 0:
            result.append({
                'page_name': page_name,
                'display_name': get_display_name(page_name),
                'visits': corrected_visits,
                'unique_visitors': unique_visitors,
                'raw_visits': raw_visits  # For debugging
            })
    
    # Sort by visits (descending)
    result.sort(key=lambda x: x['visits'], reverse=True)
    
    # Debug logging
    print(f"\n📊 TOP PAGES DEBUG:")
    print(f"   Total page views in period: {page_views.count()}")
    print(f"   Total visits after divide by 2: {page_views.count() // 2}")
    print(f"   Sum of top pages visits: {sum(r['visits'] for r in result)}")
    print(f"   Top pages breakdown:")
    for r in result[:5]:
        print(f"      {r['display_name']}: {r['visits']} visits (raw: {r['raw_visits']})")
    
    return result[:10]  # Return top 10

# =============================================
# REAL-TIME DATA
# =============================================

def get_real_time_data(analytics):
    """Get real-time active visitors"""
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    
    # VISITORS: Accurate, no division
    active_visitors = PageView.objects.filter(
        analytics=analytics,
        timestamp__gte=five_minutes_ago
    ).values('visitor_id').distinct().count()
    
    active_pages = PageView.objects.filter(
        analytics=analytics,
        timestamp__gte=five_minutes_ago
    ).values('referrer').annotate(
        active_visitors=Count('visitor_id', distinct=True)
    ).order_by('-active_visitors')[:5]
    
    pages_result = []
    for page in active_pages:
        # VISITORS: Accurate, no division
        visitors = page['active_visitors']
        
        # Extract page name from referrer
        page_name = extract_page_name_from_referrer(page['referrer'])
        
        pages_result.append({
            'page_name': page_name,
            'display_name': get_display_name(page_name),
            'active_visitors': visitors
        })
    
    return {
        'active_visitors': active_visitors,
        'active_pages': pages_result
    }


# =============================================
# MAIN API ENDPOINT
# =============================================

@csrf_exempt
def analytics_api(request, subdomain):
    """Real analytics API endpoint - only visits divided by 2"""
    try:
        # Get period from query parameters
        period = request.GET.get('period', '30d')
        
        # Calculate date range
        end_date = timezone.now().date()
        if period == '24h':
            start_date = end_date - timedelta(days=1)
        elif period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
        else:  # 30d default
            start_date = end_date - timedelta(days=30)
        
        # Get analytics for this subdomain
        try:
            page = PublishedPage.objects.get(subdomain=subdomain)
            analytics, created = WebsiteAnalytics.objects.get_or_create(page=page)
        except PublishedPage.DoesNotExist:
            return JsonResponse({'error': 'Page not found'}, status=404)
        
        # Get data based on period
        data = {
            'overview': get_overview_data(analytics, start_date, end_date),
            'time_series': get_time_series_data(analytics, start_date, end_date),
            'traffic_sources': get_traffic_sources(analytics, start_date, end_date),
            'geography': get_geographic_data(analytics, start_date, end_date),
            'devices': get_device_breakdown(analytics, start_date, end_date),
            'pages': get_top_pages(analytics, start_date, end_date),
            'real_time': get_real_time_data(analytics),
            'period': f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# =============================================
# EVENT TRACKING
# =============================================

@csrf_exempt
def track_event(request, subdomain):
    """Track custom events from frontend"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            page = get_object_or_404(PublishedPage, subdomain=subdomain)
            analytics, created = WebsiteAnalytics.objects.get_or_create(page=page)
            
            event = Event.objects.create(
                analytics=analytics,
                session_id=data.get('session_id', ''),
                event_type=data.get('event_type', 'click'),
                event_name=data.get('event_name'),
                element_id=data.get('element_id'),
                element_class=data.get('element_class'),
                element_text=data.get('element_text'),
                metadata=data.get('metadata', {})
            )
            
            return JsonResponse({'success': True, 'event_id': event.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


# =============================================
# CONVERSION TRACKING
# =============================================

@csrf_exempt
def track_conversion(request, subdomain):
    """Track conversions from frontend"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            page = get_object_or_404(PublishedPage, subdomain=subdomain)
            analytics, created = WebsiteAnalytics.objects.get_or_create(page=page)
            
            conversion = Conversion.objects.create(
                analytics=analytics,
                session_id=data.get('session_id', ''),
                conversion_type=data.get('conversion_type', 'form_submit'),
                conversion_value=data.get('conversion_value'),
                metadata=data.get('metadata', {})
            )
            
            return JsonResponse({'success': True, 'conversion_id': conversion.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


# =============================================
# PAGE VIEWS LIST (ONLY TOTAL DIVIDED BY 2)
# =============================================

@login_required
def page_views_list(request, subdomain):
    """List individual page views - page names extracted from referrer"""
    page = get_object_or_404(PublishedPage, subdomain=subdomain, user=request.user)
    analytics = get_object_or_404(WebsiteAnalytics, page=page)
    
    # Get filter parameters
    page_filter = request.GET.get('page', '')
    device_filter = request.GET.get('device', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    page_views = PageView.objects.filter(analytics=analytics)
    
    # Apply filters
    if page_filter:
        # Filter by extracted page name (requires iteration, but okay for small datasets)
        # For larger datasets, you'd want to store page_name in the model
        filtered_ids = []
        for view in page_views:
            if extract_page_name_from_referrer(view.referrer) == page_filter:
                filtered_ids.append(view.id)
        page_views = page_views.filter(id__in=filtered_ids)
    
    if device_filter:
        page_views = page_views.filter(device_type=device_filter)
    
    if date_from:
        page_views = page_views.filter(timestamp__date__gte=date_from)
    
    if date_to:
        page_views = page_views.filter(timestamp__date__lte=date_to)
    
    # Order and paginate
    page_views = page_views.order_by('-timestamp')
    
    from django.core.paginator import Paginator
    paginator = Paginator(page_views, 50)
    page_number = request.GET.get('page_num', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get unique page names for filter dropdown
    all_referrers = PageView.objects.filter(
        analytics=analytics
    ).values_list('referrer', flat=True).distinct()
    
    page_names = set()
    for referrer in all_referrers:
        if referrer:
            page_name = extract_page_name_from_referrer(referrer)
            if page_name != 'direct':
                page_names.add(page_name)
    
    # Add page_name to each view for display
    for view in page_obj:
        view.extracted_page_name = extract_page_name_from_referrer(view.referrer)
        view.display_page_name = get_display_name(view.extracted_page_name)
    
    # TOTAL PAGE VIEWS: Divide by 2
    total_views = page_views.count() // 2
    print(f"Page names are: {page_names}")
    
    context = {
        'page': page,
        'analytics': analytics,
        'page_views': page_obj,
        'page_names': sorted(page_names),
        'total_views': total_views,
        'page_filter': page_filter,
        'device_filter': device_filter,
        'date_from': date_from,
        'date_to': date_to
    }
    
    return render(request, 'builder/analytics_page_views.html', context)