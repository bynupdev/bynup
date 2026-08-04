# # src/src/celery_app.py
# import os
# from celery import Celery
# from celery.schedules import crontab

# # Set the default Django settings module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

# app = Celery('src')

# # Use CELERY_ prefix in settings.py
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Automatically find tasks.py in your apps
# app.autodiscover_tasks()

# # 6-Hour Schedule Configuration
# app.conf.beat_schedule = {
#     'sync-cj-stock-6-hours': {
#         'task': 'builder.tasks.sync_all_cj_stocks',
#         'schedule': crontab(minute=0, hour='*/6'), # 12am, 6am, 12pm, 6pm
#     },
# }