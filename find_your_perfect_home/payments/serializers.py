from rest_framework import serializers
from .models import Payment, Receipt, Commission
from bookings.models import Booking

class PaymentSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source='booking.booking_reference', read_only=True)
    user_name = serializers.CharField(source='booking.user.get_full_name', read_only=True)
    property_name = serializers.CharField(source='booking.rental_property.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'booking_reference', 'user_name', 'property_name', 'payment_id',
                 'amount', 'commission_percentage', 'commission_amount', 'net_payment',
                 'payment_status', 'payment_method', 'transaction_id', 'payment_date',
                 'updated_at']
        read_only_fields = ['id', 'booking_reference', 'user_name', 'property_name',
                           'payment_id', 'commission_amount', 'net_payment', 'payment_date',
                           'updated_at']

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'payment_method']
    
    def validate(self, attrs):
        booking = attrs['booking']
        
        # Check booking status
        if booking.status not in ['confirmed', 'completed']:
            raise serializers.ValidationError("Payment can only be made for confirmed bookings")
        
        return attrs
    
    def create(self, validated_data):
        booking = validated_data['booking']
        payment_method = validated_data['payment_method']
        
        # Generate payment ID
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8].upper()
        payment_id = f"PAY{timestamp}{unique_id}"
        
        payment = Payment.objects.create(
            booking=booking,
            payment_id=payment_id,
            amount=booking.final_amount,
            payment_method=payment_method,
            payment_status='pending'
        )
        
        return payment

class ReceiptSerializer(serializers.ModelSerializer):
    payment_id = serializers.CharField(source='payment.payment_id', read_only=True)
    booking_reference = serializers.CharField(source='payment.booking.booking_reference', read_only=True)
    amount = serializers.DecimalField(source='payment.amount', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Receipt
        fields = ['id', 'payment_id', 'booking_reference', 'receipt_number', 'receipt_link',
                 'amount', 'generated_date', 'is_sent']
        read_only_fields = ['id', 'payment_id', 'booking_reference', 'receipt_number',
                           'amount', 'generated_date', 'is_sent']

class CommissionSerializer(serializers.ModelSerializer):
    payment_id = serializers.CharField(source='payment.payment_id', read_only=True)
    property_owner_name = serializers.CharField(source='property_owner.get_full_name', read_only=True)
    property_name = serializers.CharField(source='payment.booking.rental_property.name', read_only=True)
    
    class Meta:
        model = Commission
        fields = ['id', 'payment_id', 'property_owner_name', 'property_name', 'commission_amount',
                 'status', 'payout_date', 'payout_reference', 'created_at', 'updated_at']
        read_only_fields = ['id', 'payment_id', 'property_owner_name', 'property_name',
                           'created_at', 'updated_at']
