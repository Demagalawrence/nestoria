from rest_framework import serializers
from django.utils import timezone
from .models import Booking, BookingPayment, BookingHistory, BookingDocument, BookingReview
from properties.models import Property, Room

class BookingSerializer(serializers.ModelSerializer):
    rental_property = serializers.PrimaryKeyRelatedField(read_only=True)
    room = serializers.PrimaryKeyRelatedField(read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    property_name = serializers.CharField(source='rental_property.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    is_active = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    total_paid_amount = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = ['id', 'booking_reference', 'rental_property', 'room', 'user_name', 'property_name', 'room_number',
                 'booking_type', 'booking_date', 'start_date', 'end_date', 'total_months',
                 'total_days', 'number_of_occupants', 'base_rent', 'monthly_rent',
                 'security_deposit', 'maintenance_charge', 'other_charges', 'total_amount',
                 'discount_amount', 'final_amount', 'status', 'payment_status',
                 'special_requests', 'notes', 'check_in_date', 'check_out_date',
                 'actual_check_out_date', 'is_active', 'is_upcoming', 'is_completed',
                 'total_paid_amount', 'remaining_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'booking_reference', 'rental_property', 'room', 'user_name', 'property_name',
                           'room_number', 'is_active', 'is_upcoming', 'is_completed',
                           'total_paid_amount', 'remaining_amount', 'created_at', 'updated_at']

class BookingCreateSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), required=False, allow_null=True)
    ACTIVE_BOOKING_STATUSES = ('pending', 'confirmed')
    
    class Meta:
        model = Booking
        fields = ['id', 'booking_reference', 'rental_property', 'room', 'booking_type', 'start_date', 'end_date',
                 'number_of_occupants', 'occupants_details', 'base_rent', 'monthly_rent',
                 'security_deposit', 'maintenance_charge', 'other_charges', 'discount_amount',
                 'special_requests', 'notes']
        read_only_fields = ['id', 'booking_reference']
    
    def validate(self, attrs):
        room = attrs.get('room', self.instance.room if self.instance else None)
        start_date = attrs.get('start_date', self.instance.start_date if self.instance else None)
        end_date = attrs.get('end_date', self.instance.end_date if self.instance else None)
        number_of_occupants = attrs.get(
            'number_of_occupants',
            self.instance.number_of_occupants if self.instance else 1
        )
        rental_property = attrs.get(
            'rental_property',
            self.instance.rental_property if self.instance else None
        )

        if not start_date or not end_date:
            return attrs
        
        # Check date validity
        if start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")
        
        if start_date < timezone.now().date():
            raise serializers.ValidationError("Start date cannot be in the past")

        if room:
            if rental_property and room.rental_property_id != rental_property.id:
                raise serializers.ValidationError("Room does not belong to the selected property")
            
            # Check if room is available
            if not room.is_available:
                raise serializers.ValidationError("Room is not available")
            
            # Check if room has enough capacity
            if number_of_occupants > room.available_beds:
                raise serializers.ValidationError(f"Room only has {room.available_beds} available beds")
            
            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                room=room,
                status__in=self.ACTIVE_BOOKING_STATUSES,
                start_date__lt=end_date,
                end_date__gt=start_date
            )
            if self.instance:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
            
            if overlapping_bookings.exists():
                raise serializers.ValidationError("Room is already booked for these dates")
        else:
            if not rental_property:
                raise serializers.ValidationError("Property is required")

            if number_of_occupants < rental_property.min_occupancy:
                raise serializers.ValidationError(
                    f"Property requires at least {rental_property.min_occupancy} occupants"
                )

            if number_of_occupants > rental_property.max_occupancy:
                raise serializers.ValidationError(
                    f"Property allows at most {rental_property.max_occupancy} occupants"
                )
            
            # Property-level booking - check property availability
            if rental_property.available_rooms <= 0:
                raise serializers.ValidationError("Property is fully booked")
            
            # Check property-level capacity for overlapping dates. A property can
            # accept overlapping bookings until all rooms are reserved.
            overlapping_bookings = Booking.objects.filter(
                rental_property=rental_property,
                status__in=self.ACTIVE_BOOKING_STATUSES,
                start_date__lt=end_date,
                end_date__gt=start_date
            )
            if self.instance:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
            
            if overlapping_bookings.count() >= rental_property.total_rooms:
                raise serializers.ValidationError("Property is fully booked for these dates")
            
        return attrs

class BookingDetailSerializer(BookingSerializer):
    occupants_details = serializers.JSONField()
    cancellation_reason = serializers.CharField(read_only=True)
    cancellation_date = serializers.DateTimeField(read_only=True)
    id_proofs_submitted = serializers.BooleanField(read_only=True)
    agreement_signed = serializers.BooleanField(read_only=True)
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    agent_commission = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    confirmed_at = serializers.DateTimeField(read_only=True)
    
    class Meta(BookingSerializer.Meta):
        fields = BookingSerializer.Meta.fields + ['occupants_details', 'cancellation_reason',
                 'cancellation_date', 'id_proofs_submitted', 'agreement_signed',
                 'agreement_document', 'agent_name', 'agent_commission', 'confirmed_at']

class BookingPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingPayment
        fields = ['id', 'payment_reference', 'amount', 'payment_mode', 'payment_date',
                 'transaction_id', 'bank_name', 'cheque_number', 'upi_transaction_id',
                 'card_last_4_digits', 'payment_status', 'receipt_uploaded',
                 'receipt_document', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'payment_reference', 'payment_date', 'created_at', 'updated_at']

class BookingDocumentSerializer(serializers.ModelSerializer):
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    
    class Meta:
        model = BookingDocument
        fields = ['id', 'document_type', 'document_name', 'document', 'document_number',
                 'expiry_date', 'is_verified', 'verified_by_name', 'verification_date',
                 'notes', 'uploaded_at']
        read_only_fields = ['id', 'is_verified', 'verified_by_name', 'verification_date', 'uploaded_at']

class BookingReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    property_name = serializers.CharField(source='rental_property.name', read_only=True)
    
    class Meta:
        model = BookingReview
        fields = ['id', 'cleanliness_rating', 'amenities_rating', 'safety_rating',
                 'location_rating', 'value_for_money_rating', 'overall_rating', 'title',
                 'review', 'pros', 'cons', 'is_public', 'is_verified', 'helpful_count',
                 'user_name', 'property_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'overall_rating', 'is_verified', 'helpful_count',
                           'user_name', 'property_name', 'created_at', 'updated_at']

class BookingHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = BookingHistory
        fields = ['id', 'changed_by_name', 'action', 'old_status', 'new_status',
                 'description', 'timestamp', 'ip_address']
        read_only_fields = ['id', 'changed_by_name', 'timestamp', 'ip_address']
