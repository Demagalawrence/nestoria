from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('payment_completed', 'Payment Completed'),
        ('payment_failed', 'Payment Failed'),
        ('check_in_reminder', 'Check-in Reminder'),
        ('check_out_reminder', 'Check-out Reminder'),
        ('property_approved', 'Property Approved'),
        ('property_rejected', 'Property Rejected'),
        ('review_received', 'Review Received'),
        ('commission_paid', 'Commission Paid'),
        # Maintenance notification types
        ('maintenance_request_created', 'Maintenance Request Created'),
        ('maintenance_status_update', 'Maintenance Status Updated'),
        ('maintenance_assigned', 'Maintenance Assigned'),
        ('maintenance_comment', 'New Maintenance Comment'),
        ('maintenance_property_update', 'Property Maintenance Update'),
        ('maintenance_completed', 'Maintenance Completed'),
        ('maintenance_urgent', 'Urgent Maintenance Request'),
        # Agent notification types
        ('agent_request_assigned', 'Agent Request Assigned'),
        ('agent_request_completed', 'Agent Request Completed'),
        ('agent_new_review', 'New Agent Review'),
        ('agent_commission_earned', 'Commission Earned'),
        ('agent_profile_verified', 'Agent Profile Verified'),
    ]
    
    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=20, choices=CHANNELS, default='in_app')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    
    # Related objects (optional)
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey('payments.Payment', on_delete=models.CASCADE, null=True, blank=True)
    maintenance_request = models.ForeignKey('maintenance.MaintenanceRequest', on_delete=models.CASCADE, null=True, blank=True)
    agent_request = models.ForeignKey('agents.AgentRequest', on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class NotificationTemplate(models.Model):
    notification_type = models.CharField(max_length=30, choices=Notification.NOTIFICATION_TYPES, unique=True)
    channel = models.CharField(max_length=20, choices=Notification.CHANNELS)
    subject_template = models.CharField(max_length=200, blank=True)
    message_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.notification_type} - {self.channel}"

class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    booking_updates = models.BooleanField(default=True)
    payment_updates = models.BooleanField(default=True)
    property_updates = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Preferences"
