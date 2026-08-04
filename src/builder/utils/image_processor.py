# builder/utils/image_processor.py
import threading
import time
import base64
import logging
from django.core.files.base import ContentFile
from django.utils import timezone
import uuid
# Add these imports at the top with your existing imports
import queue
from django.db import transaction
from django.core.cache import cache

logger = logging.getLogger(__name__)

class BackgroundImageProcessor:
    """Simple background thread for processing images"""
    
    _instance = None
    _lock = threading.Lock()
    _stop_flag = False
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.running = False
                cls._instance.queue = queue.Queue()
            return cls._instance
    
    def start(self):
        """Start the background processor thread"""
        if not self.running:
            self.running = True
            self._stop_flag = False
            thread = threading.Thread(target=self._process_loop, daemon=True)
            thread.start()
            logger.info("🔄 Background image processor started")
    
    def stop(self):
        """Stop the background processor"""
        self._stop_flag = True
        self.running = False
        logger.info("🛑 Background image processor stopped")
    
    def add_to_queue(self, page_id, image_data):
        """Add image data to processing queue"""
        self.queue.put({
            'page_id': page_id,
            'image_data': image_data,
            'attempts': 0,
            'added_at': timezone.now().isoformat()
        })
        logger.info(f"📥 Added image to queue. Queue size: {self.queue.qsize()}")
    
    def _process_loop(self):
        """Main processing loop"""
        from ..models import PublishedPage, BackgroundImage, ImageCustomization
        
        while not self._stop_flag:
            try:
                # Get item from queue with timeout
                try:
                    item = self.queue.get(timeout=5)
                except queue.Empty:
                    continue
                
                page_id = item['page_id']
                image_info = item['image_data']
                
                logger.info(f"🔄 Processing image for page {page_id}")
                
                try:
                    page = PublishedPage.objects.get(id=page_id)
                    
                    # Process based on type
                    if len(image_info) == 3:  # Background image
                        element_id, base64_data, page_name = image_info
                        self._process_background_image(page, element_id, base64_data, page_name)
                    
                    elif len(image_info) == 4:  # Custom image
                        element_id, base64_data, page_name, alt_text = image_info
                        self._process_custom_image(page, element_id, base64_data, page_name, alt_text)
                    
                    logger.info(f"✅ Successfully processed image for page {page_id}")
                    
                except PublishedPage.DoesNotExist:
                    logger.error(f"❌ Page {page_id} not found")
                except Exception as e:
                    logger.error(f"❌ Error processing image: {e}")
                    
                    # Retry logic
                    item['attempts'] += 1
                    if item['attempts'] < 3:
                        logger.info(f"🔄 Retry {item['attempts']} for page {page_id}")
                        time.sleep(5)  # Wait 5 seconds before retry
                        self.queue.put(item)
                
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"❌ Error in processing loop: {e}")
                time.sleep(1)
    
    def _process_background_image(self, page, element_id, base64_data, page_name):
        """Process a background image"""
        from ..models import BackgroundImage
        from django.core.files.base import ContentFile
        
        try:
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            
            # Clean element ID
            clean_id = self._extract_numeric_id(element_id)
            
            # Create image file
            image_file = ContentFile(
                base64.b64decode(imgstr),
                name=f"bg_{page_name}_{clean_id}_{uuid.uuid4()}.{ext}"
            )
            
            # Save to database
            bg, created = BackgroundImage.objects.update_or_create(
                page=page,
                element_id=clean_id,
                defaults={'image': image_file}
            )
            
            logger.info(f"✅ Saved background image for {element_id}")
            
        except Exception as e:
            logger.error(f"Error processing background image: {e}")
            raise
    
    def _process_custom_image(self, page, element_id, base64_data, page_name, alt_text):
        """Process a custom image"""
        from ..models import ImageCustomization
        from django.core.files.base import ContentFile
        
        try:
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            
            # Create image file
            image_file = ContentFile(
                base64.b64decode(imgstr),
                name=f"img_{page_name}_{element_id}_{uuid.uuid4()}.{ext}"
            )
            
            # Save to database
            img, created = ImageCustomization.objects.update_or_create(
                page=page,
                element_id=element_id,
                page_name=page_name,
                defaults={
                    'image': image_file,
                    'alt_text': alt_text
                }
            )
            
            logger.info(f"✅ Saved custom image for {element_id}")
            
        except Exception as e:
            logger.error(f"Error processing custom image: {e}")
            raise
    
    def _extract_numeric_id(self, element_id):
        """Extract numeric ID from element string"""
        import re
        if not element_id:
            return None
        match = re.search(r'\d+', str(element_id))
        return match.group() if match else None

# Create a global instance
processor = BackgroundImageProcessor()

# Function to start processor (call this when Django starts)
def start_processor():
    processor.start()

# Start processor when module loads
start_processor()