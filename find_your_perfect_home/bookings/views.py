from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from .models import Booking, BookingPayment, BookingHistory, BookingDocument, BookingReview
from properties.models import Room, Property
from .serializers import (BookingSerializer, BookingCreateSerializer, BookingDetailSerializer,
                         BookingPaymentSerializer, BookingDocumentSerializer, BookingReviewSerializer)

class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status', 'booking_type']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'agent']:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

class BookingDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'agent']:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        # Create booking history
        booking = serializer.instance
        BookingHistory.objects.create(
            booking=booking,
            changed_by=self.request.user,
            action='created',
            description=f'Booking {booking.booking_reference} created'
        )

class BookingUpdateView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

class BookingCancelView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
            
            # Check permissions
            if request.user.role != 'admin' and booking.user != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            # Check if booking can be cancelled
            if booking.status in ['completed', 'cancelled']:
                return Response({'error': 'Booking cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
            
            cancellation_reason = request.data.get('cancellation_reason', '')
            booking.status = 'cancelled'
            booking.cancellation_reason = cancellation_reason
            booking.cancellation_date = timezone.now()
            booking.save()
            
            # Create booking history
            BookingHistory.objects.create(
                booking=booking,
                changed_by=request.user,
                action='cancelled',
                old_status='confirmed',
                new_status='cancelled',
                description=f'Booking cancelled: {cancellation_reason}'
            )
            
            return Response({'message': 'Booking cancelled successfully'}, status=status.HTTP_200_OK)
            
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

class BookingConfirmView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
            
            # Check permissions (admin, property owner, or booking user can confirm)
            if request.user.role not in ['admin'] and booking.rental_property.owner != request.user and booking.user != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            if booking.status != 'pending':
                return Response({'error': 'Only pending bookings can be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
            
            booking.status = 'confirmed'
            booking.confirmed_at = timezone.now()
            booking.save()
            
            # Update room availability
            room = booking.room
            room.current_occupancy += booking.number_of_occupants
            if room.current_occupancy >= room.capacity:
                room.status = 'occupied'
            room.save()
            
            # Update property availability
            property_obj = booking.rental_property
            property_obj.available_rooms -= 1
            property_obj.save()
            
            # Create booking history
            BookingHistory.objects.create(
                booking=booking,
                changed_by=request.user,
                action='confirmed',
                old_status='pending',
                new_status='confirmed',
                description='Booking confirmed by property owner'
            )
            
            return Response({'message': 'Booking confirmed successfully'}, status=status.HTTP_200_OK)
            
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

class CheckInView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
            
            # Check permissions
            if request.user.role not in ['admin'] and booking.rental_property.owner != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            if booking.status != 'confirmed':
                return Response({'error': 'Only confirmed bookings can be checked in'}, status=status.HTTP_400_BAD_REQUEST)
            
            booking.check_in_date = timezone.now()
            booking.save()
            
            # Create booking history
            BookingHistory.objects.create(
                booking=booking,
                changed_by=request.user,
                action='check_in',
                description='Guest checked in'
            )
            
            return Response({'message': 'Check-in successful'}, status=status.HTTP_200_OK)
            
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

class CheckOutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
            
            # Check permissions
            if request.user.role not in ['admin'] and booking.rental_property.owner != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            if booking.status != 'confirmed':
                return Response({'error': 'Only confirmed bookings can be checked out'}, status=status.HTTP_400_BAD_REQUEST)
            
            booking.actual_check_out_date = timezone.now()
            booking.status = 'completed'
            booking.save()
            
            # Update room availability
            room = booking.room
            room.current_occupancy -= booking.number_of_occupants
            if room.current_occupancy == 0:
                room.status = 'vacant'
            else:
                room.status = 'occupied'
            room.save()
            
            # Update property availability
            property_obj = booking.rental_property
            property_obj.available_rooms += 1
            property_obj.save()
            
            # Create booking history
            BookingHistory.objects.create(
                booking=booking,
                changed_by=request.user,
                action='check_out',
                description='Guest checked out'
            )
            
            return Response({'message': 'Check-out successful'}, status=status.HTTP_200_OK)
            
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

class UploadBookingDocumentView(generics.CreateAPIView):
    queryset = BookingDocument.objects.all()
    serializer_class = BookingDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        booking_id = self.kwargs['pk']
        booking = Booking.objects.get(pk=booking_id)
        
        # Check permissions
        if self.request.user != booking.user and self.request.user.role != 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to upload documents for this booking")
        
        serializer.save(booking=booking)

class BookingPaymentView(generics.ListCreateAPIView):
    serializer_class = BookingPaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        booking_id = self.kwargs['pk']
        booking = Booking.objects.get(pk=booking_id)
        
        # Check permissions
        if self.request.user != booking.user and self.request.user.role != 'admin':
            return BookingPayment.objects.none()
        
        return booking.payments.all()
    
    def perform_create(self, serializer):
        booking_id = self.kwargs['pk']
        booking = Booking.objects.get(pk=booking_id)
        serializer.save(booking=booking)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_statistics(request):
    user = request.user
    
    if user.role == 'admin':
        bookings = Booking.objects.all()
    elif user.role == 'owner':
        bookings = Booking.objects.filter(rental_property__owner=user)
    else:
        bookings = Booking.objects.filter(user=user)
    
    stats = {
        'total_bookings': bookings.count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'completed_bookings': bookings.filter(status='completed').count(),
        'cancelled_bookings': bookings.filter(status='cancelled').count(),
        'total_revenue': sum(b.final_amount for b in bookings.filter(status='completed')),
    }
    
    return Response(stats)
