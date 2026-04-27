from rest_framework import serializers
from .models import RefundPolicy, Refund, RefundRequest

class RefundPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundPolicy
        fields = ['id', 'name', 'description', 'days_before_checkin_full', 
                 'days_before_checkin_partial', 'partial_refund_percentage',
                 'cancellation_fee', 'processing_fee', 'is_active', 'is_default']
        read_only_fields = ['id']

class RefundSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source='booking.booking_reference', read_only=True)
    user_name = serializers.CharField(source='booking.user.get_full_name', read_only=True)
    property_name = serializers.CharField(source='booking.rental_property.name', read_only=True)
    policy_name = serializers.CharField(source='refund_policy.name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    
    class Meta:
        model = Refund
        fields = ['id', 'booking_reference', 'user_name', 'property_name', 'policy_name',
                 'original_amount', 'refund_amount', 'refund_type', 'refund_percentage',
                 'cancellation_fee', 'processing_fee', 'status', 'processed_by_name',
                 'processed_at', 'refund_method', 'transaction_id', 'reason', 'admin_notes',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'booking_reference', 'user_name', 'property_name',
                           'policy_name', 'processed_by_name', 'processed_at', 'created_at', 'updated_at']

class RefundRequestSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source='booking.booking_reference', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    property_name = serializers.CharField(source='booking.rental_property.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    
    class Meta:
        model = RefundRequest
        fields = ['id', 'booking_reference', 'user_name', 'property_name', 'reason',
                 'additional_info', 'documents', 'status', 'reviewed_by_name',
                 'reviewed_at', 'admin_notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'booking_reference', 'user_name', 'property_name',
                           'reviewed_by_name', 'reviewed_at', 'created_at', 'updated_at']
