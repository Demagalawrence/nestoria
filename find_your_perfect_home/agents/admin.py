from django.contrib import admin
from .models import (
    AgentProfile, AgentRequest, AgentAvailability, 
    AgentReview, AgentCommission
)

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'agency_name', 'license_number', 'is_verified', 'average_rating', 'is_available']
    list_filter = ['is_verified', 'is_available', 'specialization', 'response_time']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'agency_name', 'license_number']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']

@admin.register(AgentRequest)
class AgentRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'assigned_agent', 'request_type', 'status', 'created_at']
    list_filter = ['status', 'request_type', 'priority', 'created_at']
    search_fields = ['title', 'customer__username', 'assigned_agent__username']
    readonly_fields = ['created_at', 'updated_at', 'assigned_at', 'completed_at']

@admin.register(AgentAvailability)
class AgentAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['agent', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['agent__username']

@admin.register(AgentReview)
class AgentReviewAdmin(admin.ModelAdmin):
    list_display = ['agent', 'customer', 'overall_rating', 'would_recommend', 'created_at']
    list_filter = ['overall_rating', 'would_recommend', 'is_public', 'created_at']
    search_fields = ['agent__username', 'customer__username', 'title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AgentCommission)
class AgentCommissionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'property', 'commission_amount', 'is_paid', 'created_at']
    list_filter = ['is_paid', 'created_at']
    search_fields = ['agent__username', 'property__name']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']
