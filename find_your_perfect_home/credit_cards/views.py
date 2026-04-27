"""
Credit Card API Views
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from .models import CreditCardProvider, CreditCardPayment, SavedCreditCard
from .services import credit_card_service
from payments.models import Payment
from bookings.models import Booking
from .serializers import (
    CreditCardProviderSerializer, CreditCardPaymentSerializer, 
    SavedCreditCardSerializer, CreditCardInitiateSerializer
)

class CreditCardProviderListView(generics.ListAPIView):
    """List available credit card providers"""
    serializer_class = CreditCardProviderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CreditCardProvider.objects.filter(is_active=True)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_credit_card_payment(request):
    """Initiate credit card payment"""
    try:
        serializer = CreditCardInitiateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        booking_id = serializer.validated_data['booking_id']
        provider_code = serializer.validated_data['provider_code']
        card_data = serializer.validated_data['card_data']
        
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
                payment_id=f"CC_{booking_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                amount=booking.final_amount,
                payment_method='credit_card',
                payment_status='pending'
            )
            
            # Add IP and user agent
            card_data['ip_address'] = request.META.get('REMOTE_ADDR', '127.0.0.1')
            card_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            
            # Initiate credit card payment
            result = credit_card_service.initiate_payment(payment, provider_code, card_data)
            
            if result['success']:
                return Response({
                    'success': True,
                    'message': 'Credit card payment initiated successfully',
                    'transaction_id': result['transaction_id'],
                    'status': result['status'],
                    'requires_3ds': result.get('requires_3ds', False),
                    'three_d_secure_url': result.get('three_d_secure_url'),
                    'authorization_code': result.get('authorization_code'),
                    'fraud_score': result.get('fraud_score'),
                    'risk_level': result.get('risk_level')
                }, status=status.HTTP_200_OK)
            else:
                # Mark payment as failed
                payment.payment_status = 'failed'
                payment.save()
                
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to initiate credit card payment'),
                    'details': result
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Booking.DoesNotExist:
        return Response({
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'Failed to initiate credit card payment',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_credit_card(request):
    """Save credit card for future use"""
    try:
        serializer = SavedCreditCardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        provider_code = serializer.validated_data['provider_code']
        card_data = serializer.validated_data['card_data']
        
        # Add IP and user agent
        card_data['ip_address'] = request.META.get('REMOTE_ADDR', '127.0.0.1')
        card_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        # Save card
        result = credit_card_service.save_card_for_user(request.user, provider_code, card_data)
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'Credit card saved successfully',
                'card_id': result['card_id'],
                'masked_card': result['masked_card'],
                'card_type': result['card_type'],
                'expires_at': result['expires_at']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to save credit card')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Failed to save credit card',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment_with_saved_card(request):
    """Initiate payment using saved card"""
    try:
        booking_id = request.data.get('booking_id')
        saved_card_id = request.data.get('saved_card_id')
        
        if not booking_id or not saved_card_id:
            return Response({
                'error': 'Booking ID and saved card ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get booking
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
                payment_id=f"CC_SAVED_{booking_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                amount=booking.final_amount,
                payment_method='credit_card',
                payment_status='pending'
            )
            
            # Process payment with saved card
            result = credit_card_service.initiate_payment_with_saved_card(payment, saved_card_id)
            
            if result['success']:
                return Response({
                    'success': True,
                    'message': 'Payment initiated with saved card successfully',
                    'transaction_id': result['transaction_id'],
                    'status': result['status'],
                    'requires_3ds': result.get('requires_3ds', False),
                    'three_d_secure_url': result.get('three_d_secure_url'),
                    'authorization_code': result.get('authorization_code'),
                    'fraud_score': result.get('fraud_score'),
                    'risk_level': result.get('risk_level')
                }, status=status.HTTP_200_OK)
            else:
                # Mark payment as failed
                payment.payment_status = 'failed'
                payment.save()
                
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to initiate payment with saved card')
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Booking.DoesNotExist:
        return Response({
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'Failed to initiate payment with saved card',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_payment_status(request, transaction_id):
    """Check credit card payment status"""
    try:
        result = credit_card_service.check_payment_status(transaction_id)
        
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_saved_cards(request):
    """Get user's saved credit cards"""
    try:
        saved_cards = SavedCreditCard.objects.filter(
            user=request.user,
            expires_at__gt=timezone.now()
        ).select_related('provider').order_by('-created_at')
        
        serializer = SavedCreditCardSerializer(saved_cards, many=True)
        
        return Response({
            'success': True,
            'count': saved_cards.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch saved cards',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_saved_card(request, card_id):
    """Delete saved credit card"""
    try:
        saved_card = get_object_or_404(SavedCreditCard, id=card_id, user=request.user)
        
        # Check if card has pending transactions
        pending_payments = CreditCardPayment.objects.filter(
            payment__booking__user=request.user,
            status__in=['initiated', 'processing', 'authorized']
        ).filter(
            card_last_four=saved_card.card_last_four,
            card_expiry_month=saved_card.card_expiry_month,
            card_expiry_year=saved_card.card_expiry_year
        )
        
        if pending_payments.exists():
            return Response({
                'error': 'Cannot delete card with pending transactions'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        saved_card.delete()
        
        return Response({
            'success': True,
            'message': 'Credit card deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to delete credit card',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_default_card(request, card_id):
    """Set default credit card"""
    try:
        saved_card = get_object_or_404(SavedCreditCard, id=card_id, user=request.user)
        
        # Remove default from all other cards
        SavedCreditCard.objects.filter(user=request.user).update(is_default=False)
        
        # Set this card as default
        saved_card.is_default = True
        saved_card.save()
        
        return Response({
            'success': True,
            'message': 'Default card updated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to set default card',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_credit_card_payments(request):
    """Get user's credit card payment history"""
    try:
        credit_payments = CreditCardPayment.objects.filter(
            payment__booking__user=request.user
        ).select_related('payment', 'provider', 'payment__booking').order_by('-created_at')
        
        serializer = CreditCardPaymentSerializer(credit_payments, many=True)
        
        return Response({
            'success': True,
            'count': credit_payments.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch credit card payments',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def credit_card_statistics(request):
    """Get credit card payment statistics for user"""
    try:
        credit_payments = CreditCardPayment.objects.filter(
            payment__booking__user=request.user
        )
        
        stats = {
            'total_credit_card_payments': credit_payments.count(),
            'successful_payments': credit_payments.filter(status='completed').count(),
            'pending_payments': credit_payments.filter(status__in=['initiated', 'processing', 'authorized']).count(),
            'failed_payments': credit_payments.filter(status='failed').count(),
            'total_amount': sum(p.amount for p in credit_payments.filter(status='completed')),
            'total_fees': sum(p.fee_amount for p in credit_payments.filter(status='completed')),
            'providers_used': list(credit_payments.values_list('provider__display_name', flat=True).distinct()),
            'card_types_used': list(credit_payments.values_list('card_type', flat=True).distinct()),
            'saved_cards_count': SavedCreditCard.objects.filter(user=request.user, expires_at__gt=timezone.now()).count(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch credit card statistics',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
