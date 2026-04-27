from django.contrib import admin
from .models import USSDSession, USSDMenuItem, USSDRequestLog, USSDUser, USSDPropertyCache, USSDBooking

@admin.register(USSDSession)
class USSDSessionAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'session_id', 'current_screen', 'status', 'started_at', 'expires_at']
    list_filter = ['status', 'started_at', 'expires_at']
    search_fields = ['phone_number', 'session_id', 'user__username']
    readonly_fields = ['session_id', 'started_at', 'last_activity']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'phone_number', 'user', 'is_authenticated')
        }),
        ('State', {
            'fields': ('current_screen', 'status', 'session_data')
        }),
        ('Timing', {
            'fields': ('started_at', 'last_activity', 'expires_at')
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(USSDMenuItem)
class USSDMenuItemAdmin(admin.ModelAdmin):
    list_display = ['screen_id', 'title', 'action_type', 'is_active', 'created_at']
    list_filter = ['action_type', 'is_active', 'created_at']
    search_fields = ['screen_id', 'title', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('screen_id', 'title', 'description', 'is_active')
        }),
        ('Navigation', {
            'fields': ('parent_screen', 'back_screen')
        }),
        ('Menu Options', {
            'fields': ('options',)
        }),
        ('Input Handling', {
            'fields': ('requires_input', 'input_type', 'input_placeholder', 'input_validation')
        }),
        ('Actions', {
            'fields': ('action_type', 'action_data')
        }),
        ('Display Settings', {
            'fields': ('max_text_length', 'paginate')
        })
    )

@admin.register(USSDRequestLog)
class USSDRequestLogAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'request_text', 'response_screen', 'success', 'request_time']
    list_filter = ['success', 'response_screen', 'request_time']
    search_fields = ['phone_number', 'request_text', 'response_text']
    readonly_fields = ['request_time', 'processing_time_ms']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('session', 'phone_number', 'request_text', 'request_time')
        }),
        ('Response Information', {
            'fields': ('response_text', 'response_screen', 'success')
        }),
        ('Technical Details', {
            'fields': ('processing_time_ms', 'user_agent', 'ip_address', 'error_message')
        })
    )
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(USSDUser)
class USSDUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'phone_verified', 'preferred_language', 'total_sessions']
    list_filter = ['phone_verified', 'preferred_language', 'created_at']
    search_fields = ['user__username', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'phone_verified')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'sms_notifications', 'booking_confirmations', 'payment_reminders')
        }),
        ('Usage', {
            'fields': ('total_sessions', 'last_session', 'favorite_properties')
        }),
        ('Quick Actions', {
            'fields': ('quick_search_location', 'quick_search_price_range')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )

@admin.register(USSDPropertyCache)
class USSDPropertyCacheAdmin(admin.ModelAdmin):
    list_display = ['short_name', 'price_display', 'location_display', 'view_count', 'is_active']
    list_filter = ['is_active', 'last_updated']
    search_fields = ['short_name', 'property__name', 'keywords']
    readonly_fields = ['last_updated']
    
    fieldsets = (
        ('Property Information', {
            'fields': ('property', 'short_name', 'short_description')
        }),
        ('Display Information', {
            'fields': ('price_display', 'location_display', 'contact_display')
        }),
        ('Search Optimization', {
            'fields': ('keywords', 'tags')
        }),
        ('Analytics', {
            'fields': ('view_count', 'booking_count')
        }),
        ('Cache Management', {
            'fields': ('last_updated', 'expires_at', 'is_active')
        })
    )

@admin.register(USSDBooking)
class USSDBookingAdmin(admin.ModelAdmin):
    list_display = ['booking', 'session', 'confirmed_via_ussd', 'payment_method', 'created_at']
    list_filter = ['confirmed_via_ussd', 'payment_method', 'created_at']
    search_fields = ['booking__booking_reference', 'session__phone_number']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking', 'session')
        }),
        ('USSD Process', {
            'fields': ('search_query', 'property_selected', 'confirmed_via_ussd')
        }),
        ('Payment', {
            'fields': ('payment_method', 'confirmation_code')
        }),
        ('Status Updates', {
            'fields': ('status_updates',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_status_update')
        })
    )
