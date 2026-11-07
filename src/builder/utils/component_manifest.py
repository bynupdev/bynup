# builder/utils/component_manifest.py
import json
from functools import lru_cache
from pathlib import Path
from django.conf import settings


@lru_cache(maxsize=1)
def _load_manifest():
    path = Path(settings.BASE_DIR) / 'builder' / 'components' / 'component_manifest.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    flat = {}
    for cat in data.get('categories', []):
        for comp in cat.get('components', []):
            flat[comp['id']] = comp
    return flat


def get_component_meta(component_id):
    """Return the manifest entry for a component, or None."""
    return _load_manifest().get(component_id)


def clear_manifest_cache():
    """Call this in dev after editing the manifest."""
    _load_manifest.cache_clear()