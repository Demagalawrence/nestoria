from django.contrib import admin
from .models import PropertyAnalytics, PlatformAnalytics, UserActivity

@admin.register(PropertyAnalytics)
class PropertyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('property', 'total_bookings', 'occupancy_rate', 'total_revenue', 'average_rating', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('property__name', 'property__owner__username')
    readonly_fields = ('last_updated',)
    
    fieldsets = (
        ('Property', {'fields': ('property',)}),
        ('Booking Statistics', {'fields': ('total_bookings', 'confirmed_bookings', 'cancelled_bookings', 'completed_bookings')}),
        ('Revenue Statistics', {'fields': ('total_revenue', 'monthly_revenue', 'average_booking_value')}),
        ('Performance Metrics', {'fields': ('occupancy_rate', 'average_stay_duration', 'views_count', 'inquiries_count', 'conversion_rate')}),
        ('Rating Statistics', {'fields': ('average_rating', 'total_reviews')}),
        ('Timestamps', {'fields': ('last_updated',)}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'owner':
            return qs.filter(property__owner=request.user)
        return qs

@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'new_users', 'total_properties', 'new_bookings', 'daily_revenue')
    list_filter = ('date',)
    readonly_fields = ('date',)
    
    fieldsets = (
        ('Date', {'fields': ('date',)}),
        ('User Statistics', {'fields': ('new_users', 'active_users', 'total_users')}),
        ('Property Statistics', {'fields': ('new_properties', 'total_properties', 'approved_properties')}),
        ('Booking Statistics', {'fields': ('new_bookings', 'confirmed_bookings', 'completed_bookings')}),
        ('Revenue Statistics', {'fields': ('daily_revenue', 'total_revenue', 'commission_earned')}),
        ('Activity', {'fields': ('page_views', 'search_queries')}),
    )

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'property', 'booking', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'description', 'property__name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Activity', {'fields': ('activity_type', 'description')}),
        ('Related Objects', {'fields': ('property', 'booking')}),
        ('Request Info', {'fields': ('ip_address', 'user_agent')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
