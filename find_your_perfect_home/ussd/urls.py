from django.urls import path
from . import views

app_name = 'ussd'

urlpatterns = [
    # Main USSD webhook
    path('webhook/', views.USSDWebhookView.as_view(), name='webhook'),
    
    # Gateway-specific endpoints
    path('gateway/mtn/', views.ussd_gateway_mtn, name='gateway_mtn'),
    path('gateway/airtel/', views.ussd_gateway_airtel, name='gateway_airtel'),
    path('gateway/generic/', views.ussd_gateway_generic, name='gateway_generic'),
    
    # Status and monitoring
    path('status/', views.ussd_status, name='status'),
    path('analytics/', views.ussd_analytics, name='analytics'),
    
    # Development and testing
    path('test/', views.ussd_test, name='test'),
    path('send-sms/', views.usd_send_sms, name='send_sms'),
    
    # Debug endpoints (only in DEBUG mode)
    path('debug/sessions/', views.usd_debug_sessions, name='debug_sessions'),
    path('debug/logs/', views.usd_debug_logs, name='debug_logs'),
    path('debug/clear-expired/', views.usd_clear_expired_sessions, name='clear_expired'),
]
