from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('property/<int:pk>/', views.PropertyAnalyticsView.as_view(), name='property_analytics'),
    path('platform/', views.platform_analytics, name='platform_analytics'),
    path('property-performance/', views.property_performance_report, name='property_performance'),
    path('user-activity/', views.UserActivityListView.as_view(), name='user_activity'),
    path('track-activity/', views.track_user_activity, name='track_activity'),
    path('dashboard/', views.dashboard_stats, name='dashboard_stats'),
]
