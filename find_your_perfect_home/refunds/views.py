from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import RefundPolicy, Refund, RefundRequest
from .serializers import RefundPolicySerializer, RefundSerializer, RefundRequestSerializer
from django.utils import timezone

class RefundPolicyListView(generics.ListAPIView):
    queryset = RefundPolicy.objects.filter(is_active=True)
    serializer_class = RefundPolicySerializer
    permission_classes = [IsAuthenticated]

class RefundRequestCreateView(generics.CreateAPIView):
    queryset = RefundRequest.objects.all()
    serializer_class = RefundRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RefundRequestDetailView(generics.RetrieveAPIView):
    serializer_class = RefundRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return RefundRequest.objects.all()
        return RefundRequest.objects.filter(user=user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_refund(request, booking_id):
    """Calculate refund amount for a booking"""
    try:
        from bookings.models import Booking
        booking = Booking.objects.get(id=booking_id)
        
        # Check permissions
        user = request.user
        if user.role not in ['admin'] and booking.user != user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get refund policy (default or property-specific)
        policy = RefundPolicy.objects.filter(is_default=True).first()
        if not policy:
            return Response({'error': 'No refund policy found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate refund
        calculation = policy.calculate_refund(booking)
        
        return Response({
            'booking_reference': booking.booking_reference,
            'original_amount': float(booking.final_amount),
            'refund_amount': float(calculation['refund_amount']),
            'refund_type': calculation['refund_type'],
            'cancellation_fee': float(calculation['cancellation_fee']),
            'processing_fee': float(calculation['processing_fee']),
            'days_until_checkin': calculation['days_until_checkin'],
            'policy_name': policy.name,
        })
        
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_refund_request(request, pk):
    """Process a refund request (approve/reject)"""
    try:
        refund_request = RefundRequest.objects.get(pk=pk)
        
        # Check permissions (only admin can process)
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get('action')  # 'approve' or 'reject'
        notes = request.data.get('notes', '')
        
        if action == 'approve':
            success, message = refund_request.approve(request.user, notes)
            if success:
                return Response({'message': message, 'refund_id': refund_request.refund.id})
            else:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
        elif action == 'reject':
            success, message = refund_request.reject(request.user, notes)
            if success:
                return Response({'message': message})
            else:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            
    except RefundRequest.DoesNotExist:
        return Response({'error': 'Refund request not found'}, status=status.HTTP_404_NOT_FOUND)

class RefundListView(generics.ListAPIView):
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'refund_type']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Refund.objects.all()
        elif user.role == 'owner':
            # Owners can see refunds for their properties
            from bookings.models import Booking
            from properties.models import Property
            user_properties = Property.objects.filter(owner=user)
            property_ids = user_properties.values_list('id', flat=True)
            booking_ids = Booking.objects.filter(rental_property__in=property_ids).values_list('id', flat=True)
            return Refund.objects.filter(booking_id__in=booking_ids)
        else:
            # Users can see their own refunds
            return Refund.objects.filter(booking__user=user)

class RefundDetailView(generics.RetrieveAPIView):
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Refund.objects.all()
        elif user.role == 'owner':
            from bookings.models import Booking
            from properties.models import Property
            user_properties = Property.objects.filter(owner=user)
            property_ids = user_properties.values_list('id', flat=True)
            booking_ids = Booking.objects.filter(rental_property__in=property_ids).values_list('id', flat=True)
            return Refund.objects.filter(booking_id__in=booking_ids)
        else:
            return Refund.objects.filter(booking__user=user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_refund(request, pk):
    """Execute refund processing (integrate with payment gateway)"""
    try:
        refund = Refund.objects.get(pk=pk)
        
        # Check permissions
        user = request.user
        if user.role not in ['admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if refund.status != 'pending':
            return Response({'error': 'Refund is not in pending status'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process refund
        success, message = refund.process_refund(processed_by=user)
        
        if success:
            return Response({
                'message': message,
                'transaction_id': refund.transaction_id,
                'refund_amount': float(refund.refund_amount)
            })
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            
    except Refund.DoesNotExist:
        return Response({'error': 'Refund not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def refund_statistics(request):
    """Get refund statistics"""
    user = request.user
    
    if user.role == 'admin':
        refunds = Refund.objects.all()
        refund_requests = RefundRequest.objects.all()
    elif user.role == 'owner':
        from bookings.models import Booking
        from properties.models import Property
        user_properties = Property.objects.filter(owner=user)
        property_ids = user_properties.values_list('id', flat=True)
        booking_ids = Booking.objects.filter(rental_property__in=property_ids).values_list('id', flat=True)
        refunds = Refund.objects.filter(booking_id__in=booking_ids)
        refund_requests = RefundRequest.objects.filter(booking__rental_property__in=property_ids)
    else:
        refunds = Refund.objects.filter(booking__user=user)
        refund_requests = RefundRequest.objects.filter(user=user)
    
    stats = {
        'total_refunds': refunds.count(),
        'pending_refunds': refunds.filter(status='pending').count(),
        'completed_refunds': refunds.filter(status='completed').count(),
        'failed_refunds': refunds.filter(status='failed').count(),
        'total_refund_amount': float(sum(r.refund_amount for r in refunds.filter(status='completed'))),
        'pending_requests': refund_requests.filter(status='pending').count(),
        'approved_requests': refund_requests.filter(status='approved').count(),
        'rejected_requests': refund_requests.filter(status='rejected').count(),
    }
    
    return Response(stats)
