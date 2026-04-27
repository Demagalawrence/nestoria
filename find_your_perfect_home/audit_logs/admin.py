from django.contrib import admin
from .models import AuditLog, SystemLog, DataChangeLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'object_repr', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp', 'content_type')
    search_fields = ('user__username', 'object_repr', 'changes')
    readonly_fields = ('timestamp', 'user', 'action', 'content_type', 'object_id', 
                      'content_object', 'object_repr', 'changes', 'ip_address', 
                      'user_agent', 'session_key')
    
    fieldsets = (
        ('User & Action', {'fields': ('user', 'action', 'timestamp')}),
        ('Object', {'fields': ('content_type', 'object_id', 'content_object', 'object_repr')}),
        ('Changes', {'fields': ('changes', 'reason')}),
        ('Request Info', {'fields': ('ip_address', 'user_agent', 'session_key')}),
    )
    
    def has_add_permission(self, request):
        return False  # Audit logs should not be manually created

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'module', 'message_short', 'user', 'created_at')
    list_filter = ('level', 'module', 'created_at')
    search_fields = ('message', 'module', 'function')
    readonly_fields = ('created_at', 'level', 'message', 'module', 'function', 
                      'line_number', 'user', 'ip_address', 'user_agent', 'request_id', 'extra_data')
    
    def message_short(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = 'Message'
    
    fieldsets = (
        ('Log Info', {'fields': ('level', 'message', 'module', 'function', 'line_number')}),
        ('Context', {'fields': ('user', 'ip_address', 'user_agent', 'request_id')}),
        ('Extra Data', {'fields': ('extra_data',)}),
        ('Timestamp', {'fields': ('created_at',)}),
    )
    
    def has_add_permission(self, request):
        return False

@admin.register(DataChangeLog)
class DataChangeLogAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'record_id', 'field_name', 'changed_by', 'changed_at')
    list_filter = ('table_name', 'changed_at')
    search_fields = ('table_name', 'field_name', 'changed_by__username')
    readonly_fields = ('changed_at', 'table_name', 'record_id', 'field_name', 
                      'old_value', 'new_value', 'changed_by', 'change_reason', 
                      'ip_address', 'user_agent')
    
    fieldsets = (
        ('Data Info', {'fields': ('table_name', 'record_id', 'field_name')}),
        ('Values', {'fields': ('old_value', 'new_value')}),
        ('Change Info', {'fields': ('changed_by', 'changed_at', 'change_reason')}),
        ('Request Info', {'fields': ('ip_address', 'user_agent')}),
    )
    
    def has_add_permission(self, request):
        return False
