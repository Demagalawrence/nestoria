"""
Credit Card Serializers
"""
from rest_framework import serializers
from .models import CreditCardProvider, CreditCardPayment, SavedCreditCard

class CreditCardProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCardProvider
        fields = [
            'id', 'code', 'display_name', 'supported_cards', 'min_amount', 'max_amount',
            'transaction_fee_percentage', 'fixed_fee', 'supports_ugx', 'supports_usd',
            'supports_3ds', 'is_active'
        ]
        read_only_fields = ['id']

class CreditCardInitiateSerializer(serializers.Serializer):
    """Serializer for initiating credit card payments"""
    booking_id = serializers.IntegerField(required=True)
    provider_code = serializers.CharField(required=True, max_length=20)
    card_data = serializers.JSONField(required=True)
    
    def validate_card_data(self, value):
        """Validate credit card data"""
        required_fields = ['card_number', 'cardholder_name', 'expiry_date', 'cvv']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"'{field}' is required in card_data")
        
        # Validate card number
        card_number = value['card_number'].replace('-', '').replace(' ', '')
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            raise serializers.ValidationError("Invalid card number")
        
        # Validate expiry date
        expiry_date = value['expiry_date']
        if not expiry_date or '/' not in expiry_date:
            raise serializers.ValidationError("Invalid expiry date format")
        
        # Validate CVV
        cvv = value['cvv']
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            raise serializers.ValidationError("Invalid CVV")
        
        return value
    
    def validate_provider_code(self, value):
        """Validate provider code exists"""
        if not CreditCardProvider.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(f"Provider {value} is not available")
        return value

class CreditCardPaymentSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='provider.display_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    fee_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    masked_card_number = serializers.CharField(read_only=True)
    
    class Meta:
        model = CreditCardPayment
        fields = [
            'id', 'transaction_id', 'provider', 'provider_display', 'card_type',
            'card_last_four', 'masked_card_number', 'cardholder_name',
            'amount', 'currency', 'fee_amount', 'net_amount',
            'status', 'status_display', 'initiated_at', 'authorized_at',
            'captured_at', 'completed_at', 'requires_3ds', 'three_d_secure_url'
        ]
        read_only_fields = [
            'id', 'provider_display', 'status_display', 'fee_amount', 
            'net_amount', 'masked_card_number'
        ]

class SavedCreditCardSerializer(serializers.Serializer):
    """Serializer for saving credit cards"""
    provider_code = serializers.CharField(required=True, max_length=20)
    card_data = serializers.JSONField(required=True)
    
    def validate_card_data(self, value):
        """Validate credit card data for saving"""
        required_fields = ['card_number', 'cardholder_name', 'expiry_date', 'cvv']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"'{field}' is required in card_data")
        
        # Validate card number
        card_number = value['card_number'].replace('-', '').replace(' ', '')
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            raise serializers.ValidationError("Invalid card number")
        
        # Validate expiry date
        expiry_date = value['expiry_date']
        if not expiry_date or '/' not in expiry_date:
            raise serializers.ValidationError("Invalid expiry date format")
        
        # Validate CVV
        cvv = value['cvv']
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            raise serializers.ValidationError("Invalid CVV")
        
        # Validate billing address if provided
        billing_address = value.get('billing_address', {})
        if billing_address:
            required_address_fields = ['country', 'city', 'address_line1']
            for field in required_address_fields:
                if field not in billing_address:
                    raise serializers.ValidationError(f"'{field}' is required in billing_address")
        
        return value
    
    def validate_provider_code(self, value):
        """Validate provider code exists"""
        if not CreditCardProvider.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(f"Provider {value} is not available")
        return value

class SavedCreditCardDetailSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='provider.display_name', read_only=True)
    masked_card_number = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SavedCreditCard
        fields = [
            'id', 'provider', 'provider_display', 'card_type', 'card_last_four',
            'masked_card_number', 'cardholder_name', 'card_expiry_month',
            'card_expiry_year', 'nickname', 'is_default', 'usage_count',
            'last_used_at', 'created_at', 'expires_at', 'is_expired'
        ]
        read_only_fields = [
            'id', 'provider_display', 'masked_card_number', 'is_expired',
            'usage_count', 'last_used_at', 'created_at'
        ]

class CreditCardPaymentDetailSerializer(serializers.ModelSerializer):
    """Detailed credit card payment serializer"""
    provider_display = serializers.CharField(source='provider.display_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    fee_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    masked_card_number = serializers.CharField(read_only=True)
    verification = serializers.SerializerMethodField()
    
    class Meta:
        model = CreditCardPayment
        fields = [
            'id', 'transaction_id', 'provider', 'provider_display', 'card_type',
            'card_last_four', 'masked_card_number', 'cardholder_name',
            'billing_address', 'amount', 'currency', 'fee_amount', 'net_amount',
            'status', 'status_display', 'initiated_at', 'authorized_at',
            'captured_at', 'completed_at', 'requires_3ds', 'three_d_secure_url',
            'authorization_code', 'fraud_score', 'refund_amount', 'refund_reason',
            'verification'
        ]
        read_only_fields = [
            'id', 'provider_display', 'status_display', 'fee_amount',
            'net_amount', 'masked_card_number', 'verification'
        ]
    
    def get_verification(self, obj):
        """Get verification details"""
        try:
            verification = obj.verification
            return {
                'fraud_score': verification.fraud_score,
                'risk_level': verification.risk_level,
                'cvv_verified': verification.cvv_verified,
                'address_verified': verification.address_verified,
                'requires_manual_review': verification.requires_manual_review
            }
        except:
            return None
