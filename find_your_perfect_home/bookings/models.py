from django.db import models
from django.conf import settings
from properties.models import Room, Property

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected'),
    ]
    
    BOOKING_TYPE_CHOICES = [
        ('direct', 'Direct Booking'),
        ('agent', 'Through Agent'),
        ('walk_in', 'Walk In'),
        ('online', 'Online Platform'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial Paid'),
        ('fully_paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    rental_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    
    # Booking Details
    booking_reference = models.CharField(max_length=20, unique=True, blank=True)
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES, default='online')
    booking_date = models.DateTimeField(auto_now_add=True)
    
    # Stay Details
    start_date = models.DateField()
    end_date = models.DateField()
    total_months = models.PositiveIntegerField(default=1)
    total_days = models.PositiveIntegerField(default=30)
    
    # Occupancy Details
    number_of_occupants = models.PositiveIntegerField(default=1)
    occupants_details = models.JSONField(default=list)  # Store details of all occupants
    
    # Pricing
    base_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maintenance_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Additional Information
    special_requests = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancellation_date = models.DateTimeField(blank=True, null=True)
    
    # Documents
    id_proofs_submitted = models.BooleanField(default=False)
    agreement_signed = models.BooleanField(default=False)
    agreement_document = models.FileField(upload_to='agreements/', blank=True, null=True)
    
    # Check-in/Check-out
    check_in_date = models.DateTimeField(blank=True, null=True)
    check_out_date = models.DateTimeField(blank=True, null=True)
    actual_check_out_date = models.DateTimeField(blank=True, null=True)
    
    # Agent Information (if booked through agent)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='agent_bookings'
    )
    agent_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.booking_reference} - {self.user.username} ({self.rental_property.name})"
    
    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.start_date <= today <= self.end_date and 
            self.status == 'confirmed' and
            self.check_in_date and
            not self.actual_check_out_date
        )
    
    @property
    def is_upcoming(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date > today and self.status == 'confirmed'
    
    @property
    def is_completed(self):
        return self.status == 'completed' or (self.actual_check_out_date is not None)
    
    @property
    def total_paid_amount(self):
        """Calculate total paid amount from related payments"""
        return sum(payment.amount for payment in self.payments.filter(payment_status='completed'))
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.final_amount - self.total_paid_amount
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate unique booking reference with retry mechanism
            max_attempts = 5
            for attempt in range(max_attempts):
                self.booking_reference = self.generate_booking_reference()
                # Check if reference already exists
                if not Booking.objects.filter(booking_reference=self.booking_reference).exists():
                    break
                # If we reach the last attempt, add random suffix
                if attempt == max_attempts - 1:
                    import uuid
                    self.booking_reference = f"{self.booking_reference}{uuid.uuid4().hex[:4]}"
        
        if self.start_date and self.end_date:
            from datetime import date
            delta = self.end_date - self.start_date
            if delta.days > 0:
                self.total_days = delta.days
                self.total_months = max(1, (delta.days // 30) + (1 if delta.days % 30 > 0 else 0))
            else:
                self.total_days = 1
                self.total_months = 1
            
            # Calculate final amount
            self.final_amount = (
                self.monthly_rent * self.total_months +
                self.security_deposit +
                self.maintenance_charge +
                self.other_charges -
                self.discount_amount
            )
        
        super().save(*args, **kwargs)
    
    def generate_booking_reference(self):
        import uuid
        from datetime import datetime
        # Include time with seconds for more uniqueness
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        # Use full UUID for maximum uniqueness
        unique_id = str(uuid.uuid4()).upper()[:8]
        return f"BK{timestamp}{unique_id}"

class BookingPayment(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_reference = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    cheque_number = models.CharField(max_length=50, blank=True)
    upi_transaction_id = models.CharField(max_length=100, blank=True)
    card_last_4_digits = models.CharField(max_length=4, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    receipt_uploaded = models.BooleanField(default=False)
    receipt_document = models.FileField(upload_to='payment_receipts/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.payment_reference} - {self.booking.booking_reference}"

class BookingHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Booking Created'),
        ('confirmed', 'Booking Confirmed'),
        ('cancelled', 'Booking Cancelled'),
        ('modified', 'Booking Modified'),
        ('payment_received', 'Payment Received'),
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('document_uploaded', 'Document Uploaded'),
        ('agreement_signed', 'Agreement Signed'),
        ('note_added', 'Note Added'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.action} by {self.changed_by.username}"

class BookingDocument(models.Model):
    DOCUMENT_TYPES = [
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
        ('income_proof', 'Income Proof'),
        ('student_id', 'Student ID'),
        ('company_id', 'Company ID'),
        ('police_verification', 'Police Verification'),
        ('medical_certificate', 'Medical Certificate'),
        ('agreement', 'Rental Agreement'),
        ('noc', 'NOC Certificate'),
        ('other', 'Other'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_name = models.CharField(max_length=200)
    document = models.FileField(upload_to='booking_documents/')
    document_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='verified_documents'
    )
    verification_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.document_type}"

class BookingReview(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rental_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='booking_reviews')
    
    # Ratings
    cleanliness_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    amenities_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    safety_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    location_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    value_for_money_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    overall_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    
    # Review Details
    title = models.CharField(max_length=200)
    review = models.TextField()
    pros = models.TextField(blank=True)
    cons = models.TextField(blank=True)
    
    # Status
    is_public = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.overall_rating}★"
    
    def save(self, *args, **kwargs):
        # Calculate overall rating as average of all ratings
        total_rating = (
            self.cleanliness_rating +
            self.amenities_rating +
            self.safety_rating +
            self.location_rating +
            self.value_for_money_rating
        )
        self.overall_rating = round(total_rating / 5)
        super().save(*args, **kwargs)
