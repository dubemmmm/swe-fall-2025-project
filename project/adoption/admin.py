from django.contrib import admin
from .models import AdoptionPost

# Register your models here.

@admin.register(AdoptionPost)
class AdoptionPostAdmin(admin.ModelAdmin):
    list_display = ['pet', 'is_active', 'posted_at']
    list_filter = ['is_active', 'posted_at']
    search_fields = ['pet__name', 'pet__owner__username', 'additional_info']
    readonly_fields = ['posted_at']

    fieldsets = (
        ('Pet Information', {
            'fields': ('pet',)
        }),
        ('Adoption Details', {
            'fields': ('additional_info', 'adoption_requirements')
        }),
        ('Status', {
            'fields': ('is_active', 'posted_at')
        }),
    )
