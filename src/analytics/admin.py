from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(WebsiteAnalytics)

admin.site.register(PageView)
admin.site.register(Event)
admin.site.register(Conversion)