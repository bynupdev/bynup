# src/src/__init__.py
# The correct import path from the second src folder
from .celery_app import app as celery_app
import threading
import time
import logging

__all__ = ('celery_app',)

logger = logging.getLogger(__name__)

def start_image_processor_when_ready():
    """Wait for Django to be ready and then start the image processor"""
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            from django.apps import apps
            if apps.ready:
                from builder.utils.image_processor import start_processor
                start_processor()
                logger.info("Image processor started successfully")
                return
        except (ImportError, Exception) as e:
            logger.debug(f"Waiting for Django to be ready (attempt {attempt + 1}): {e}")
        
        time.sleep(1)
        attempt += 1
    
    logger.error("Failed to start image processor after 30 seconds")

processor_thread = threading.Thread(target=start_image_processor_when_ready, daemon=True)
processor_thread.start()