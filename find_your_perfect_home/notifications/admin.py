from django.contrib import admin
from .models import Notification, NotificationTemplate, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'channel', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'channel', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'notification_type', 'channel', 'title', 'message')}),
        ('Status', {'fields': ('is_read', 'email_sent', 'sms_sent', 'push_sent')}),
        ('Related Objects', {'fields': ('booking', 'property', 'payment')}),
        ('Timestamps', {'fields': ('created_at', 'read_at')}),
    )

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'channel', 'is_active', 'created_at')
    list_filter = ('notification_type', 'channel', 'is_active')
    search_fields = ('notification_type', 'subject_template')
    
    fieldsets = (
        ('Basic Info', {'fields': ('notification_type', 'channel', 'is_active')}),
        ('Templates', {'fields': ('subject_template', 'message_template')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'sms_notifications', 'push_notifications')
    list_filter = ('email_notifications', 'sms_notifications', 'push_notifications')
    search_fields = ('user__username',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Channel Preferences', {'fields': ('email_notifications', 'sms_notifications', 'push_notifications')}),
        ('Content Preferences', {'fields': ('booking_updates', 'payment_updates', 'property_updates', 'marketing_emails')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
