from django.urls import path
from . import views

app_name = 'mobile_money'

urlpatterns = [
    path('providers/', views.MobileMoneyProviderListView.as_view(), name='provider_list'),
    path('initiate/', views.initiate_mobile_payment, name='initiate_payment'),
    path('verify-phone/', views.verify_phone_number, name='verify_phone'),
    path('confirm-verification/', views.confirm_verification, name='confirm_verification'),
    path('status/<str:transaction_id>/', views.check_payment_status, name='check_payment_status'),
    path('retry/', views.retry_payment, name='retry_payment'),
    path('history/', views.user_mobile_payments, name='payment_history'),
    path('statistics/', views.mobile_payment_statistics, name='payment_statistics'),
]
