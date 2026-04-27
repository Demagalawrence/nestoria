from django.db import models
from django.conf import settings
from django.utils import timezone
from properties.models import Property, Room

class MaintenanceCategory(models.Model):
    """Categories for maintenance requests"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For UI display
    color = models.CharField(max_length=7, default='#6b7280')  # Hex color
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Maintenance Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class MaintenanceRequest(models.Model):
    """Main maintenance request model"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(MaintenanceCategory, on_delete=models.SET_NULL, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Relationships
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='maintenance_requests')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_requests')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='maintenance_requests')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_maintenance'
    )
    
    # Request Details
    requested_date = models.DateTimeField(auto_now_add=True)
    preferred_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Access Information
    access_instructions = models.TextField(blank=True)
    permission_to_enter = models.BooleanField(default=False)
    tenant_present = models.BooleanField(default=False)
    
    # Tracking
    reference_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['property', 'status']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)
        
        # Trigger notifications on status change
        if self.pk:
            old_instance = MaintenanceRequest.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                self.create_status_notification(old_instance.status, self.status)
    
    def generate_reference_number(self):
        """Generate unique reference number"""
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"MR{timestamp}{unique_id}"
    
    def create_status_notification(self, old_status, new_status):
        """Create notifications when status changes"""
        from notifications.models import Notification
        
        # Notify tenant
        Notification.objects.create(
            user=self.tenant,
            notification_type='maintenance_status_update',
            title=f'Maintenance Request {self.reference_number} Updated',
            message=f'Your maintenance request "{self.title}" status changed from {old_status.replace("_", " ").title()} to {new_status.replace("_", " ").title()}.',
            maintenance_request=self,
            property=self.property
        )
        
        # Notify assigned person if different from tenant
        if self.assigned_to and self.assigned_to != self.tenant:
            Notification.objects.create(
                user=self.assigned_to,
                notification_type='maintenance_assigned',
                title=f'Maintenance Request {self.reference_number} Status Update',
                message=f'Maintenance request "{self.title}" status changed to {new_status.replace("_", " ").title()}.',
                maintenance_request=self,
                property=self.property
            )
        
        # Notify property owner
        if hasattr(self.property, 'owner') and self.property.owner != self.tenant and self.property.owner != self.assigned_to:
            Notification.objects.create(
                user=self.property.owner,
                notification_type='maintenance_property_update',
                title=f'Property Maintenance Update - {self.property.name}',
                message=f'Maintenance request "{self.title}" status changed to {new_status.replace("_", " ").title()}.',
                maintenance_request=self,
                property=self.property
            )

class MaintenanceImage(models.Model):
    """Images for maintenance requests"""
    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='maintenance_images/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.maintenance_request.reference_number} - Image"

class MaintenanceComment(models.Model):
    """Comments and communication for maintenance requests"""
    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal notes vs tenant-visible
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['maintenance_request', 'is_internal']),
        ]
    
    def __str__(self):
        return f"{self.maintenance_request.reference_number} - Comment by {self.author.username}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Create notification for new comments
        if is_new and not self.is_internal:
            self.create_comment_notification()
    
    def create_comment_notification(self):
        """Create notifications for new comments"""
        from notifications.models import Notification
        
        # Notify other participants
        participants = set()
        participants.add(self.maintenance_request.tenant)
        
        if self.maintenance_request.assigned_to:
            participants.add(self.maintenance_request.assigned_to)
        
        if hasattr(self.maintenance_request.property, 'owner'):
            participants.add(self.maintenance_request.property.owner)
        
        # Remove the comment author from notifications
        participants.discard(self.author)
        
        for user in participants:
            Notification.objects.create(
                user=user,
                notification_type='maintenance_comment',
                title=f'New Comment on {self.maintenance_request.reference_number}',
                message=f'{self.author.get_full_name() or self.author.username} commented: "{self.comment[:100]}..."',
                maintenance_request=self.maintenance_request,
                property=self.maintenance_request.property
            )

class MaintenanceHistory(models.Model):
    """Track all changes to maintenance requests"""
    ACTION_CHOICES = [
        ('created', 'Request Created'),
        ('status_changed', 'Status Changed'),
        ('assigned', 'Assigned to Staff'),
        ('unassigned', 'Unassigned'),
        ('priority_changed', 'Priority Changed'),
        ('cost_updated', 'Cost Updated'),
        ('comment_added', 'Comment Added'),
        ('image_added', 'Image Added'),
        ('completed', 'Request Completed'),
        ('cancelled', 'Request Cancelled'),
    ]
    
    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['maintenance_request', 'action']),
            models.Index(fields=['changed_by', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.maintenance_request.reference_number} - {self.action}"
