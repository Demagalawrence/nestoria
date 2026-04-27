"""
Mobile Money API Views
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from .models import MobileMoneyProvider, MobileMoneyPayment, MobileMoneyVerification
from .services import mobile_money_service
from payments.models import Payment
from bookings.models import Booking
from .serializers import (
    MobileMoneyProviderSerializer, MobileMoneyPaymentSerializer, 
    MobileMoneyVerificationSerializer, MobileMoneyInitiateSerializer
)

class MobileMoneyProviderListView(generics.ListAPIView):
    """List available mobile money providers"""
    serializer_class = MobileMoneyProviderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MobileMoneyProvider.objects.filter(is_active=True)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_mobile_payment(request):
    """Initiate mobile money payment"""
    try:
        serializer = MobileMoneyInitiateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        booking_id = serializer.validated_data['booking_id']
        provider_code = serializer.validated_data['provider_code']
        phone_number = serializer.validated_data['phone_number']
        
        # Get booking and payment
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # Check if payment already exists
        if hasattr(booking, 'payment') and booking.payment:
            return Response({
                'error': 'Payment already initiated for this booking'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment record
        with transaction.atomic():
            payment = Payment.objects.create(
                booking=booking,
                payment_id=f"MOBILE_{booking_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                amount=booking.final_amount,
                payment_method='mobile_money',
                payment_status='pending'
            )
            
            # Initiate mobile money payment
            result = mobile_money_service.initiate_payment(payment, provider_code, phone_number)
            
            if result['success']:
                return Response({
                    'success': True,
                    'message': 'Mobile money payment initiated successfully',
                    'transaction_id': result['transaction_id'],
                    'confirmation_code': result.get('confirmation_code'),
                    'ussd_session_id': result.get('ussd_session_id'),
                    'instructions': result.get('instructions'),
                    'status': result['status'],
                    'provider': provider_code
                }, status=status.HTTP_200_OK)
            else:
                # Mark payment as failed
                payment.payment_status = 'failed'
                payment.save()
                
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to initiate mobile money payment'),
                    'details': result
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Booking.DoesNotExist:
        return Response({
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'Failed to initiate mobile money payment',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_phone_number(request):
    """Verify phone number for mobile money"""
    try:
        serializer = MobileMoneyVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        provider_code = serializer.validated_data['provider_code']
        phone_number = serializer.validated_data['phone_number']
        
        # Initiate verification
        result = mobile_money_service.verify_phone_number(request.user, provider_code, phone_number)
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'Verification code sent successfully',
                'verification_id': result['verification_id'],
                'expires_at': result['expires_at']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to send verification code')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Failed to verify phone number',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_verification(request):
    """Confirm phone number verification"""
    try:
        verification_id = request.data.get('verification_id')
        verification_code = request.data.get('verification_code')
        
        if not verification_id or not verification_code:
            return Response({
                'error': 'Verification ID and code are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = mobile_money_service.confirm_verification(verification_id, verification_code)
        
        if result['success']:
            return Response({
                'success': True,
                'message': result['message']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Invalid verification code'),
                'attempts_remaining': result.get('attempts_remaining', 0)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Failed to confirm verification',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_payment_status(request, transaction_id):
    """Check mobile money payment status"""
    try:
        result = mobile_money_service.check_payment_status(transaction_id)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to check payment status')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Failed to check payment status',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retry_payment(request):
    """Retry failed mobile money payment"""
    try:
        transaction_id = request.data.get('transaction_id')
        
        if not transaction_id:
            return Response({
                'error': 'Transaction ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mobile_payment = get_object_or_404(MobileMoneyPayment, transaction_id=transaction_id)
        
        # Check if retry is allowed
        if mobile_payment.retry_count >= mobile_payment.max_retries:
            return Response({
                'error': 'Maximum retry attempts exceeded',
                'attempts': mobile_payment.retry_count
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Increment retry count
        mobile_payment.retry_count += 1
        mobile_payment.next_retry_at = timezone.now() + timezone.timedelta(minutes=5)
        mobile_payment.save()
        
        # Retry payment
        result = mobile_money_service._process_with_provider(
            mobile_payment.provider, 
            mobile_payment, 
            mobile_payment.phone_number
        )
        
        if result['success']:
            mobile_payment.status = result['status']
            mobile_payment.provider_response = result['response']
            mobile_payment.save()
            
            return Response({
                'success': True,
                'message': 'Payment retry initiated successfully',
                'status': result['status'],
                'retry_count': mobile_payment.retry_count
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Payment retry failed')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except MobileMoneyPayment.DoesNotExist:
        return Response({
            'error': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'Failed to retry payment',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_mobile_payments(request):
    """Get user's mobile money payment history"""
    try:
        mobile_payments = MobileMoneyPayment.objects.filter(
            payment__booking__user=request.user
        ).select_related('payment', 'provider', 'payment__booking').order_by('-created_at')
        
        serializer = MobileMoneyPaymentSerializer(mobile_payments, many=True)
        
        return Response({
            'success': True,
            'count': mobile_payments.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch mobile payments',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_payment_statistics(request):
    """Get mobile money payment statistics for user"""
    try:
        mobile_payments = MobileMoneyPayment.objects.filter(
            payment__booking__user=request.user
        )
        
        stats = {
            'total_mobile_payments': mobile_payments.count(),
            'successful_payments': mobile_payments.filter(status='completed').count(),
            'pending_payments': mobile_payments.filter(status__in=['initiated', 'pending', 'confirmed']).count(),
            'failed_payments': mobile_payments.filter(status='failed').count(),
            'total_amount': sum(p.amount for p in mobile_payments.filter(status='completed')),
            'total_fees': sum(p.fee_amount for p in mobile_payments.filter(status='completed')),
            'providers_used': list(mobile_payments.values_list('provider__display_name', flat=True).distinct()),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch mobile payment statistics',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
