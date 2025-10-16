from django.contrib import admin
from .models import MessageThread, Message

# Register your models here.

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ['sender', 'text', 'timestamp', 'is_read']
    readonly_fields = ['timestamp']
    can_delete = False

@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'playdate', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user1__username', 'user2__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MessageInline]

    fieldsets = (
        ('Thread Participants', {
            'fields': ('user1', 'user2', 'playdate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['thread', 'sender', 'text_preview', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp']
    search_fields = ['sender__username', 'text']
    readonly_fields = ['timestamp']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Message Preview'

    fieldsets = (
        ('Message Details', {
            'fields': ('thread', 'sender', 'text', 'photo')
        }),
        ('Status', {
            'fields': ('is_read', 'timestamp')
        }),
    )
