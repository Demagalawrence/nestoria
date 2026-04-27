from django.urls import path
from . import views
from . import verification_views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('process/', views.ProcessPaymentView.as_view(), name='process_payment'),
    path('success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('failed/', views.PaymentFailedView.as_view(), name='payment_failed'),
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    path('receipt/<int:pk>/', views.ReceiptView.as_view(), name='receipt'),
    
    # Verification endpoints
    path('verify/<str:receipt_number>/', verification_views.verify_receipt, name='verify_receipt'),
    path('verify-signature/', verification_views.verify_receipt_with_signature, name='verify_receipt_signature'),
    path('download/<str:receipt_number>/', verification_views.ReceiptDownloadView.as_view(), name='download_receipt'),
]
