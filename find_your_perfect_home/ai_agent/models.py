from django.db import models
from django.conf import settings
from django.utils import timezone

class AIConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]
    
    def __str__(self):
        return f"Conversation with {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def last_message(self):
        return self.messages.last().message if self.messages.exists() else None
    
    @property
    def message_count(self):
        return self.messages.count()

class AIMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Assistant'),
    ]
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional metadata
    intent = models.CharField(max_length=50, blank=True)
    properties_shown = models.JSONField(default=list)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.role.title()}: {self.message[:50]}..."
