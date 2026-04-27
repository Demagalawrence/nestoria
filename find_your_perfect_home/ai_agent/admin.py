from django.contrib import admin
from .models import AIConversation, AIMessage

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'message_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'title')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'admin':
            return qs
        return qs.filter(user=request.user)

@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'message_preview', 'intent', 'created_at')
    list_filter = ('role', 'intent', 'created_at')
    search_fields = ('conversation__user__username', 'message', 'intent')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Message Info', {'fields': ('conversation', 'role', 'message')}),
        ('AI Metadata', {'fields': ('intent', 'properties_shown', 'confidence_score')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'admin':
            return qs
        return qs.filter(conversation__user=request.user)
