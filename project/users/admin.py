from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields to display in the admin list view
    list_display = ['username', 'email', 'profile_name', 'location', 'created_at']
    list_filter = ['created_at', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'profile_name', 'location']

    # Fields to display in the admin detail view
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('profile_name', 'profile_photo', 'phone_number', 'bio')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
    )

    # Fields to display when creating a new user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile Information', {
            'fields': ('profile_name', 'profile_photo', 'phone_number', 'bio')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
    )
