from django.contrib import admin
from django.utils.html import format_html
from .models import Playdate, PlaydateParticipant

# Register your models here.

class PlaydateParticipantInline(admin.TabularInline):
    model = PlaydateParticipant
    extra = 0
    readonly_fields = ['created_at', 'responded_at', 'status_display']
    fields = ['pet', 'user', 'status', 'status_display', 'created_at', 'responded_at']

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'INVITED': '#FFA500',
            'REQUESTED': '#007BFF',
            'ACCEPTED': '#28A745',
            'DECLINED': '#DC3545'
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status Display'


@admin.register(Playdate)
class PlaydateAdmin(admin.ModelAdmin):
    list_display = [
        'organizer_pet',
        'organizer',
        'scheduled_time',
        'location',
        'is_public',
        'status',
        'participant_count',
        'available_spots',
        'created_at'
    ]
    list_filter = ['status', 'is_public', 'scheduled_time', 'created_at']
    search_fields = ['organizer_pet__name', 'organizer__username', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at', 'participant_count', 'available_spots']
    inlines = [PlaydateParticipantInline]
    date_hierarchy = 'scheduled_time'

    fieldsets = (
        ('Basic Information', {
            'fields': ('organizer', 'organizer_pet', 'scheduled_time', 'location')
        }),
        ('Details', {
            'fields': ('description', 'max_participants', 'is_public')
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
        ('Participant Info', {
            'fields': ('participant_count', 'available_spots'),
            'classes': ('collapse',)
        }),
    )

    def participant_count(self, obj):
        """Display count of accepted participants"""
        count = obj.get_accepted_count()
        return format_html(
            '<span style="font-weight: bold;">{} / {}</span>',
            count,
            obj.max_participants - 1
        )
    participant_count.short_description = 'Accepted Participants'

    def available_spots(self, obj):
        """Display available spots"""
        spots = obj.get_available_spots()
        color = '#28A745' if spots > 0 else '#DC3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            spots
        )
    available_spots.short_description = 'Available Spots'

    def get_queryset(self, request):
        """Optimize queryset with related objects"""
        qs = super().get_queryset(request)
        return qs.select_related('organizer', 'organizer_pet').prefetch_related('participants')


@admin.register(PlaydateParticipant)
class PlaydateParticipantAdmin(admin.ModelAdmin):
    list_display = [
        'pet',
        'user',
        'playdate_info',
        'status_colored',
        'created_at',
        'responded_at'
    ]
    list_filter = ['status', 'created_at', 'responded_at']
    search_fields = [
        'pet__name',
        'user__username',
        'playdate__location',
        'playdate__organizer__username'
    ]
    readonly_fields = ['created_at', 'responded_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Participant Information', {
            'fields': ('playdate', 'user', 'pet')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'responded_at')
        }),
    )

    def playdate_info(self, obj):
        """Display playdate information"""
        return f"{obj.playdate.organizer_pet.name} at {obj.playdate.location}"
    playdate_info.short_description = 'Playdate'

    def status_colored(self, obj):
        """Display status with color coding"""
        colors = {
            'INVITED': '#FFA500',
            'REQUESTED': '#007BFF',
            'ACCEPTED': '#28A745',
            'DECLINED': '#DC3545'
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'

    def get_queryset(self, request):
        """Optimize queryset with related objects"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'playdate',
            'playdate__organizer',
            'playdate__organizer_pet',
            'user',
            'pet'
        )
