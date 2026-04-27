from django.contrib import admin
from .models import (
    MaintenanceCategory, MaintenanceRequest, MaintenanceImage, 
    MaintenanceComment, MaintenanceHistory
)

@admin.register(MaintenanceCategory)
class MaintenanceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']

class MaintenanceImageInline(admin.TabularInline):
    model = MaintenanceImage
    extra = 1
    readonly_fields = ['uploaded_at']

class MaintenanceCommentInline(admin.TabularInline):
    model = MaintenanceComment
    extra = 1
    readonly_fields = ['created_at', 'updated_at']

class MaintenanceHistoryInline(admin.TabularInline):
    model = MaintenanceHistory
    extra = 0
    readonly_fields = ['timestamp', 'changed_by', 'action', 'old_value', 'new_value']
    can_delete = False

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'title', 'property', 'tenant', 'status', 
        'priority', 'assigned_to', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'category', 'created_at', 'requested_date'
    ]
    search_fields = [
        'reference_number', 'title', 'description', 'tenant__username',
        'property__name', 'assigned_to__username'
    ]
    readonly_fields = ['reference_number', 'created_at', 'updated_at']
    inlines = [MaintenanceImageInline, MaintenanceCommentInline, MaintenanceHistoryInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'reference_number', 'title', 'description', 'category', 
                'priority', 'status'
            )
        }),
        ('Relationships', {
            'fields': ('property', 'room', 'tenant', 'assigned_to')
        }),
        ('Request Details', {
            'fields': (
                'requested_date', 'preferred_date', 'completed_date',
                'estimated_cost', 'actual_cost'
            )
        }),
        ('Access Information', {
            'fields': (
                'access_instructions', 'permission_to_enter', 'tenant_present'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj and obj.status == 'completed':
            readonly.extend(['status', 'completed_date'])
        return readonly

@admin.register(MaintenanceImage)
class MaintenanceImageAdmin(admin.ModelAdmin):
    list_display = ['maintenance_request', 'caption', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = [
        'maintenance_request__reference_number', 'caption',
        'uploaded_by__username'
    ]
    readonly_fields = ['uploaded_at']

@admin.register(MaintenanceComment)
class MaintenanceCommentAdmin(admin.ModelAdmin):
    list_display = [
        'maintenance_request', 'author', 'is_internal', 
        'comment_preview', 'created_at'
    ]
    list_filter = ['is_internal', 'created_at']
    search_fields = [
        'maintenance_request__reference_number', 'comment',
        'author__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    def comment_preview(self, obj):
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    comment_preview.short_description = 'Comment'

@admin.register(MaintenanceHistory)
class MaintenanceHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'maintenance_request', 'action', 'changed_by', 'timestamp'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = [
        'maintenance_request__reference_number', 'changed_by__username',
        'notes'
    ]
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
