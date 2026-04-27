from django.db import models
from django.conf import settings
from django.utils import timezone
from properties.models import Property

class AgentProfile(models.Model):
    """Extended profile for real estate agents"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='agent_profile'
    )
    
    # Professional Information
    license_number = models.CharField(max_length=50, unique=True)
    agency_name = models.CharField(max_length=200, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    specialization = models.CharField(
        max_length=100,
        choices=[
            ('residential', 'Residential Properties'),
            ('commercial', 'Commercial Properties'),
            ('student_housing', 'Student Housing'),
            ('luxury', 'Luxury Properties'),
            ('budget', 'Budget Properties'),
            ('all_types', 'All Property Types'),
        ],
        default='all_types'
    )
    
    # Service Areas
    service_areas = models.JSONField(default=list)  # List of districts/areas
    preferred_property_types = models.JSONField(default=list)  # List of property types
    
    # Availability
    is_available = models.BooleanField(default=True)
    working_hours = models.JSONField(default=dict)  # {"monday": "9:00-17:00", ...}
    response_time = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('within_30min', 'Within 30 minutes'),
            ('within_1hour', 'Within 1 hour'),
            ('within_2hours', 'Within 2 hours'),
            ('within_24hours', 'Within 24 hours'),
        ],
        default='within_1hour'
    )
    
    # Languages
    languages = models.JSONField(default=list)  # ["english", "luganda", "swahili"]
    
    # Commission and Pricing
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_consultation = models.BooleanField(default=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='agent_verifications/', blank=True, null=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Ratings and Performance
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_clients = models.PositiveIntegerField(default=0)
    successful_deals = models.PositiveIntegerField(default=0)
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Bio and Description
    bio = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    education = models.TextField(blank=True)
    
    # Social Media
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Agent Profile"
        verbose_name_plural = "Agent Profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Agent"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def is_online(self):
        """Check if agent is currently online based on working hours"""
        now = timezone.now()
        current_day = now.strftime('%A').lower()
        current_time = now.strftime('%H:%M')
        
        if current_day in self.working_hours:
            start_time, end_time = self.working_hours[current_day].split('-')
            return start_time <= current_time <= end_time
        return False

class AgentRequest(models.Model):
    """Customer requests for agent assistance"""
    REQUEST_TYPES = [
        ('property_viewing', 'Property Viewing'),
        ('property_consultation', 'Property Consultation'),
        ('booking_assistance', 'Booking Assistance'),
        ('negotiation', 'Price Negotiation'),
        ('document_help', 'Document Assistance'),
        ('general_inquiry', 'General Inquiry'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned to Agent'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_response', 'No Response from Agent'),
    ]
    
    # Customer Information
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='agent_requests'
    )
    
    # Request Details
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    property = models.ForeignKey(
        Property, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='agent_requests'
    )
    
    # Assignment
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )
    
    # Scheduling
    preferred_date = models.DateTimeField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    
    # Communication
    contact_method = models.CharField(
        max_length=20,
        choices=[
            ('phone', 'Phone Call'),
            ('whatsapp', 'WhatsApp'),
            ('email', 'Email'),
            ('video_call', 'Video Call'),
            ('in_person', 'In Person'),
        ],
        default='phone'
    )
    contact_details = models.TextField(blank=True)  # Additional contact info
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium'
    )
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    customer_rating = models.PositiveIntegerField(null=True, blank=True)  # 1-5 stars
    customer_feedback = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['assigned_agent', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        # Create notification when request is assigned
        if self.pk:
            old_instance = AgentRequest.objects.get(pk=self.pk)
            if old_instance.assigned_agent != self.assigned_agent and self.assigned_agent:
                self.create_assignment_notification()
        
        super().save(*args, **kwargs)
    
    def create_assignment_notification(self):
        """Create notification for assigned agent"""
        from notifications.models import Notification
        
        Notification.objects.create(
            user=self.assigned_agent,
            notification_type='agent_request_assigned',
            title=f'New Agent Request - {self.title}',
            message=f'You have been assigned to assist with: {self.description[:100]}...',
            agent_request=self,
            property=self.property
        )

class AgentAvailability(models.Model):
    """Agent availability schedule"""
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ]
    )
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    # Special notes for the day
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['agent', 'day_of_week']
        ordering = ['day_of_week']
    
    def __str__(self):
        return f"{self.agent.get_full_name()} - {self.day_of_week.title()}"

class AgentReview(models.Model):
    """Customer reviews for agents"""
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_reviews'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_agent_reviews'
    )
    agent_request = models.OneToOneField(
        AgentRequest,
        on_delete=models.CASCADE,
        related_name='review'
    )
    
    # Ratings
    communication_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    professionalism_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    knowledge_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    helpfulness_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    overall_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    
    # Review Details
    title = models.CharField(max_length=200)
    review = models.TextField()
    would_recommend = models.BooleanField(default=True)
    
    # Status
    is_public = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['agent', 'customer', 'agent_request']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.customer.username} for {self.agent.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Update agent's average rating
        super().save(*args, **kwargs)
        self.update_agent_rating()
    
    def update_agent_rating(self):
        """Update agent's average rating"""
        agent_profile = self.agent.agent_profile
        reviews = AgentReview.objects.filter(agent=self.agent)
        
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('overall_rating'))['overall_rating__avg']
            agent_profile.average_rating = round(avg_rating, 2)
            agent_profile.save()

class AgentCommission(models.Model):
    """Track agent commissions and payments"""
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_commissions'
    )
    
    # Deal Information
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='commission_payment'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='agent_commissions'
    )
    
    # Commission Details
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_deal_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment Status
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_reference = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commission for {self.agent.get_full_name()} - {self.commission_amount}"
