from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class AuditLog(models.Model):
    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'Viewed'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('payment', 'Payment Processed'),
        ('refund', 'Refund Processed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Object being audited
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Details
    object_repr = models.CharField(max_length=200)
    changes = models.JSONField(default=dict)  # Store old and new values
    reason = models.TextField(blank=True)
    
    # Request information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
    
    def __str__(self):
        return f"{self.user} {self.action} {self.object_repr} at {self.timestamp}"

class SystemLog(models.Model):
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    module = models.CharField(max_length=100)
    function = models.CharField(max_length=100)
    line_number = models.PositiveIntegerField(null=True, blank=True)
    
    # Optional user context
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=50, blank=True)
    
    # Additional data
    extra_data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level', 'created_at']),
            models.Index(fields=['module']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.level} - {self.module} - {self.message[:50]}"

class DataChangeLog(models.Model):
    """Track specific data changes for compliance"""
    table_name = models.CharField(max_length=100)
    record_id = models.PositiveIntegerField()
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    change_reason = models.TextField(blank=True)
    
    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['table_name', 'record_id']),
            models.Index(fields=['changed_by', 'changed_at']),
            models.Index(fields=['changed_at']),
        ]
        unique_together = ['table_name', 'record_id', 'field_name', 'changed_at']
    
    def __str__(self):
        return f"{self.table_name}.{self.field_name} changed by {self.changed_by}"
