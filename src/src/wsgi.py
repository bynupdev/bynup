"""
WSGI config for src project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the parent directory (first src) to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from django.core.wsgi import get_wsgi_application

# Set the correct settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

application = get_wsgi_application()

# for production
app = application