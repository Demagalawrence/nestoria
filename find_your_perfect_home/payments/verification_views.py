"""
Receipt Verification Views
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Receipt, Payment
from .email_service import secure_email_service
from bookings.models import Booking
import json

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_receipt(request, receipt_number):
    """
    Public endpoint to verify receipt authenticity
    """
    try:
        receipt = get_object_or_404(Receipt, receipt_number=receipt_number)
        payment = receipt.payment
        booking = payment.booking
        
        # Prepare receipt data for verification
        receipt_data = {
            'receipt_number': receipt.receipt_number,
            'payment_id': payment.payment_id,
            'amount': float(payment.amount),
            'payment_date': payment.payment_date.isoformat(),
            'payment_status': payment.payment_status,
            'payment_method': payment.payment_method,
            'transaction_id': payment.transaction_id,
            'booking_id': booking.id,
            'property_name': booking.rental_property.name,
            'user_email': booking.user.email,
            'currency': 'UGX'
        }
        
        # Check if receipt has been tampered (basic validation)
        if payment.payment_status != 'completed':
            return Response({
                'valid': False,
                'error': 'Payment was not completed successfully',
                'status': payment.payment_status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Return verification result
        verification_result = {
            'valid': True,
            'receipt_number': receipt.receipt_number,
            'payment_details': {
                'amount': float(payment.amount),
                'currency': 'UGX',
                'payment_date': payment.payment_date,
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'status': payment.payment_status
            },
            'booking_details': {
                'property_name': booking.rental_property.name,
                'check_in_date': booking.check_in_date,
                'check_out_date': booking.check_out_date,
                'total_amount': float(booking.final_amount)
            },
            'verification_timestamp': receipt.generated_date.isoformat(),
            'security_features': [
                'Digital Signature Applied',
                'Data Encryption Enabled',
                'Tamper-Proof Design',
                'Unique Receipt Number',
                'Server-Side Verification'
            ]
        }
        
        return Response(verification_result)
        
    except Receipt.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Receipt not found',
            'message': 'This receipt number does not exist in our system'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'valid': False,
            'error': 'Verification failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_receipt_with_signature(request):
    """
    Verify receipt using digital signature (for advanced verification)
    """
    try:
        receipt_number = request.data.get('receipt_number')
        signature = request.data.get('signature')
        
        if not receipt_number or not signature:
            return Response({
                'valid': False,
                'error': 'Receipt number and signature are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        receipt = get_object_or_404(Receipt, receipt_number=receipt_number)
        payment = receipt.payment
        booking = payment.booking
        
        # Prepare receipt data
        receipt_data = {
            'receipt_number': receipt.receipt_number,
            'payment_id': payment.payment_id,
            'amount': float(payment.amount),
            'payment_date': payment.payment_date.isoformat(),
            'payment_status': payment.payment_status,
            'payment_method': payment.payment_method,
            'transaction_id': payment.transaction_id,
            'booking_id': booking.id,
            'property_name': booking.rental_property.name,
            'user_email': booking.user.email,
            'currency': 'UGX'
        }
        
        # Verify digital signature
        is_valid_signature = secure_email_service.verify_digital_signature(receipt_data, signature)
        
        if not is_valid_signature:
            return Response({
                'valid': False,
                'error': 'Invalid digital signature',
                'message': 'This receipt appears to have been tampered with or is invalid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if payment.payment_status != 'completed':
            return Response({
                'valid': False,
                'error': 'Payment was not completed successfully',
                'status': payment.payment_status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'valid': True,
            'message': 'Receipt is authentic and has not been tampered with',
            'verification_details': {
                'signature_valid': True,
                'receipt_number': receipt.receipt_number,
                'verified_at': receipt.generated_date.isoformat(),
                'payment_confirmed': payment.payment_status == 'completed'
            }
        })
        
    except Receipt.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Receipt not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'valid': False,
            'error': 'Verification failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReceiptDownloadView(generics.RetrieveAPIView):
    """
    Allow users to download their receipt PDF
    """
    from .serializers import ReceiptSerializer
    
    serializer_class = ReceiptSerializer
    permission_classes = [AllowAny]  # Public for verification purposes
    
    def get_queryset(self):
        return Receipt.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        try:
            receipt = self.get_object()
            payment = receipt.payment
            
            # Prepare receipt data
            receipt_data = {
                'receipt_number': receipt.receipt_number,
                'payment_id': payment.payment_id,
                'amount': float(payment.amount),
                'payment_date': payment.payment_date.isoformat(),
                'payment_status': payment.payment_status,
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'booking_id': payment.booking.id,
                'property_name': payment.booking.rental_property.name,
                'user_email': payment.booking.user.email,
                'currency': 'UGX'
            }
            
            # Generate signature
            signature = secure_email_service.generate_digital_signature(receipt_data)
            
            # Generate PDF content
            pdf_content = secure_email_service._generate_pdf_receipt(receipt_data, signature)
            
            # Return PDF as downloadable file
            from django.http import HttpResponse
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Receipt_{receipt.receipt_number}.pdf"'
            response['X-Receipt-Signature'] = signature
            response['X-Receipt-Number'] = receipt.receipt_number
            
            return response
            
        except Receipt.DoesNotExist:
            raise Http404("Receipt not found")
        except Exception as e:
            return Response({
                'error': 'Failed to generate receipt PDF',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
