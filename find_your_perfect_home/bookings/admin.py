from django.contrib import admin
from .models import Booking, BookingHistory, BookingPayment, BookingDocument, BookingReview

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'user', 'rental_property', 'room', 'status', 'payment_status', 'start_date', 'end_date', 'final_amount')
    list_filter = ('status', 'payment_status', 'booking_type', 'start_date', 'end_date')
    search_fields = ('booking_reference', 'user__username', 'rental_property__name', 'room__room_number')
    
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'rental_property', 'room', 'booking_reference', 'booking_type', 'booking_date')}),
        ('Stay Details', {'fields': ('start_date', 'end_date', 'total_months', 'total_days')}),
        ('Occupancy', {'fields': ('number_of_occupants', 'occupants_details')}),
        ('Pricing', {'fields': ('base_rent', 'monthly_rent', 'security_deposit', 'maintenance_charge', 'other_charges', 'total_amount', 'discount_amount', 'final_amount')}),
        ('Status', {'fields': ('status', 'payment_status')}),
        ('Additional Info', {'fields': ('special_requests', 'notes', 'cancellation_reason', 'cancellation_date')}),
        ('Documents', {'fields': ('id_proofs_submitted', 'agreement_signed', 'agreement_document')}),
        ('Check-in/Check-out', {'fields': ('check_in_date', 'check_out_date', 'actual_check_out_date')}),
        ('Agent Info', {'fields': ('agent', 'agent_commission')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'confirmed_at')}),
    )
    
    readonly_fields = ('booking_reference', 'booking_date', 'created_at', 'updated_at', 'confirmed_at')

@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'changed_by', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('booking__booking_reference', 'changed_by__username', 'description')
    readonly_fields = ('timestamp',)

@admin.register(BookingPayment)
class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'booking', 'amount', 'payment_mode', 'payment_status', 'payment_date')
    list_filter = ('payment_mode', 'payment_status', 'payment_date')
    search_fields = ('payment_reference', 'booking__booking_reference', 'transaction_id')
    
    fieldsets = (
        ('Basic Info', {'fields': ('booking', 'payment_reference', 'amount', 'payment_mode', 'payment_date')}),
        ('Transaction Details', {'fields': ('transaction_id', 'bank_name', 'cheque_number', 'upi_transaction_id', 'card_last_4_digits')}),
        ('Status', {'fields': ('payment_status',)}),
        ('Receipt', {'fields': ('receipt_uploaded', 'receipt_document')}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('payment_date', 'created_at', 'updated_at')

@admin.register(BookingDocument)
class BookingDocumentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'document_type', 'document_name', 'is_verified', 'uploaded_at')
    list_filter = ('document_type', 'is_verified')
    search_fields = ('booking__booking_reference', 'document_name', 'document_number')
    
    fieldsets = (
        ('Basic Info', {'fields': ('booking', 'document_type', 'document_name', 'document', 'document_number', 'expiry_date')}),
        ('Verification', {'fields': ('is_verified', 'verified_by', 'verification_date')}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('uploaded_at',)}),
    )
    
    readonly_fields = ('uploaded_at', 'verification_date')

@admin.register(BookingReview)
class BookingReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'user', 'rental_property', 'overall_rating', 'is_public', 'created_at')
    list_filter = ('overall_rating', 'is_public', 'is_verified')
    search_fields = ('booking__booking_reference', 'user__username', 'rental_property__name', 'title')
    
    fieldsets = (
        ('Basic Info', {'fields': ('booking', 'user', 'rental_property')}),
        ('Ratings', {'fields': ('cleanliness_rating', 'amenities_rating', 'safety_rating', 'location_rating', 'value_for_money_rating', 'overall_rating')}),
        ('Review Details', {'fields': ('title', 'review', 'pros', 'cons')}),
        ('Status', {'fields': ('is_public', 'is_verified', 'helpful_count')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
