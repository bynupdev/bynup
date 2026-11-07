from django import template

register = template.Library()


# ===== EXISTING FILTERS (kept as-is) =====

@register.filter
def sum_quantity(variants):
    if not variants:
        return 0
    try:
        return sum(v.quantity for v in variants)
    except Exception:
        return 0


@register.simple_tag(takes_context=True)
def resolve_product(context):
    """Return the first available product. Never raises."""
    try:
        products = context.get('products')
        if products:
            try:
                first = products[0]
                if first is not None:
                    return first
            except (TypeError, IndexError, KeyError):
                pass
        single = context.get('product')
        if single is not None:
            return single
    except Exception:
        pass
    return None


@register.filter
def split(value, sep=','):
    """Split a string by separator. Safe on None."""
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    try:
        return [item.strip() for item in str(value).split(sep) if item.strip()]
    except Exception:
        return []


@register.filter
def mul(value, arg):
    """Multiply value by arg. Safe on None / non-numeric."""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0


# ===== NEW FAIL-SAFE FILTERS =====

@register.filter
def safe_price(value, default=0):
    """Return a float price, defaulting on error."""
    try:
        return float(value) if value is not None else float(default)
    except (TypeError, ValueError):
        try:
            return float(default)
        except (TypeError, ValueError):
            return 0.0


@register.filter
def safe_int(value, default=0):
    """Return an int, defaulting on error."""
    try:
        return int(value) if value is not None else int(default)
    except (TypeError, ValueError):
        try:
            return int(default)
        except (TypeError, ValueError):
            return 0


@register.filter
def safe_str(value, default=''):
    """Return a string, defaulting on None."""
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


@register.filter
def safe_image(value):
    """Return a URL from an image field, or a placeholder."""
    PLACEHOLDER = (
        "https://images.pexels.com/photos/4047186/pexels-photo-4047186.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    )
    if not value:
        return PLACEHOLDER
    try:
        url = value.url
        return url or PLACEHOLDER
    except Exception:
        return PLACEHOLDER


@register.filter
def safe_tiers(tiers):
    """Iterate tiers safely. Returns a list of dicts."""
    out = []
    if not tiers:
        return out
    try:
        for t in tiers:
            try:
                out.append({
                    'id': t.id,
                    'tier_id': getattr(t, 'id', None),
                    'quantity': getattr(t, 'quantity', 1),
                    'price_per_unit': float(getattr(t, 'price_per_unit', 0) or 0),
                    'total_price': float(getattr(t, 'total_price', 0) or 0),
                    'badge_text': getattr(t, 'badge_text', '') or '',
                    'is_default': bool(getattr(t, 'is_default', False)),
                })
            except Exception:
                continue
    except Exception:
        return []
    return out


@register.filter
def safe_variants(variants):
    """Iterate variants safely."""
    out = []
    if not variants:
        return out
    try:
        for v in variants:
            try:
                img_url = None
                try:
                    if v.image:
                        img_url = v.image.url
                except Exception:
                    pass
                out.append({
                    'id': v.id,
                    'sku': getattr(v, 'sku', '') or 'Option',
                    'price': float(getattr(v, 'price', 0) or 0),
                    'compare_at_price': getattr(v, 'compare_at_price', None),
                    'image_url': img_url,
                    'options': getattr(v, 'options', {}) or {},
                })
            except Exception:
                continue
    except Exception:
        return []
    return out


@register.filter
def safe_gallery(images, limit=3):
    """Return up to `limit` gallery images as dicts."""
    out = []
    if not images:
        return out
    try:
        for i, img in enumerate(images):
            if i >= int(limit):
                break
            try:
                url = img.image.url if img.image else None
                out.append({
                    'url': url,
                    'alt_text': getattr(img, 'alt_text', '') or '',
                })
            except Exception:
                continue
    except Exception:
        return []
    return out


@register.filter
def safe_reviews(reviews):
    """Return review stats."""
    stats = {'total': 0, 'average': 0.0, 'has_reviews': False}
    if not reviews:
        return stats
    try:
        total = reviews.count() if hasattr(reviews, 'count') else len(reviews)
        if total == 0:
            return stats
        from django.db.models import Avg
        avg = reviews.aggregate(a=Avg('rating'))['a'] or 0
        return {
            'total': total,
            'average': round(float(avg), 1),
            'has_reviews': True,
        }
    except Exception:
        return stats


@register.filter
def variant_label(variant):
    """
    Return a human-readable label for a variant.
    Tries option values joined, falls back to SKU, then to "Option".
    """
    if not variant:
        return "Option"

    # 1. Try the options dict
    options = getattr(variant, 'options', None)
    if options and isinstance(options, dict):
        # Build "Color: Red · Size: Large"
        parts = []
        for key, value in options.items():
            if value is None or value == '':
                continue
            parts.append(f"{key}: {value}")
        if parts:
            return ' · '.join(parts)

    # 2. Try option1 / option2 / option3 fields (Shopify-style)
    opt_parts = []
    for attr in ('option1', 'option2', 'option3'):
        val = getattr(variant, attr, None)
        if val:
            opt_parts.append(str(val))
    if opt_parts:
        return ' · '.join(opt_parts)

    # 3. Fall back to SKU
    sku = getattr(variant, 'sku', None)
    if sku:
        return sku

    # 4. Last resort
    return "Option"

@register.filter
def variant_color_value(variant):
    """Return the value of the 'Color' (or 'colour') option, if present."""
    if not variant:
        return ""
    options = getattr(variant, 'options', None)
    if options and isinstance(options, dict):
        for key in ('Color', 'color', 'Colour', 'colour'):
            if key in options:
                return options[key]
    return ""

@register.simple_tag
def render_icon(icon_customizations, element_id, default_class='fas fa-circle'):
    from django.utils.safestring import mark_safe

    data = {}
    if icon_customizations:
        key = str(element_id)
        if key in icon_customizations:
            data = icon_customizations[key] or {}

    icon_class = data.get('icon_class') or default_class
    color = data.get('color') or ''
    font_size = data.get('font_size') or ''

    style_parts = []
    if color:
        style_parts.append(f"color:{color}")
    if font_size:
        style_parts.append(f"font-size:{font_size}")
    style_attr = f' style="{";".join(style_parts)}"' if style_parts else ''

    return mark_safe(f'<i class="{icon_class}"{style_attr}></i>')


@register.filter
def variant_label(variant):
    if not variant:
        return "Option"
    options = getattr(variant, 'options', None)
    if options and isinstance(options, dict):
        parts = []
        for key, value in options.items():
            if value is None or value == '':
                continue
            parts.append(f"{key}: {value}")
        if parts:
            return ' · '.join(parts)
    opt_parts = []
    for attr in ('option1', 'option2', 'option3'):
        val = getattr(variant, attr, None)
        if val:
            opt_parts.append(str(val))
    if opt_parts:
        return ' · '.join(opt_parts)
    sku = getattr(variant, 'sku', None)
    if sku:
        return sku
    return "Option"

