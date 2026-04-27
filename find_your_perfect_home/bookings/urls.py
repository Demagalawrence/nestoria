from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking_update'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('<int:pk>/confirm/', views.BookingConfirmView.as_view(), name='booking_confirm'),
    path('<int:pk>/check-in/', views.CheckInView.as_view(), name='check_in'),
    path('<int:pk>/check-out/', views.CheckOutView.as_view(), name='check_out'),
    path('<int:pk>/upload-document/', views.UploadBookingDocumentView.as_view(), name='upload_document'),
    path('<int:pk>/payment/', views.BookingPaymentView.as_view(), name='booking_payment'),
]
