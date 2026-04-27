from django.contrib import admin
from .models import Payment, Receipt, Commission

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'amount', 'payment_method', 'payment_status', 'payment_date')
    list_filter = ('payment_method', 'payment_status', 'payment_date')
    search_fields = ('payment_id', 'booking__booking_reference', 'transaction_id')
    
    fieldsets = (
        ('Basic Info', {'fields': ('booking', 'payment_id', 'amount', 'payment_method', 'payment_status')}),
        ('Transaction Details', {'fields': ('transaction_id', 'gateway_response')}),
        ('Commission', {'fields': ('commission_percentage', 'commission_amount', 'net_payment')}),
        ('Timestamps', {'fields': ('payment_date', 'updated_at')}),
    )
    
    readonly_fields = ('payment_date', 'updated_at')

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'payment', 'receipt_link', 'is_sent', 'generated_date')
    list_filter = ('is_sent', 'generated_date')
    search_fields = ('receipt_number', 'payment__payment_id')
    
    fieldsets = (
        ('Basic Info', {'fields': ('payment', 'receipt_number', 'receipt_link')}),
        ('Status', {'fields': ('is_sent',)}),
        ('Timestamps', {'fields': ('generated_date',)}),
    )
    
    readonly_fields = ('generated_date',)

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('payment', 'property_owner', 'commission_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('payment__payment_id', 'property_owner__username')
    
    fieldsets = (
        ('Basic Info', {'fields': ('payment', 'property_owner', 'commission_amount')}),
        ('Status', {'fields': ('status', 'payout_date', 'payout_reference')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
