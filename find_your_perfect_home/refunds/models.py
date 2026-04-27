from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class RefundPolicy(models.Model):
    CANCELLATION_TYPES = [
        ('full_refund', 'Full Refund'),
        ('partial_refund', 'Partial Refund'),
        ('no_refund', 'No Refund'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Cancellation rules based on days before check-in
    days_before_checkin_full = models.PositiveIntegerField(default=0)  # Days for full refund
    days_before_checkin_partial = models.PositiveIntegerField(default=0)  # Days for partial refund
    partial_refund_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # % for partial refund
    
    # Additional fees
    cancellation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def calculate_refund(self, booking, cancellation_date=None):
        """Calculate refund amount for a booking"""
        if not cancellation_date:
            cancellation_date = timezone.now().date()
        
        days_until_checkin = (booking.start_date - cancellation_date).days
        
        if days_until_checkin >= self.days_before_checkin_full:
            # Full refund
            refund_amount = booking.final_amount - self.cancellation_fee - self.processing_fee
            refund_type = 'full_refund'
        elif days_until_checkin >= self.days_before_checkin_partial:
            # Partial refund
            refund_percentage = self.partial_refund_percentage / 100
            refund_amount = (booking.final_amount * refund_percentage) - self.processing_fee
            refund_type = 'partial_refund'
        else:
            # No refund
            refund_amount = Decimal('0')
            refund_type = 'no_refund'
        
        return {
            'refund_amount': max(refund_amount, Decimal('0')),
            'refund_type': refund_type,
            'cancellation_fee': self.cancellation_fee,
            'processing_fee': self.processing_fee,
            'days_until_checkin': days_until_checkin
        }

class Refund(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    REFUND_TYPES = [
        ('full', 'Full Refund'),
        ('partial', 'Partial Refund'),
        ('cancellation_fee', 'Cancellation Fee Only'),
    ]
    
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='refund')
    refund_policy = models.ForeignKey(RefundPolicy, on_delete=models.PROTECT)
    
    # Refund details
    original_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_type = models.CharField(max_length=20, choices=REFUND_TYPES)
    refund_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Fees
    cancellation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Payment details
    refund_method = models.CharField(max_length=50, default='original')
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict)
    
    # Reason and notes
    reason = models.TextField()
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Refund for {self.booking.booking_reference} - {self.refund_amount}"
    
    def process_refund(self, processed_by=None):
        """Process the refund (would integrate with payment gateway)"""
        try:
            # Here you would integrate with Stripe or other payment gateway
            # For now, we'll just mark as processed
            
            self.status = 'processing'
            self.processed_by = processed_by
            self.save()
            
            # Simulate payment gateway processing
            import time
            time.sleep(1)  # Simulate API call
            
            # Mark as completed
            self.status = 'completed'
            self.processed_at = timezone.now()
            self.transaction_id = f"REF_{self.booking.booking_reference}_{int(timezone.now().timestamp())}"
            self.save()
            
            # Update booking status
            booking = self.booking
            booking.status = 'cancelled'
            booking.cancellation_date = timezone.now()
            booking.save()
            
            return True, "Refund processed successfully"
            
        except Exception as e:
            self.status = 'failed'
            self.gateway_response = {'error': str(e)}
            self.save()
            return False, str(e)

class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='refund_request')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Request details
    reason = models.TextField()
    additional_info = models.TextField(blank=True)
    
    # Supporting documents
    documents = models.JSONField(default=list)  # List of document URLs
    
    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_refund_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund Request for {self.booking.booking_reference} - {self.status}"
    
    def approve(self, reviewed_by, notes=""):
        """Approve refund request and create refund"""
        if self.status != 'pending':
            return False, "Request is not pending"
        
        # Get default refund policy
        policy = RefundPolicy.objects.filter(is_default=True).first()
        if not policy:
            return False, "No default refund policy found"
        
        # Calculate refund
        refund_calculation = policy.calculate_refund(self.booking)
        
        # Create refund
        refund = Refund.objects.create(
            booking=self.booking,
            refund_policy=policy,
            original_amount=self.booking.final_amount,
            refund_amount=refund_calculation['refund_amount'],
            refund_type=refund_calculation['refund_type'],
            cancellation_fee=refund_calculation['cancellation_fee'],
            processing_fee=refund_calculation['processing_fee'],
            reason=self.reason
        )
        
        # Update request status
        self.status = 'approved'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.admin_notes = notes
        self.save()
        
        return True, f"Refund approved: {refund.refund_amount}"
    
    def reject(self, reviewed_by, reason=""):
        """Reject refund request"""
        self.status = 'rejected'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.admin_notes = reason
        self.save()
        
        return True, "Refund request rejected"
