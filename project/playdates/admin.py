from django.contrib import admin
from .models import Playdate

# Register your models here.

@admin.register(Playdate)
class PlaydateAdmin(admin.ModelAdmin):
    list_display = ['pet', 'organizer', 'scheduled_time', 'location', 'status', 'created_at']
    list_filter = ['status', 'scheduled_time', 'created_at']
    search_fields = ['pet__name', 'organizer__username', 'location']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Playdate Details', {
            'fields': ('pet', 'organizer', 'scheduled_time', 'location')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )
