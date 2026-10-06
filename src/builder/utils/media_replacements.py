"""
Server-side media replacements.

Hides <img class="...editable-image" data-image="N"> elements whose id
matches a media_replacement entry in injected_sections, and inserts a
<video> or <iframe> in the same slot with the same computed dimensions.

Zero template changes required.
"""
import re
import html as html_module


_IMG_RE = re.compile(
    r'<img\b[^>]*\bclass\s*=\s*"[^"]*editable-image[^"]*"[^>]*>',
    re.IGNORECASE,
)
_DATA_IMAGE_RE = re.compile(r'\bdata-image\s*=\s*"([^"]+)"', re.IGNORECASE)
_STYLE_RE = re.compile(r'\bstyle\s*=\s*"([^"]*)"', re.IGNORECASE)


def apply_media_replacements(html, injected_sections):
    """
    Hide replaced images and inject their video/embed siblings.
    Runs purely on the HTML string.
    """
    if not html or not injected_sections:
        return html

    replacements = [
        e for e in injected_sections
        if isinstance(e, dict) and e.get('type') == 'media_replacement'
    ]
    if not replacements:
        return html

    by_id = {}
    for entry in replacements:
        img_id = str(entry.get('target_image_id') or '')
        if img_id and entry.get('src'):
            by_id[img_id] = entry

    if not by_id:
        return html

    def _replace(match):
        img_tag = match.group(0)
        m = _DATA_IMAGE_RE.search(img_tag)
        if not m:
            return img_tag

        img_id = m.group(1).strip()
        entry = by_id.get(img_id)
        if not entry:
            return img_tag

        hidden_img = _make_hidden(img_tag)
        replacement_html = _build_media_html(entry, img_id)
        if not replacement_html:
            return img_tag

        return hidden_img + replacement_html

    return _IMG_RE.sub(_replace, html)


def _make_hidden(img_tag):
    """Add display:none and aria-hidden to an <img>."""
    if _STYLE_RE.search(img_tag):
        img_tag = _STYLE_RE.sub(
            lambda m: 'style="' + m.group(1).rstrip('; ')
                      + '; display:none !important;"',
            img_tag, count=1,
        )
    else:
        img_tag = img_tag[:-1].rstrip() + ' style="display:none !important;"' + img_tag[-1:]

    if 'aria-hidden' not in img_tag.lower():
        img_tag = img_tag[:-1].rstrip() + ' aria-hidden="true"' + img_tag[-1:]
    return img_tag


def _style_from_layout(layout):
    css_map = {
        'width':        'width',
        'height':       'height',
        'maxWidth':     'max-width',
        'minWidth':     'min-width',
        'borderRadius': 'border-radius',
        'margin':       'margin',
        'boxShadow':    'box-shadow',
    }
    parts = []
    for key, css_name in css_map.items():
        v = layout.get(key)
        if not v or v in ('auto', 'none', 'normal'):
            continue
        parts.append(f'{css_name}: {html_module.escape(str(v), quote=True)}')
    parts.append('object-fit: cover')
    parts.append('background: #000')
    parts.append('display: block')
    return parts


def _build_media_html(entry, img_id):
    kind = entry.get('media_kind') or 'video'
    src = html_module.escape(entry.get('src') or '', quote=True)
    if not src:
        return ''

    layout = entry.get('layout') or {}
    style_attr = '; '.join(_style_from_layout(layout))
    injected_id = html_module.escape(entry.get('id') or '', quote=True)
    target_id = html_module.escape(str(img_id), quote=True)

    if kind == 'embed':
        wrapper_style = 'position:relative; ' + style_attr
        if not layout.get('height') and not layout.get('width'):
            wrapper_style += '; aspect-ratio: 16 / 9'
        return (
            f'<div class="injected-media injected-media-embed" '
            f'data-injected-id="{injected_id}" '
            f'data-image-replaced="{target_id}" '
            f'style="{wrapper_style}">'
            f'<iframe src="{src}" frameborder="0" allowfullscreen '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
            f'gyroscope; picture-in-picture" '
            f'style="position:absolute; inset:0; width:100%; height:100%; border:0;">'
            f'</iframe></div>'
        )

    attrs = []
    if entry.get('autoplay'):       attrs.append('autoplay')
    if entry.get('loop'):           attrs.append('loop')
    if entry.get('muted', True):    attrs.append('muted')
    if entry.get('controls', True): attrs.append('controls')
    attrs.append('playsinline')
    attrs.append('preload="metadata"')
    attr_str = ' '.join(attrs)

    poster_attr = ''
    if entry.get('poster_url'):
        poster_attr = ' poster="' + html_module.escape(entry['poster_url'], quote=True) + '"'

    return (
        f'<video class="injected-media injected-media-video" '
        f'data-injected-id="{injected_id}" '
        f'data-image-replaced="{target_id}" '
        f'src="{src}" {attr_str}{poster_attr} '
        f'style="{style_attr}"></video>'
    )


_PUBLIC_CSS = (
    '<style id="bynup-media-replacements">'
    '.injected-media{display:block;max-width:100%;}'
    '.injected-media-video{object-fit:cover;background:#000;}'
    '.injected-media-embed{position:relative;overflow:hidden;}'
    '.injected-media-embed iframe{position:absolute;inset:0;width:100%;height:100%;border:0;}'
    '</style>'
)


def inject_public_css(html):
    """Add the media-replacement stylesheet to <head> once."""
    if 'id="bynup-media-replacements"' in html:
        return html
    if '</head>' in html:
        return html.replace('</head>', _PUBLIC_CSS + '</head>', 1)
    return _PUBLIC_CSS + html