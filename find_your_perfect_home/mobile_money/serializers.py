"""
Mobile Money Serializers
"""
from rest_framework import serializers
from .models import MobileMoneyProvider, MobileMoneyPayment, MobileMoneyVerification

class MobileMoneyProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileMoneyProvider
        fields = [
            'id', 'code', 'display_name', 'min_amount', 'max_amount', 
            'daily_limit', 'transaction_fee_percentage', 'fixed_fee',
            'supports_ussd', 'supports_app', 'is_active'
        ]
        read_only_fields = ['id']

class MobileMoneyInitiateSerializer(serializers.Serializer):
    """Serializer for initiating mobile money payments"""
    booking_id = serializers.IntegerField(required=True)
    provider_code = serializers.CharField(required=True, max_length=20)
    phone_number = serializers.CharField(required=True, max_length=20)
    
    def validate_phone_number(self, value):
        """Validate Uganda phone number format"""
        import re
        uganda_phone_pattern = r'^\+256[0-9]{9}$|^07[0-9]{9}$'
        if not re.match(uganda_phone_pattern, value):
            raise serializers.ValidationError("Invalid Uganda phone number format. Use +256XXXXXXXX or 07XXXXXXXX format.")
        return value
    
    def validate_provider_code(self, value):
        """Validate provider code exists"""
        if not MobileMoneyProvider.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(f"Provider {value} is not available")
        return value

class MobileMoneyPaymentSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='provider.display_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    fee_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = MobileMoneyPayment
        fields = [
            'id', 'transaction_id', 'provider', 'provider_display', 'phone_number',
            'amount', 'fee_amount', 'net_amount', 'status', 'status_display',
            'initiated_at', 'confirmed_at', 'completed_at',
            'confirmation_code', 'ussd_session_id', 'retry_count'
        ]
        read_only_fields = ['id', 'provider_display', 'status_display', 'fee_amount', 'net_amount']

class MobileMoneyVerificationSerializer(serializers.Serializer):
    """Serializer for phone number verification"""
    provider_code = serializers.CharField(required=True, max_length=20)
    phone_number = serializers.CharField(required=True, max_length=20)
    
    def validate_phone_number(self, value):
        """Validate Uganda phone number format"""
        import re
        uganda_phone_pattern = r'^\+256[0-9]{9}$|^07[0-9]{9}$'
        if not re.match(uganda_phone_pattern, value):
            raise serializers.ValidationError("Invalid Uganda phone number format. Use +256XXXXXXXX or 07XXXXXXXX format.")
        return value

class MobileMoneyVerificationDetailSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='provider.display_name', read_only=True)
    verification_type_display = serializers.CharField(source='get_verification_type_display', read_only=True)
    
    class Meta:
        model = MobileMoneyVerification
        fields = [
            'id', 'provider', 'provider_display', 'phone_number',
            'verification_type', 'verification_type_display',
            'is_verified', 'created_at', 'verified_at', 'expires_at'
        ]
        read_only_fields = ['id', 'provider_display', 'verification_type_display']
