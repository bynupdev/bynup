# payments/decorators.py

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from urllib.parse import urlencode


# ============ UPGRADE PROMPT HELPERS ============

# Human-readable plan names by tier
PLAN_DISPLAY_NAMES = {
    'free':     'Starter',
    'pro':      'Pro',
    'business': 'Business',
    'agency':   'Agency',
}

# Minimum tier required for each named feature
FEATURE_REQUIRED_TIER = {
    'custom_domain':    'pro',
    'remove_branding':  'pro',
    'advanced_seo':     'pro',
    'email_marketing':  'pro',
    'priority_support': 'pro',
    'abandoned_cart':   'business',
    'discount_codes':   'business',
    'white_label':      'agency',
    'custom_templates': 'agency',
}


def _build_upgrade_url(request, feature=None, required_plan=None, reason=None):
    """
    Build a URL to the pricing page with query params so it can
    highlight the right plan and show context to the user.
    """
    params = {'upgrade': '1'}
    if required_plan:
        params['plan'] = required_plan
    if feature:
        params['feature'] = feature
    if reason:
        params['reason'] = reason
    return f"/payments/pricing/?{urlencode(params)}"


def _upgrade_response(request, message, feature=None,
                      required_plan=None, extra=None,
                      error_code='upgrade_required'):
    """
    Central handler for all gated decorators.

    - For AJAX / JSON requests → returns a JSON payload the frontend
      can use to show an inline modal or banner.
    - For normal requests → flashes a Django message and redirects to
      the pricing page with context so it can highlight the right plan.

    `extra` is merged into the JSON payload (e.g. current/limit values).
    """
    payload = {
        'success': False,
        'error': error_code,
        'message': message,
        'upgrade_required': True,
        'required_plan': required_plan,
        'required_plan_display': PLAN_DISPLAY_NAMES.get(required_plan, required_plan),
        'feature': feature,
        'upgrade_url': _build_upgrade_url(request, feature, required_plan),
    }
    if extra:
        payload.update(extra)

    # AJAX / fetch requests get JSON back
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('Accept', '')
        or request.headers.get('Content-Type', '').startswith('application/json')
    )
    if is_ajax:
        return JsonResponse(payload)

    # Regular request: flash a message and redirect to pricing
    messages.warning(request, message)
    return redirect(_build_upgrade_url(request, feature, required_plan))


# ============ HELPER FUNCTIONS ============

def get_user_subscription(user):
    """Get or create user's subscription"""
    from payments.models import Subscription, Plan

    try:
        return user.subscription
    except:
        free_plan = Plan.objects.filter(tier='free').first()
        if not free_plan:
            free_plan = Plan.objects.create(
                name='Starter',
                tier='free',
                max_websites=1,
                max_products=10,
                max_storage_mb=100,
                max_visitors=1000,
                max_form_submissions=10,
            )
        return Subscription.objects.create(user=user, plan=free_plan, status='free')


def get_user_plan(user):
    """Get user's current plan"""
    subscription = get_user_subscription(user)

    if not subscription.is_active or not subscription.plan:
        from payments.models import Plan
        free_plan = Plan.objects.filter(tier='free').first()
        if free_plan:
            return free_plan

        class FreePlan:
            tier = 'free'
            name = 'Starter'
            max_websites = 1
            max_products = 10
            max_storage_mb = 100
            max_visitors = 1000
            max_form_submissions = 10
            max_emails = 0
            max_domains = 0
            free_domain_tlds = []
            custom_domain = False
            remove_branding = False
            advanced_seo = False
            priority_support = False
            email_marketing = False
            abandoned_cart = False
            discount_codes = False
            white_label = False
            custom_templates = False
        return FreePlan()

    return subscription.plan


def get_tier_level(user):
    """Get numeric tier level: free=0, pro=1, business=2, agency=3"""
    plan = get_user_plan(user)
    tier_map = {'free': 0, 'pro': 1, 'business': 2, 'agency': 3}
    return tier_map.get(plan.tier, 0)


# ============ USAGE COUNTING ============

def count_user_websites(user):
    from builder.models import PublishedPage
    return PublishedPage.objects.filter(user=user).count()


def count_user_products(user):
    from builder.models import Product
    return Product.objects.filter(page__user=user).count()


def count_user_form_submissions_this_month(user):
    from builder.models import FormSubmission
    now = timezone.now()
    return FormSubmission.objects.filter(
        page__user=user,
        submitted_at__year=now.year,
        submitted_at__month=now.month
    ).count()


def count_user_domains(user):
    from builder.models import DomainRequest
    return DomainRequest.objects.filter(
        user=user
    ).exclude(
        status__in=DomainRequest.TERMINAL_STATUSES
    ).count()


def count_user_active_domains(user):
    from builder.models import DomainRequest
    return DomainRequest.objects.filter(
        user=user,
        status='active'
    ).count()


def get_user_domain_summary(user):
    plan = get_user_plan(user)
    active_count = count_user_active_domains(user)
    pending_count = count_user_domains(user) - active_count

    return {
        'active': active_count,
        'pending': pending_count,
        'total_used': active_count + pending_count,
        'limit': plan.max_domains,
        'free_tlds': plan.free_domain_tlds or [],
        'has_received_free_domain': getattr(
            getattr(user, 'profile', None),
            'has_received_free_domain',
            False
        ),
    }


def get_user_storage_usage_bytes(user):
    from builder.models import BackgroundImage, ImageCustomization, Product, ProductImages

    total_bytes = 0

    for bg in BackgroundImage.objects.filter(page__user=user):
        if bg.image:
            try:
                total_bytes += bg.image.size
            except:
                pass

    for img in ImageCustomization.objects.filter(page__user=user):
        if img.image:
            try:
                total_bytes += img.image.size
            except:
                pass

    for product in Product.objects.filter(page__user=user):
        if product.main_image:
            try:
                total_bytes += product.main_image.size
            except:
                pass

    for img in ProductImages.objects.filter(product__page__user=user):
        if img.image:
            try:
                total_bytes += img.image.size
            except:
                pass

    return total_bytes


def format_bytes(bytes_val):
    if bytes_val is None:
        return "Unlimited"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


# ============ LIMIT CHECKERS ============

def can_create_website(user):
    plan = get_user_plan(user)
    current_count = count_user_websites(user)

    if plan.max_websites == -1:
        return True, None

    if current_count >= plan.max_websites:
        return False, 0

    return True, plan.max_websites - current_count


def can_add_products(user, count=1):
    plan = get_user_plan(user)
    current_count = count_user_products(user)

    if plan.max_products == -1:
        return True, None

    if current_count + count > plan.max_products:
        remaining = plan.max_products - current_count
        return False, max(0, remaining)

    return True, plan.max_products - (current_count + count)


def can_submit_form(user):
    plan = get_user_plan(user)
    current_count = count_user_form_submissions_this_month(user)

    if plan.max_form_submissions == -1:
        return True, None

    if current_count >= plan.max_form_submissions:
        return False, 0

    return True, plan.max_form_submissions - current_count


def can_upload_file(user, file_size_bytes):
    plan = get_user_plan(user)

    if plan.max_storage_mb == -1:
        return True, None

    limit_bytes = plan.max_storage_mb * 1024 * 1024
    current_bytes = get_user_storage_usage_bytes(user)
    new_total = current_bytes + file_size_bytes

    if new_total > limit_bytes:
        remaining = limit_bytes - current_bytes
        return False, remaining

    return True, limit_bytes - new_total


def can_add_domain(user):
    plan = get_user_plan(user)

    if plan.max_domains == -1:
        return True, None, None

    if plan.max_domains == 0:
        return False, 0, "Your plan does not include custom domains."

    current_count = count_user_domains(user)

    if current_count >= plan.max_domains:
        return False, 0, (
            f"You've reached your plan's domain limit "
            f"({current_count}/{plan.max_domains})."
        )

    return True, plan.max_domains - current_count, None


def has_feature(user, feature_name):
    plan = get_user_plan(user)

    features = {
        'custom_domain':    plan.custom_domain,
        'remove_branding':  plan.remove_branding,
        'advanced_seo':     plan.advanced_seo,
        'priority_support': plan.priority_support,
        'email_marketing':  plan.email_marketing,
        'abandoned_cart':   plan.abandoned_cart,
        'discount_codes':   plan.discount_codes,
        'white_label':      plan.white_label,
        'custom_templates': plan.custom_templates,
    }

    return features.get(feature_name, False)


# ============ DECORATORS ============

def pro_required(view_func):
    """Require Pro plan or higher"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if get_tier_level(request.user) < 1:
            return _upgrade_response(
                request,
                "This feature is available on the Pro plan and above. "
                "Upgrade to unlock it.",
                required_plan='pro',
                feature=getattr(view_func, '__name__', None),
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def business_required(view_func):
    """Require Business plan or higher"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if get_tier_level(request.user) < 2:
            return _upgrade_response(
                request,
                "This feature is available on the Business plan and above. "
                "Upgrade to unlock it.",
                required_plan='business',
                feature=getattr(view_func, '__name__', None),
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def agency_required(view_func):
    """Require Agency plan"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if get_tier_level(request.user) < 3:
            return _upgrade_response(
                request,
                "This feature is available on the Agency plan. "
                "Upgrade to unlock it.",
                required_plan='agency',
                feature=getattr(view_func, '__name__', None),
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def paid_plan_required(view_func):
    """Require any paid plan"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if get_tier_level(request.user) < 1:
            return _upgrade_response(
                request,
                "This feature requires a paid subscription. "
                "Choose a plan to continue.",
                required_plan='pro',
                feature=getattr(view_func, '__name__', None),
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def check_website_limit(view_func):
    """
    Smart decorator:
    - Only checks limits when CREATING new websites
    - Automatically detects edit operations and allows them
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        # ---------- Aggressive edit detection ----------
        is_edit_operation = False

        if kwargs.get('subdomain'):
            is_edit_operation = True

        if '/editor/' in request.path and kwargs.get('subdomain'):
            is_edit_operation = True

        if request.GET.get('edit') or request.GET.get('page_subdomain') or request.GET.get('page'):
            is_edit_operation = True

        subdomain = kwargs.get('subdomain')
        if subdomain:
            from builder.models import PublishedPage
            existing_page = PublishedPage.objects.filter(
                subdomain=subdomain,
                user=request.user
            ).first()
            if existing_page:
                is_edit_operation = True

        if request.method == 'POST':
            try:
                import json
                if request.body:
                    data = json.loads(request.body)
                    if data.get('page_subdomain') or data.get('is_editing') or data.get('subdomain'):
                        is_edit_operation = True
            except:
                pass

        view_name = view_func.__name__
        if view_name in ['editor', 'edit_page', 'publish_page'] and kwargs.get('subdomain'):
            is_edit_operation = True

        if is_edit_operation:
            return view_func(request, *args, **kwargs)

        # ---------- Create operation: check limit ----------
        can_create, remaining = can_create_website(request.user)

        if not can_create:
            plan = get_user_plan(request.user)
            current = count_user_websites(request.user)
            return _upgrade_response(
                request,
                f"You've reached the website limit on the "
                f"{PLAN_DISPLAY_NAMES.get(plan.tier, plan.name)} plan "
                f"({current}/{plan.max_websites}). "
                f"Upgrade to add more stores.",
                required_plan='pro' if plan.tier == 'free' else 'business',
                error_code='limit_exceeded',
                extra={
                    'current': current,
                    'limit': plan.max_websites,
                },
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def check_product_limit(count=1):
    """Check if user can add products"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            can_add, remaining = can_add_products(request.user, count)

            if not can_add:
                plan = get_user_plan(request.user)
                current = count_user_products(request.user)
                return _upgrade_response(
                    request,
                    f"You've reached the product limit on the "
                    f"{PLAN_DISPLAY_NAMES.get(plan.tier, plan.name)} plan "
                    f"({current}/{plan.max_products}). "
                    f"Upgrade to list more products.",
                    required_plan='pro' if plan.tier == 'free' else 'business',
                    error_code='limit_exceeded',
                    extra={
                        'current': current,
                        'limit': plan.max_products,
                        'remaining': remaining,
                    },
                )

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def check_form_submission_limit(view_func):
    """Check if the site owner can receive another form submission this month"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        subdomain = kwargs.get('subdomain')

        if subdomain:
            from builder.models import PublishedPage
            page = PublishedPage.objects.filter(subdomain=subdomain).first()
            if page:
                user = page.user

                can_submit, remaining = can_submit_form(user)

                if not can_submit:
                    plan = get_user_plan(user)
                    current = count_user_form_submissions_this_month(user)
                    return _upgrade_response(
                        request,
                        f"This store has reached its monthly form submission "
                        f"limit ({current}/{plan.max_form_submissions}). "
                        f"The owner needs to upgrade to receive more submissions.",
                        required_plan='pro' if plan.tier == 'free' else 'business',
                        error_code='limit_exceeded',
                        extra={
                            'current': current,
                            'limit': plan.max_form_submissions,
                        },
                    )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def check_storage_before_upload(file_field='image'):
    """Check storage before file upload"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            uploaded_file = request.FILES.get(file_field)
            if not uploaded_file and request.FILES:
                uploaded_file = list(request.FILES.values())[0]

            if uploaded_file:
                can_upload, remaining = can_upload_file(request.user, uploaded_file.size)

                if not can_upload:
                    plan = get_user_plan(request.user)
                    current_bytes = get_user_storage_usage_bytes(request.user)
                    current_mb = current_bytes / (1024 * 1024)
                    limit_mb = plan.max_storage_mb
                    remaining_str = format_bytes(remaining) if remaining else "0 B"

                    return _upgrade_response(
                        request,
                        f"Storage limit reached on the "
                        f"{PLAN_DISPLAY_NAMES.get(plan.tier, plan.name)} plan "
                        f"({current_mb:.1f} MB / {limit_mb} MB used). "
                        f"Upgrade to upload more files.",
                        required_plan='pro' if plan.tier == 'free' else 'business',
                        error_code='storage_full',
                        extra={
                            'current_mb': round(current_mb, 2),
                            'limit_mb': limit_mb,
                            'remaining_bytes': remaining,
                        },
                    )

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def check_domain_eligibility(view_func):
    """
    Runs all eligibility checks before allowing a domain request.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        import json as _json

        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'not_authenticated'})
            return redirect('accounts:login')

        # --- Extract domain + tld ---
        domain_name = ''
        tld = ''

        if request.method == 'POST':
            domain_name = (request.POST.get('domain_name') or '').strip().lower()
            tld = (request.POST.get('tld') or '').strip().lower()

            if not domain_name:
                try:
                    data = _json.loads(request.body or b'{}')
                    domain_name = (data.get('domain_name') or '').strip().lower()
                    tld = (data.get('tld') or '').strip().lower()
                except Exception:
                    pass

        if not domain_name or not tld:
            return _upgrade_response(
                request,
                "Domain name and TLD are required.",
                error_code='invalid_input',
            )

        # --- Subscription active ---
        subscription = get_user_subscription(request.user)
        if not subscription.is_active:
            return _upgrade_response(
                request,
                "Your subscription is not active. Please renew to add domains.",
                error_code='subscription_inactive',
            )

        plan = subscription.plan or get_user_plan(request.user)

        # --- Plan includes domains ---
        if not plan.max_domains or plan.max_domains == 0:
            return _upgrade_response(
                request,
                "Custom domains are available on paid plans. "
                "Upgrade to connect your own domain.",
                feature='custom_domain',
                required_plan='pro',
                error_code='upgrade_required',
            )

        # --- Domain count ---
        can_add, remaining, reason = can_add_domain(request.user)
        if not can_add:
            return _upgrade_response(
                request,
                reason or "Domain limit reached.",
                feature='custom_domain',
                required_plan='business',
                error_code='limit_exceeded',
            )

        # --- TLD ---
        free_tlds = plan.free_domain_tlds or []
        is_free_tier = tld in free_tlds

        if not is_free_tier:
            return _upgrade_response(
                request,
                f"'.{tld}' is not included in your plan. "
                f"Please contact us for pricing.",
                feature='custom_domain',
                required_plan='business',
                error_code='tld_not_included',
            )

        # --- Free domain history ---
        profile = getattr(request.user, 'profile', None)
        if is_free_tier and profile and profile.has_received_free_domain:
            return _upgrade_response(
                request,
                "You've already received a free domain on your account. "
                "Contact support if you need additional domains.",
                feature='custom_domain',
                required_plan='business',
                error_code='free_domain_used',
            )

        request.domain_plan = plan
        request.domain_free_tlds = free_tlds
        request.domain_is_free_tier = is_free_tier
        request.domain_name = domain_name
        request.domain_tld = tld

        return view_func(request, *args, **kwargs)
    return wrapped_view


def custom_domain_required(view_func):
    """Require custom domain feature"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not has_feature(request.user, 'custom_domain'):
            return _upgrade_response(
                request,
                "Custom domains are available on the Pro plan and above. "
                "Upgrade to connect your own domain.",
                feature='custom_domain',
                required_plan='pro',
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def remove_branding_required(view_func):
    """Require remove branding feature"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not has_feature(request.user, 'remove_branding'):
            return _upgrade_response(
                request,
                "Removing the platform branding is available on the Pro plan "
                "and above. Upgrade to unlock it.",
                feature='remove_branding',
                required_plan='pro',
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def email_marketing_required(view_func):
    """Require email marketing feature"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not has_feature(request.user, 'email_marketing'):
            return _upgrade_response(
                request,
                "Email marketing is available on the Pro plan and above. "
                "Upgrade to send campaigns to your customers.",
                feature='email_marketing',
                required_plan='pro',
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def abandoned_cart_required(view_func):
    """Require abandoned cart feature"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not has_feature(request.user, 'abandoned_cart'):
            return _upgrade_response(
                request,
                "Abandoned cart recovery is available on the Business plan "
                "and above. Upgrade to recover lost sales.",
                feature='abandoned_cart',
                required_plan='business',
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def discount_codes_required(view_func):
    """Require discount codes feature"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not has_feature(request.user, 'discount_codes'):
            return _upgrade_response(
                request,
                "Discount codes are available on the Business plan and above. "
                "Upgrade to run promotions.",
                feature='discount_codes',
                required_plan='business',
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def advanced_seo_required(view_func):
    """Require advanced SEO feature"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not has_feature(request.user, 'advanced_seo'):
            return _upgrade_response(
                request,
                "Advanced SEO tools are available on the Pro plan and above. "
                "Upgrade to boost your store's visibility.",
                feature='advanced_seo',
                required_plan='pro',
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def white_label_required(view_func):
    """Require white label feature"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not has_feature(request.user, 'white_label'):
            return _upgrade_response(
                request,
                "White label is available on the Agency plan. "
                "Upgrade to fully rebrand your store.",
                feature='white_label',
                required_plan='agency',
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


def custom_templates_required(view_func):
    """Require custom templates feature"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not has_feature(request.user, 'custom_templates'):
            return _upgrade_response(
                request,
                "Custom template creation is available on the Agency plan. "
                "Upgrade to design your own themes.",
                feature='custom_templates',
                required_plan='agency',
            )

        return view_func(request, *args, **kwargs)
    return wrapped_view


# ============ API HELPER ============

def get_user_limits_status(user):
    """Get complete limits status for API responses"""
    plan = get_user_plan(user)

    websites_current = count_user_websites(user)
    products_current = count_user_products(user)
    forms_current = count_user_form_submissions_this_month(user)
    storage_bytes = get_user_storage_usage_bytes(user)
    domain_summary = get_user_domain_summary(user)

    return {
        'tier': plan.tier,
        'plan_name': plan.name if hasattr(plan, 'name') else 'Free',
        'is_paid': get_tier_level(user) >= 1,

        'websites': {
            'used': websites_current,
            'limit': plan.max_websites if plan.max_websites != -1 else 'Unlimited',
            'remaining': None if plan.max_websites == -1 else max(0, plan.max_websites - websites_current),
        },
        'products': {
            'used': products_current,
            'limit': plan.max_products if plan.max_products != -1 else 'Unlimited',
            'remaining': None if plan.max_products == -1 else max(0, plan.max_products - products_current),
        },
        'forms_this_month': {
            'used': forms_current,
            'limit': plan.max_form_submissions if plan.max_form_submissions != -1 else 'Unlimited',
            'remaining': None if plan.max_form_submissions == -1 else max(0, plan.max_form_submissions - forms_current),
        },
        'storage': {
            'used_bytes': storage_bytes,
            'used_mb': round(storage_bytes / (1024 * 1024), 2),
            'limit_mb': plan.max_storage_mb if plan.max_storage_mb != -1 else 'Unlimited',
            'remaining_bytes': None if plan.max_storage_mb == -1 else max(0, (plan.max_storage_mb * 1024 * 1024) - storage_bytes),
            'percentage': 0 if plan.max_storage_mb == -1 else round((storage_bytes / (plan.max_storage_mb * 1024 * 1024)) * 100, 1),
        },

        'domains': {
            'active': domain_summary['active'],
            'pending': domain_summary['pending'],
            'used': domain_summary['total_used'],
            'limit': domain_summary['limit'] if domain_summary['limit'] != -1 else 'Unlimited',
            'remaining': None if domain_summary['limit'] == -1 else max(
                0, domain_summary['limit'] - domain_summary['total_used']
            ),
            'free_tlds': domain_summary['free_tlds'],
            'has_received_free_domain': domain_summary['has_received_free_domain'],
        },

        'features': {
            'custom_domain':    plan.custom_domain,
            'remove_branding':  plan.remove_branding,
            'advanced_seo':     plan.advanced_seo,
            'priority_support': plan.priority_support,
            'email_marketing':  plan.email_marketing,
            'abandoned_cart':   plan.abandoned_cart,
            'discount_codes':   plan.discount_codes,
            'white_label':      plan.white_label,
            'custom_templates': plan.custom_templates,
        }
    }