from django.contrib import admin
from .models import CreditCardProvider, CreditCardPayment, SavedCreditCard, CreditCardVerification, CreditCardTransactionLog

@admin.register(CreditCardProvider)
class CreditCardProviderAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'code', 'transaction_fee_percentage', 'fixed_fee', 'supports_3ds', 'is_active']
    list_filter = ['is_active', 'supports_3ds', 'supports_ugx', 'supports_usd']
    search_fields = ['display_name', 'code']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'display_name')
        }),
        ('Configuration', {
            'fields': ('api_endpoint', 'api_key_encrypted', 'webhook_secret', 'is_active')
        }),
        ('Supported Cards', {
            'fields': ('supported_cards',)
        }),
        ('Limits', {
            'fields': ('min_amount', 'max_amount')
        }),
        ('Fees', {
            'fields': ('transaction_fee_percentage', 'fixed_fee')
        }),
        ('Features', {
            'fields': ('supports_ugx', 'supports_usd', 'supports_3ds')
        })
    )

@admin.register(CreditCardPayment)
class CreditCardPaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'provider', 'card_type', 'card_last_four', 'amount', 'status', 'initiated_at']
    search_fields = ['transaction_id', 'card_last_four', 'payment__booking__id', 'cardholder_name']
    readonly_fields = ['transaction_id', 'fee_amount', 'net_amount', 'masked_card_number']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('payment', 'provider', 'transaction_id', 'provider_transaction_id')
        }),
        ('Card Information', {
            'fields': ('card_type', 'card_last_four', 'masked_card_number', 'cardholder_name', 'card_expiry_month', 'card_expiry_year')
        }),
        ('Billing Information', {
            'fields': ('billing_address', 'billing_country')
        }),
        ('Amount', {
            'fields': ('amount', 'currency', 'fee_amount', 'net_amount')
        }),
        ('Status', {
            'fields': ('status', 'initiated_at', 'authorized_at', 'captured_at', 'completed_at')
        }),
        ('Provider Response', {
            'fields': ('provider_response', 'authorization_code', 'fraud_score')
        }),
        ('3D Secure', {
            'fields': ('requires_3ds', 'three_d_secure_url', 'three_d_secure_completed')
        }),
        ('Refund Information', {
            'fields': ('refund_amount', 'refund_reason', 'refund_id')
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(payment__booking__user=request.user)

@admin.register(SavedCreditCard)
class SavedCreditCardAdmin(admin.ModelAdmin):
    list_display = ['user', 'card_type', 'masked_card_number', 'provider_display', 'is_default', 'usage_count', 'created_at']
    list_filter = ['card_type', 'is_default', 'provider', 'created_at']
    search_fields = ['user__username', 'cardholder_name', 'nickname']
    readonly_fields = ['created_at', 'updated_at', 'masked_card_number', 'is_expired']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'cardholder_name', 'nickname')
        }),
        ('Card Information', {
            'fields': ('card_type', 'card_last_four', 'masked_card_number', 'card_expiry_month', 'card_expiry_year')
        }),
        ('Provider Information', {
            'fields': ('provider', 'provider_token')
        }),
        ('Settings', {
            'fields': ('is_default', 'billing_address')
        }),
        ('Usage', {
            'fields': ('usage_count', 'last_used_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'expires_at')
        })
    )
    
    def provider_display(self, obj):
        return obj.provider.display_name
    provider_display.short_description = 'Provider'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(CreditCardVerification)
class CreditCardVerificationAdmin(admin.ModelAdmin):
    list_display = ['payment', 'risk_level', 'fraud_score', 'requires_manual_review', 'created_at']
    list_filter = ['risk_level', 'requires_manual_review', 'cvv_verified', 'address_verified', 'created_at']
    search_fields = ['payment__transaction_id', 'payment__card_last_four']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment',)
        }),
        ('Fraud Detection', {
            'fields': ('fraud_score', 'risk_level')
        }),
        ('Verification Checks', {
            'fields': ('cvv_verified', 'address_verified', 'zip_code_verified')
        }),
        ('Device Information', {
            'fields': ('ip_address', 'user_agent', 'device_fingerprint')
        }),
        ('Velocity Checks', {
            'fields': ('transactions_last_hour', 'transactions_last_day', 'amount_last_hour', 'amount_last_day')
        }),
        ('Manual Review', {
            'fields': ('reviewed_by', 'review_notes', 'reviewed_at')
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(payment__payment__booking__user=request.user)

@admin.register(CreditCardTransactionLog)
class CreditCardTransactionLogAdmin(admin.ModelAdmin):
    list_display = ['provider', 'action_type', 'success', 'created_at']
    list_filter = ['success', 'action_type', 'provider', 'created_at']
    search_fields = ['transaction__transaction_id', 'action_type']
    readonly_fields = ['created_at', 'request_data', 'response_data', 'processing_time_ms']
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
