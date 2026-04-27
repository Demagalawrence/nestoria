from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('<int:pk>/mark-read/', views.mark_notification_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark_all_read'),
    path('preferences/', views.NotificationPreferenceView.as_view(), name='preferences'),
    path('statistics/', views.notification_statistics, name='statistics'),
    
    # Admin URLs
    path('templates/', views.NotificationTemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.NotificationTemplateDetailView.as_view(), name='template_detail'),
]
