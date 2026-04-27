from django.urls import path
from . import views

app_name = 'refunds'

urlpatterns = [
    path('policies/', views.RefundPolicyListView.as_view(), name='policy_list'),
    path('requests/', views.RefundRequestCreateView.as_view(), name='request_create'),
    path('requests/<int:pk>/', views.RefundRequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:pk>/process/', views.process_refund_request, name='process_request'),
    path('calculate/<int:booking_id>/', views.calculate_refund, name='calculate_refund'),
    path('', views.RefundListView.as_view(), name='refund_list'),
    path('<int:pk>/', views.RefundDetailView.as_view(), name='refund_detail'),
    path('<int:pk>/execute/', views.execute_refund, name='execute_refund'),
    path('statistics/', views.refund_statistics, name='statistics'),
]
