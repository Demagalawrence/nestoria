"""
AI Assistant Tools URLs
URL patterns for AI assistant hostel booking tools
"""

from django.urls import path
from . import ai_tools_views

app_name = 'ai_tools'

urlpatterns = [
    # AI-powered hostel search
    path('search-hostels/', ai_tools_views.ai_search_hostels, name='ai_search_hostels'),
    
    # Hostel details
    path('hostel-details/<str:hostel_id>/', ai_tools_views.ai_get_hostel_details, name='ai_get_hostel_details'),
    
    # Availability checking
    path('check-availability/<str:hostel_id>/', ai_tools_views.ai_check_availability, name='ai_check_availability'),
    
    # Cost calculation
    path('calculate-cost/', ai_tools_views.ai_calculate_booking_cost, name='ai_calculate_booking_cost'),
    
    # Hostel comparison
    path('compare-hostels/', ai_tools_views.ai_compare_hostels, name='ai_compare_hostels'),
    
    # Booking status
    path('booking-status/<str:booking_id>/', ai_tools_views.ai_get_booking_status, name='ai_get_booking_status'),
    
    # University information
    path('universities/', ai_tools_views.ai_get_universities_info, name='ai_get_universities_info'),
    
    # Area information
    path('areas/', ai_tools_views.ai_get_areas_info, name='ai_get_areas_info'),
    
    # Booking tips
    path('booking-tips/', ai_tools_views.ai_get_booking_tips, name='ai_get_booking_tips'),
]
