from django.urls import path
from . import views

app_name = 'credit_cards'

urlpatterns = [
    path('providers/', views.CreditCardProviderListView.as_view(), name='provider_list'),
    path('initiate/', views.initiate_credit_card_payment, name='initiate_payment'),
    path('save-card/', views.save_credit_card, name='save_card'),
    path('pay-with-saved/', views.initiate_payment_with_saved_card, name='pay_with_saved'),
    path('status/<str:transaction_id>/', views.check_payment_status, name='check_payment_status'),
    path('saved-cards/', views.user_saved_cards, name='saved_cards'),
    path('saved-cards/<int:card_id>/', views.delete_saved_card, name='delete_saved_card'),
    path('saved-cards/<int:card_id>/set-default/', views.set_default_card, name='set_default_card'),
    path('history/', views.user_credit_card_payments, name='payment_history'),
    path('statistics/', views.credit_card_statistics, name='payment_statistics'),
]
