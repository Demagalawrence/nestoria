from rest_framework import serializers
from .models import PropertyAnalytics, PlatformAnalytics, UserActivity

class PropertyAnalyticsSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    property_owner = serializers.CharField(source='property.owner.get_full_name', read_only=True)
    
    class Meta:
        model = PropertyAnalytics
        fields = ['property_name', 'property_owner', 'total_bookings', 'confirmed_bookings',
                 'cancelled_bookings', 'completed_bookings', 'total_revenue', 'monthly_revenue',
                 'average_booking_value', 'occupancy_rate', 'average_stay_duration',
                 'views_count', 'inquiries_count', 'conversion_rate', 'average_rating',
                 'total_reviews', 'last_updated']
        read_only_fields = ['last_updated']

class PlatformAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformAnalytics
        fields = ['date', 'new_users', 'active_users', 'total_users', 'new_properties',
                 'total_properties', 'approved_properties', 'new_bookings', 'confirmed_bookings',
                 'completed_bookings', 'daily_revenue', 'total_revenue', 'commission_earned',
                 'page_views', 'search_queries']
        read_only_fields = ['date']

class UserActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    booking_reference = serializers.CharField(source='booking.booking_reference', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = ['user_name', 'activity_type', 'description', 'ip_address', 'user_agent',
                 'property_name', 'booking_reference', 'created_at']
        read_only_fields = ['created_at']
