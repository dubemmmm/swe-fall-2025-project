from django.contrib import admin
from .models import Post, Comment, CommunityAlert

# Register your models here.

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['user', 'text', 'created_at']
    readonly_fields = ['created_at']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'caption_preview', 'timestamp', 'comment_count']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'caption']
    readonly_fields = ['timestamp']
    inlines = [CommentInline]

    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'

    fieldsets = (
        ('Post Content', {
            'fields': ('user', 'caption', 'photo')
        }),
        ('Metadata', {
            'fields': ('timestamp',)
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'text_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'text']
    readonly_fields = ['created_at']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment'

    fieldsets = (
        ('Comment Details', {
            'fields': ('post', 'user', 'text')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

@admin.register(CommunityAlert)
class CommunityAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'user', 'location', 'is_active', 'created_at']
    list_filter = ['alert_type', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'location']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Alert Information', {
            'fields': ('user', 'alert_type', 'title', 'description')
        }),
        ('Pet Details', {
            'fields': ('pet_type', 'size', 'color_markings', 'photo')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Contact & Status', {
            'fields': ('contact_info', 'is_active', 'created_at')
        }),
    )
