from django.contrib import admin
from .models import AdoptionPost

@admin.register(AdoptionPost)
class AdoptionPostAdmin(admin.ModelAdmin):
    list_display = ['pet', 'owner', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['pet__name', 'owner__username', 'additional_info']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Pet Information', {
            'fields': ('pet',)
        }),
        ('Adoption Details', {
            'fields': ('additional_info', 'requirements')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )
