from django.contrib import admin
from .models import MobileMoneyProvider, MobileMoneyPayment, MobileMoneyVerification, MobileMoneyTransactionLog

@admin.register(MobileMoneyProvider)
class MobileMoneyProviderAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'code', 'transaction_fee_percentage', 'fixed_fee', 'is_active']
    list_filter = ['is_active', 'supports_ussd', 'supports_app']
    search_fields = ['display_name', 'code']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'display_name')
        }),
        ('Configuration', {
            'fields': ('api_endpoint', 'api_key_encrypted', 'is_active')
        }),
        ('Limits', {
            'fields': ('min_amount', 'max_amount', 'daily_limit')
        }),
        ('Fees', {
            'fields': ('transaction_fee_percentage', 'fixed_fee')
        }),
        ('Features', {
            'fields': ('supports_ussd', 'supports_app')
        })
    )

@admin.register(MobileMoneyPayment)
class MobileMoneyPaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'provider', 'phone_number', 'amount', 'status', 'initiated_at']
    search_fields = ['transaction_id', 'phone_number', 'payment__booking__id']
    readonly_fields = ['transaction_id', 'fee_amount', 'net_amount']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('payment', 'provider', 'transaction_id', 'phone_number')
        }),
        ('Amount', {
            'fields': ('amount', 'fee_amount', 'net_amount')
        }),
        ('Status', {
            'fields': ('status', 'initiated_at', 'confirmed_at', 'completed_at')
        }),
        ('Provider Response', {
            'fields': ('provider_response', 'confirmation_code', 'ussd_session_id')
        }),
        ('Retry Information', {
            'fields': ('retry_count', 'max_retries', 'next_retry_at')
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(payment__booking__user=request.user)

@admin.register(MobileMoneyVerification)
class MobileMoneyVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'phone_number', 'verification_type', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'provider', 'verification_type', 'created_at']
    search_fields = ['user__username', 'phone_number', 'verification_code']
    readonly_fields = ['verification_code', 'created_at', 'verified_at', 'expires_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(MobileMoneyTransactionLog)
class MobileMoneyTransactionLogAdmin(admin.ModelAdmin):
    list_display = ['provider', 'action_type', 'success', 'created_at']
    list_filter = ['success', 'action_type', 'provider', 'created_at']
    search_fields = ['transaction__transaction_id', 'action_type']
    readonly_fields = ['created_at', 'request_data', 'response_data', 'processing_time_ms']
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
