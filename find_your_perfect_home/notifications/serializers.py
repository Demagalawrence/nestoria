from rest_framework import serializers
from .models import Notification, NotificationTemplate, NotificationPreference

class NotificationSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(read_only=True)
    property_id = serializers.IntegerField(read_only=True)
    booking_reference = serializers.CharField(source='booking.booking_reference', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    payment_id = serializers.CharField(source='payment.payment_id', read_only=True)
    action_url = serializers.SerializerMethodField()
    action_label = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'channel', 'title', 'message', 'is_read',
                 'email_sent', 'sms_sent', 'push_sent', 'booking_id', 'property_id',
                 'booking_reference', 'property_name', 'payment_id', 'action_url',
                 'action_label', 'created_at', 'read_at']
        read_only_fields = ['id', 'created_at', 'read_at', 'email_sent', 'sms_sent', 'push_sent']

    def get_action_url(self, obj):
        if obj.notification_type == 'review_requested' and obj.property_id:
            return f'/reviews/{obj.property_id}?rate=1&notification={obj.id}'
        if obj.booking_id:
            return f'/payment/{obj.booking_id}'
        if obj.property_id:
            return f'/property/{obj.property_id}'
        return ''

    def get_action_label(self, obj):
        if obj.notification_type == 'review_requested':
            return 'Rate Services'
        if obj.notification_type.startswith('payment'):
            return 'View Payment'
        if obj.notification_type.startswith('booking'):
            return 'View Booking'
        if obj.property_id:
            return 'View Property'
        return ''

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'notification_type', 'channel', 'subject_template', 
                 'message_template', 'is_active']
        read_only_fields = ['id']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['email_notifications', 'sms_notifications', 'push_notifications',
                 'booking_updates', 'payment_updates', 'property_updates', 'marketing_emails']
