from django.contrib import admin
from .models import RefundPolicy, Refund, RefundRequest

@admin.register(RefundPolicy)
class RefundPolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'days_before_checkin_full', 'days_before_checkin_partial', 
                   'partial_refund_percentage', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'description', 'is_active', 'is_default')}),
        ('Cancellation Rules', {'fields': ('days_before_checkin_full', 'days_before_checkin_partial',
                                         'partial_refund_percentage')}),
        ('Fees', {'fields': ('cancellation_fee', 'processing_fee')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('booking', 'refund_amount', 'refund_type', 'status', 'processed_by', 'created_at')
    list_filter = ('status', 'refund_type', 'created_at')
    search_fields = ('booking__booking_reference', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'processed_at')
    
    fieldsets = (
        ('Basic Info', {'fields': ('booking', 'refund_policy', 'original_amount', 'refund_amount',
                                 'refund_type', 'refund_percentage')}),
        ('Fees', {'fields': ('cancellation_fee', 'processing_fee')}),
        ('Status', {'fields': ('status', 'processed_by', 'processed_at')}),
        ('Payment Details', {'fields': ('refund_method', 'transaction_id', 'gateway_response')}),
        ('Reason & Notes', {'fields': ('reason', 'admin_notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'owner':
            from bookings.models import Booking
            from properties.models import Property
            user_properties = Property.objects.filter(owner=request.user)
            property_ids = user_properties.values_list('id', flat=True)
            booking_ids = Booking.objects.filter(rental_property__in=property_ids).values_list('id', flat=True)
            return qs.filter(booking_id__in=booking_ids)
        return qs

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('booking', 'user', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('booking__booking_reference', 'user__username', 'reason')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')
    
    fieldsets = (
        ('Basic Info', {'fields': ('booking', 'user', 'status')}),
        ('Request Details', {'fields': ('reason', 'additional_info', 'documents')}),
        ('Review', {'fields': ('reviewed_by', 'reviewed_at', 'admin_notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'owner':
            from properties.models import Property
            user_properties = Property.objects.filter(owner=request.user)
            property_ids = user_properties.values_list('id', flat=True)
            return qs.filter(booking__rental_property__in=property_ids)
        return qs
