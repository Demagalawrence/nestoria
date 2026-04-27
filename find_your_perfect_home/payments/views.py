from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings
import stripe
from .models import Payment, Receipt, Commission
from bookings.models import Booking
from .serializers import PaymentSerializer, PaymentCreateSerializer, ReceiptSerializer
from .email_service import secure_email_service

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        elif user.role == 'owner':
            return Payment.objects.filter(booking__rental_property__owner=user)
        else:
            return Payment.objects.filter(booking__user=user)

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        elif user.role == 'owner':
            return Payment.objects.filter(booking__rental_property__owner=user)
        else:
            return Payment.objects.filter(booking__user=user)

class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()
        
        # Create receipt
        payment = serializer.instance
        receipt = Receipt.objects.create(
            payment=payment,
            receipt_number=payment.generate_receipt_number()
        )
        
        # Create commission
        Commission.objects.create(
            payment=payment,
            property_owner=payment.booking.rental_property.owner,
            commission_amount=payment.commission_amount
        )

class ProcessPaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        payment_id = request.data.get('payment_id')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            booking = payment.booking
            
            # Check permissions
            if request.user != booking.user and request.user.role != 'admin':
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            # Process payment (simulate successful payment)
            payment.payment_status = 'completed'
            payment.transaction_id = payment.payment_id
            payment.save()
            
            # Update booking payment status
            booking.payment_status = 'fully_paid'
            booking.save()
            
            # Create receipt if it doesn't exist
            receipt, created = Receipt.objects.get_or_create(
                payment=payment,
                defaults={'receipt_number': f"RCT-{timezone.now().strftime('%Y%m%d')}-{payment.payment_id[-8:]}"}
            )
            
            # Send receipt email (try but continue if fails)
            try:
                secure_email_service.send_payment_receipt_email(
                    payment=payment,
                    receipt=receipt,
                    user_email=booking.user.email
                )
                receipt.is_sent = True
                receipt.save()
            except Exception as email_error:
                print(f"Failed to send receipt email: {str(email_error)}")
            
            return Response({
                'success': True,
                'payment_id': payment.payment_id,
                'receipt_number': receipt.receipt_number,
                'message': 'Payment processed successfully'
            })
            
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PaymentSuccessView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')
        booking_id = request.data.get('booking_id')
        
        try:
            booking = Booking.objects.get(id=booking_id)
            
            # Retrieve payment intent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Create payment record
                payment = Payment.objects.create(
                    booking=booking,
                    payment_id=payment_intent_id,
                    amount=booking.final_amount,
                    payment_method='credit_card',
                    payment_status='completed',
                    transaction_id=payment_intent_id
                )
                
                # Update booking payment status and confirm booking
                booking.payment_status = 'fully_paid'
                booking.status = 'confirmed'
                booking.save()
                
                # Create receipt
                receipt = Receipt.objects.create(
                    payment=payment,
                    receipt_number=payment.generate_receipt_number()
                )
                
                # Send secure receipt email
                try:
                    email_sent = secure_email_service.send_payment_receipt_email(
                        payment=payment,
                        receipt=receipt,
                        user_email=booking.user.email
                    )
                    if email_sent:
                        receipt.is_sent = True
                        receipt.save()
                except Exception as email_error:
                    print(f"Failed to send receipt email: {str(email_error)}")
                    # Continue even if email fails
                
                # Create commission
                Commission.objects.create(
                    payment=payment,
                    property_owner=booking.rental_property.owner,
                    commission_amount=payment.commission_amount
                )
                
                return Response({
                    'message': 'Payment successful',
                    'payment_id': payment.payment_id,
                    'receipt_number': receipt.receipt_number
                })
            else:
                return Response({'error': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PaymentFailedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')
        error_message = request.data.get('error_message', 'Payment failed')
        
        try:
            # Create failed payment record
            payment = Payment.objects.create(
                payment_id=payment_intent_id,
                amount=0,  # Will be updated based on booking
                payment_method='credit_card',
                payment_status='failed',
                transaction_id=payment_intent_id,
                gateway_response={'error': error_message}
            )
            
            return Response({
                'message': 'Payment failure recorded',
                'payment_id': payment.payment_id
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(generics.GenericAPIView):
    permission_classes = []
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            booking_id = payment_intent['metadata'].get('booking_id')
            
            if booking_id:
                try:
                    booking = Booking.objects.get(id=booking_id)
                    
                    # Create payment record
                    payment = Payment.objects.create(
                        booking=booking,
                        payment_id=payment_intent['id'],
                        amount=booking.final_amount,
                        payment_method='credit_card',
                        payment_status='completed',
                        transaction_id=payment_intent['id']
                    )
                    
                    # Update booking payment status and confirm booking
                    booking.payment_status = 'fully_paid'
                    booking.status = 'confirmed'
                    booking.save()
                    
                    # Create receipt and commission
                    receipt = Receipt.objects.create(
                        payment=payment,
                        receipt_number=payment.generate_receipt_number()
                    )
                    
                    # Send secure receipt email
                    try:
                        email_sent = secure_email_service.send_payment_receipt_email(
                            payment=payment,
                            receipt=receipt,
                            user_email=booking.user.email
                        )
                        if email_sent:
                            receipt.is_sent = True
                            receipt.save()
                    except Exception as email_error:
                        print(f"Failed to send receipt email: {str(email_error)}")
                    
                    Commission.objects.create(
                        payment=payment,
                        property_owner=booking.rental_property.owner,
                        commission_amount=payment.commission_amount
                    )
                    
                except Booking.DoesNotExist:
                    pass
        
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class ReceiptView(generics.RetrieveAPIView):
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Receipt.objects.all()
        elif user.role == 'owner':
            return Receipt.objects.filter(payment__booking__rental_property__owner=user)
        else:
            return Receipt.objects.filter(payment__booking__user=user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_statistics(request):
    user = request.user
    
    if user.role == 'admin':
        payments = Payment.objects.all()
    elif user.role == 'owner':
        payments = Payment.objects.filter(booking__rental_property__owner=user)
    else:
        payments = Payment.objects.filter(booking__user=user)
    
    stats = {
        'total_payments': payments.count(),
        'completed_payments': payments.filter(payment_status='completed').count(),
        'failed_payments': payments.filter(payment_status='failed').count(),
        'pending_payments': payments.filter(payment_status='pending').count(),
        'total_revenue': sum(p.amount for p in payments.filter(payment_status='completed')),
        'total_commission': sum(p.commission_amount for p in payments.filter(payment_status='completed')),
    }
    
    return Response(stats)
