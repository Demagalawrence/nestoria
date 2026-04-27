from django.db import models
from django.conf import settings
from bookings.models import Booking

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payment_records')
    payment_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_payment = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict)
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.booking}"
    
    def save(self, *args, **kwargs):
        if self.amount:
            from decimal import Decimal
            self.commission_amount = (self.amount * Decimal(self.commission_percentage)) / Decimal('100')
            self.net_payment = self.amount - self.commission_amount
        super().save(*args, **kwargs)
    
    def generate_receipt_number(self):
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"RCT-{timestamp}-{unique_id}"

class Receipt(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_link = models.URLField(blank=True)
    generated_date = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Receipt {self.receipt_number}"
    
    def generate_receipt_number(self):
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"RCT-{timestamp}-{unique_id}"

class Commission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='commissions')
    property_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payout_date = models.DateTimeField(null=True, blank=True)
    payout_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Commission - {self.property_owner.username} - {self.commission_amount}"
