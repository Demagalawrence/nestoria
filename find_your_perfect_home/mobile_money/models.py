"""
Mobile Money Models for Uganda Payment Integration
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid
import json

class MobileMoneyProvider(models.Model):
    """Mobile Money Providers in Uganda"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=100)
    
    # Provider configuration
    api_endpoint = models.URLField(blank=True)
    api_key_encrypted = models.TextField(blank=True)
    supports_ussd = models.BooleanField(default=False)
    supports_app = models.BooleanField(default=True)
    
    # Transaction limits
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=5000000)
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2, default=10000000)
    
    # Fees
    transaction_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)
    fixed_fee = models.DecimalField(max_digits=8, decimal_places=2, default=500)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.display_name} ({self.code})"
    
    class Meta:
        ordering = ['display_name']

class MobileMoneyPayment(models.Model):
    """Mobile Money Transaction Records"""
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Reference to main payment
    payment = models.OneToOneField('payments.Payment', on_delete=models.CASCADE, related_name='mobile_money')
    
    # Transaction details
    provider = models.ForeignKey(MobileMoneyProvider, on_delete=models.PROTECT)
    transaction_id = models.CharField(max_length=100, unique=True)
    external_reference = models.CharField(max_length=100, blank=True)
    
    # User details
    phone_number = models.CharField(max_length=20)
    phone_number_verified = models.BooleanField(default=False)
    
    # Amount details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    initiated_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Provider response
    provider_response = models.JSONField(default=dict)
    confirmation_code = models.CharField(max_length=20, blank=True)
    ussd_session_id = models.CharField(max_length=100, blank=True)
    
    # Retry mechanism
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.provider.display_name} - {self.transaction_id}"
    
    @property
    def is_successful(self):
        return self.status == 'completed'
    
    @property
    def is_pending(self):
        return self.status in ['initiated', 'pending', 'confirmed']
    
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

class MobileMoneyVerification(models.Model):
    """Phone Number Verification for Mobile Money"""
    
    VERIFICATION_TYPES = [
        ('ussd', 'USSD Code'),
        ('sms', 'SMS Code'),
        ('app', 'In-App Verification'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.ForeignKey(MobileMoneyProvider, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES)
    verification_code = models.CharField(max_length=10)
    ussd_code = models.CharField(max_length=20, blank=True)
    
    is_verified = models.BooleanField(default=False)
    verification_attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def can_attempt_verification(self):
        return (not self.is_verified and 
                not self.is_expired() and 
                self.verification_attempts < self.max_attempts)

class MobileMoneyTransactionLog(models.Model):
    """Detailed log of all mobile money transactions"""
    
    ACTION_TYPES = [
        ('payment_initiated', 'Payment Initiated'),
        ('payment_completed', 'Payment Completed'),
        ('payment_failed', 'Payment Failed'),
        ('refund_processed', 'Refund Processed'),
        ('verification_sent', 'Verification Sent'),
        ('verification_completed', 'Verification Completed'),
        ('ussd_session', 'USSD Session'),
    ]
    
    provider = models.ForeignKey(MobileMoneyProvider, on_delete=models.CASCADE)
    transaction = models.ForeignKey(MobileMoneyPayment, on_delete=models.CASCADE, null=True, blank=True)
    
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    
    # Log details
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    success = models.BooleanField(default=False)
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.provider.display_name} - {self.action_type} - {self.created_at}"

# Initialize default mobile money providers
def create_default_providers():
    """Create default Uganda mobile money providers"""
    providers_data = [
        {
            'name': 'MTN Mobile Money',
            'code': 'MTN_MOMO',
            'display_name': 'MTN MoMo',
            'api_endpoint': 'https://momoapi.mtn.co.ug',
            'supports_ussd': True,
            'supports_app': True,
            'min_amount': 1000,
            'max_amount': 5000000,
            'daily_limit': 10000000,
            'transaction_fee_percentage': 2.5,
            'fixed_fee': 500,
        },
        {
            'name': 'Airtel Money',
            'code': 'AIRTEL_MONEY',
            'display_name': 'Airtel Money',
            'api_endpoint': 'https://money.airtel.com',
            'supports_ussd': True,
            'supports_app': True,
            'min_amount': 1000,
            'max_amount': 4000000,
            'daily_limit': 8000000,
            'transaction_fee_percentage': 2.0,
            'fixed_fee': 400,
        },
        {
            'name': 'Stanbic Mobile',
            'code': 'STANBIC_MOBILE',
            'display_name': 'Stanbic Mobile Banking',
            'api_endpoint': 'https://mobile.stanbicbank.co.ug',
            'supports_ussd': True,
            'supports_app': True,
            'min_amount': 5000,
            'max_amount': 10000000,
            'daily_limit': 20000000,
            'transaction_fee_percentage': 1.5,
            'fixed_fee': 1000,
        },
        {
            'name': 'Centenary Mobile',
            'code': 'CENTENARY_MOBILE',
            'display_name': 'CenteMobile',
            'api_endpoint': 'https://mobile.centenarybank.co.ug',
            'supports_ussd': True,
            'supports_app': True,
            'min_amount': 2000,
            'max_amount': 7000000,
            'daily_limit': 15000000,
            'transaction_fee_percentage': 2.0,
            'fixed_fee': 800,
        },
        {
            'name': 'DFCU Mobile',
            'code': 'DFCU_MOBILE',
            'display_name': 'DFCU Mobile',
            'api_endpoint': 'https://mobile.dfcuBank.co.ug',
            'supports_ussd': True,
            'supports_app': True,
            'min_amount': 3000,
            'max_amount': 8000000,
            'daily_limit': 12000000,
            'transaction_fee_percentage': 1.8,
            'fixed_fee': 600,
        },
    ]
    
    for provider_data in providers_data:
        MobileMoneyProvider.objects.get_or_create(
            code=provider_data['code'],
            defaults=provider_data
        )
