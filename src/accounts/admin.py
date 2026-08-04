from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, WebsiteUser, UserActivity, UserType

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_active', 'date_joined']
    list_filter = ['profile__user_type', 'is_active', 'is_staff', 'date_joined']
    
    def get_user_type(self, obj):
        return obj.profile.user_type.name if hasattr(obj, 'profile') else 'N/A'
    get_user_type.short_description = 'User Type'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(WebsiteUser)
class WebsiteUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'website', 'role', 'is_active', 'registered_at']
    list_filter = ['website', 'role', 'is_active', 'registered_at']
    search_fields = ['user__username', 'user__email', 'website__brand_name']
    raw_id_fields = ['user', 'website']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'ip_address', 'timestamp']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['timestamp']
