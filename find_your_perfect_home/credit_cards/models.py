"""
Credit Card Payment Models for Uganda Rental Platform
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid
import json

class CreditCardProvider(models.Model):
    """Credit card payment providers for Uganda"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=100)
    
    # Provider configuration
    api_endpoint = models.URLField()
    api_key_encrypted = models.TextField(blank=True)
    webhook_secret = models.TextField(blank=True)
    
    # Supported card types
    supported_cards = models.JSONField(default=list, help_text="List of supported card types")
    
    # Transaction limits
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50000000)
    
    # Fees
    transaction_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.9)
    fixed_fee = models.DecimalField(max_digits=8, decimal_places=2, default=1500)  # UGX 1,500
    
    # Uganda-specific features
    supports_ugx = models.BooleanField(default=True, help_text="Supports UGX transactions")
    supports_usd = models.BooleanField(default=True, help_text="Supports USD transactions")
    supports_3ds = models.BooleanField(default=True, help_text="Supports 3D Secure")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.display_name
    
    class Meta:
        ordering = ['display_name']

class CreditCardPayment(models.Model):
    """Credit card transaction records"""
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('chargeback', 'Chargeback'),
    ]
    
    CARD_TYPES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('american_express', 'American Express'),
        ('discover', 'Discover'),
        ('unionpay', 'UnionPay'),
        ('other', 'Other'),
    ]
    
    # Reference to main payment
    payment = models.OneToOneField('payments.Payment', on_delete=models.CASCADE, related_name='credit_card')
    
    # Transaction details
    provider = models.ForeignKey(CreditCardProvider, on_delete=models.PROTECT)
    transaction_id = models.CharField(max_length=100, unique=True)
    provider_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Card details (encrypted)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    card_last_four = models.CharField(max_length=4)
    card_expiry_month = models.PositiveIntegerField()
    card_expiry_year = models.PositiveIntegerField()
    cardholder_name = models.CharField(max_length=100)
    
    # Billing details
    billing_address = models.JSONField(default=dict)
    billing_country = models.CharField(max_length=2, default='UG')  # Uganda default
    
    # Amount details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='UGX')
    fee_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    initiated_at = models.DateTimeField(auto_now_add=True)
    authorized_at = models.DateTimeField(null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Provider response
    provider_response = models.JSONField(default=dict)
    authorization_code = models.CharField(max_length=100, blank=True)
    fraud_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # 3D Secure
    requires_3ds = models.BooleanField(default=False)
    three_d_secure_url = models.URLField(blank=True)
    three_d_secure_completed = models.BooleanField(default=False)
    
    # Refund information
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.CharField(max_length=500, blank=True)
    refund_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.provider.display_name} - {self.card_last_four}"
    
    @property
    def is_successful(self):
        return self.status == 'completed'
    
    @property
    def is_pending(self):
        return self.status in ['initiated', 'processing', 'authorized']
    
    @property
    def masked_card_number(self):
        return f"****-****-****-{self.card_last_four}"
    
    def calculate_fee(self):
        """Calculate transaction fee"""
        fee = (self.amount * self.provider.transaction_fee_percentage) / 100
        fee += self.provider.fixed_fee
        return fee
    
    def save(self, *args, **kwargs):
        # Calculate fee before saving
        self.fee_amount = self.calculate_fee()
        self.net_amount = self.amount - self.fee_amount
        super().save(*args, **kwargs)

class SavedCreditCard(models.Model):
    """Saved credit cards for users"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_cards')
    
    # Card details (encrypted)
    card_type = models.CharField(max_length=20, choices=CreditCardPayment.CARD_TYPES)
    card_last_four = models.CharField(max_length=4)
    card_expiry_month = models.PositiveIntegerField()
    card_expiry_year = models.PositiveIntegerField()
    cardholder_name = models.CharField(max_length=100)
    
    # Token from provider
    provider_token = models.CharField(max_length=200)
    provider = models.ForeignKey(CreditCardProvider, on_delete=models.CASCADE)
    
    # Metadata
    is_default = models.BooleanField(default=False)
    nickname = models.CharField(max_length=50, blank=True)
    billing_address = models.JSONField(default=dict)
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.user.username} - {self.masked_card_number}"
    
    @property
    def masked_card_number(self):
        return f"****-****-****-{self.card_last_four}"
    
    @property
    def is_expired(self):
        from datetime import datetime
        return datetime(self.card_expiry_year, self.card_expiry_month, 1) < datetime.now()

class CreditCardVerification(models.Model):
    """Credit card verification and fraud detection"""
    
    payment = models.OneToOneField(CreditCardPayment, on_delete=models.CASCADE, related_name='verification')
    
    # Fraud detection
    fraud_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('very_high', 'Very High Risk'),
    ], default='low')
    
    # Verification checks
    cvv_verified = models.BooleanField(default=False)
    address_verified = models.BooleanField(default=False)
    zip_code_verified = models.BooleanField(default=False)
    
    # Device and location
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_fingerprint = models.CharField(max_length=100, blank=True)
    
    # Velocity checks
    transactions_last_hour = models.PositiveIntegerField(default=0)
    transactions_last_day = models.PositiveIntegerField(default=0)
    amount_last_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_last_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Manual review
    requires_manual_review = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_payments'
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Verification for {self.payment.card_last_four}"

class CreditCardTransactionLog(models.Model):
    """Detailed log of credit card transactions"""
    
    ACTION_TYPES = [
        ('payment_initiated', 'Payment Initiated'),
        ('payment_authorized', 'Payment Authorized'),
        ('payment_captured', 'Payment Captured'),
        ('payment_completed', 'Payment Completed'),
        ('payment_failed', 'Payment Failed'),
        ('refund_processed', 'Refund Processed'),
        ('chargeback_received', 'Chargeback Received'),
        ('fraud_detected', 'Fraud Detected'),
        ('3ds_initiated', '3D Secure Initiated'),
        ('3ds_completed', '3D Secure Completed'),
    ]
    
    provider = models.ForeignKey(CreditCardProvider, on_delete=models.CASCADE)
    transaction = models.ForeignKey(CreditCardPayment, on_delete=models.CASCADE, null=True, blank=True)
    
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    
    # Request/Response data
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    success = models.BooleanField(default=False)
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    
    # Security
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.provider.display_name} - {self.action_type} - {self.created_at}"

# Create default credit card providers
def create_default_credit_card_providers():
    """Create default credit card providers for Uganda"""
    providers_data = [
        {
            'name': 'Stripe',
            'code': 'STRIPE',
            'display_name': 'Stripe',
            'api_endpoint': 'https://api.stripe.com/v1',
            'supported_cards': ['visa', 'mastercard', 'american_express', 'discover'],
            'min_amount': 1000,
            'max_amount': 50000000,
            'transaction_fee_percentage': 2.9,
            'fixed_fee': 1500,
            'supports_ugx': True,
            'supports_usd': True,
            'supports_3ds': True,
        },
        {
            'name': 'Flutterwave',
            'code': 'FLUTTERWAVE',
            'display_name': 'Flutterwave',
            'api_endpoint': 'https://api.flutterwave.com/v3',
            'supported_cards': ['visa', 'mastercard', 'unionpay'],
            'min_amount': 1000,
            'max_amount': 20000000,
            'transaction_fee_percentage': 3.2,
            'fixed_fee': 1200,
            'supports_ugx': True,
            'supports_usd': True,
            'supports_3ds': True,
        },
        {
            'name': 'Paystack',
            'code': 'PAYSTACK',
            'display_name': 'Paystack',
            'api_endpoint': 'https://api.paystack.co',
            'supported_cards': ['visa', 'mastercard', 'unionpay'],
            'min_amount': 1000,
            'max_amount': 15000000,
            'transaction_fee_percentage': 2.5,
            'fixed_fee': 1000,
            'supports_ugx': True,
            'supports_usd': True,
            'supports_3ds': True,
        },
        {
            'name': 'DPO Uganda',
            'code': 'DPO_UGANDA',
            'display_name': 'DPO Uganda',
            'api_endpoint': 'https://secure.3gdirectpay.com',
            'supported_cards': ['visa', 'mastercard'],
            'min_amount': 2000,
            'max_amount': 10000000,
            'transaction_fee_percentage': 3.0,
            'fixed_fee': 800,
            'supports_ugx': True,
            'supports_usd': False,
            'supports_3ds': True,
        },
    ]
    
    for provider_data in providers_data:
        CreditCardProvider.objects.get_or_create(
            code=provider_data['code'],
            defaults=provider_data
        )
