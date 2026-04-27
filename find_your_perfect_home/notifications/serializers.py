from rest_framework import serializers
from .models import Notification, NotificationTemplate, NotificationPreference

class NotificationSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source='booking.booking_reference', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    payment_id = serializers.CharField(source='payment.payment_id', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'channel', 'title', 'message', 'is_read',
                 'email_sent', 'sms_sent', 'push_sent', 'booking_reference', 'property_name',
                 'payment_id', 'created_at', 'read_at']
        read_only_fields = ['id', 'created_at', 'read_at', 'email_sent', 'sms_sent', 'push_sent']

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
