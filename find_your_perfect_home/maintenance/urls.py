from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Categories
    path('categories/', views.MaintenanceCategoryListView.as_view(), name='category-list'),
    
    # Maintenance Requests
    path('requests/', views.MaintenanceRequestListCreateView.as_view(), name='request-list-create'),
    path('requests/<int:pk>/', views.MaintenanceRequestDetailView.as_view(), name='request-detail'),
    path('requests/my/', views.my_maintenance_requests, name='my-requests'),
    
    # Statistics
    path('stats/', views.maintenance_stats, name='stats'),
]
