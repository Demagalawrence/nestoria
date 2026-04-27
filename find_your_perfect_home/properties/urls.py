from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property_list'),
    path('create/', views.PropertyCreateView.as_view(), name='property_create'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('<int:pk>/update/', views.PropertyUpdateView.as_view(), name='property_update'),
    path('<int:pk>/delete/', views.PropertyDeleteView.as_view(), name='property_delete'),
    path('<int:pk>/rooms/', views.RoomListView.as_view(), name='room_list'),
    path('<int:pk>/rooms/create/', views.RoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:room_pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('rooms/<int:room_pk>/update/', views.RoomUpdateView.as_view(), name='room_update'),
    path('rooms/<int:room_pk>/delete/', views.RoomDeleteView.as_view(), name='room_delete'),
    path('search/', views.PropertySearchView.as_view(), name='property_search'),
    path('<int:pk>/upload-image/', views.upload_property_image, name='upload_image'),
    path('<int:pk>/upload-video/', views.upload_property_video, name='upload_video'),
    path('<int:pk>/add-review/', views.add_property_review, name='add_review'),
]
