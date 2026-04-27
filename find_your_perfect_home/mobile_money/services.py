"""
Mobile Money Services for Uganda Payment Integration
"""
import requests
import json
import uuid
import hashlib
import hmac
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from .models import MobileMoneyProvider, MobileMoneyPayment, MobileMoneyVerification, MobileMoneyTransactionLog
from payments.models import Payment
from bookings.models import Booking
import logging

logger = logging.getLogger(__name__)

class MobileMoneyService:
    """Service for handling Uganda mobile money payments"""
    
    def __init__(self):
        self.providers_cache = {}
    
    def get_provider(self, provider_code):
        """Get mobile money provider by code"""
        if provider_code not in self.providers_cache:
            try:
                provider = MobileMoneyProvider.objects.get(code=provider_code, is_active=True)
                self.providers_cache[provider_code] = provider
            except MobileMoneyProvider.DoesNotExist:
                raise ValueError(f"Provider {provider_code} not found or inactive")
        return self.providers_cache[provider_code]
    
    def initiate_payment(self, payment, provider_code, phone_number):
        """Initiate mobile money payment"""
        try:
            provider = self.get_provider(provider_code)
            
            # Validate amount
            if payment.amount < provider.min_amount or payment.amount > provider.max_amount:
                raise ValueError(f"Amount must be between UGX {provider.min_amount:,} and UGX {provider.max_amount:,}")
            
            # Create mobile money payment record
            mobile_payment = MobileMoneyPayment.objects.create(
                payment=payment,
                provider=provider,
                phone_number=phone_number,
                amount=payment.amount,
                transaction_id=f"MMO_{provider.code}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            )
            
            # Log initiation
            self._log_transaction(
                provider=provider,
                transaction=mobile_payment,
                action_type='payment_initiated',
                request_data={
                    'amount': str(payment.amount),
                    'phone_number': phone_number,
                    'booking_id': payment.booking.id
                },
                success=True
            )
            
            # Process with provider
            result = self._process_with_provider(provider, mobile_payment, phone_number)
            
            # Update mobile payment record
            mobile_payment.status = result['status']
            mobile_payment.provider_response = result['response']
            mobile_payment.confirmation_code = result.get('confirmation_code', '')
            mobile_payment.ussd_session_id = result.get('ussd_session_id', '')
            mobile_payment.save()
            
            # Log result
            self._log_transaction(
                provider=provider,
                transaction=mobile_payment,
                action_type='payment_completed' if result['success'] else 'payment_failed',
                request_data=result.get('request_data', {}),
                response_data=result['response'],
                success=result['success'],
                error_code=result.get('error_code'),
                error_message=result.get('error_message')
            )
            
            return {
                'success': result['success'],
                'transaction_id': mobile_payment.transaction_id,
                'confirmation_code': result.get('confirmation_code'),
                'ussd_session_id': result.get('ussd_session_id'),
                'instructions': result.get('instructions'),
                'status': mobile_payment.status
            }
            
        except Exception as e:
            logger.error(f"Mobile money payment initiation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_phone_number(self, user, provider_code, phone_number):
        """Verify phone number for mobile money"""
        try:
            provider = self.get_provider(provider_code)
            
            # Generate verification code
            verification_code = f"{uuid.uuid4().int % 1000000:06d}"
            
            # Create verification record
            verification = MobileMoneyVerification.objects.create(
                user=user,
                provider=provider,
                phone_number=phone_number,
                verification_code=verification_code,
                verification_type='sms' if provider.supports_app else 'ussd',
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            # Send verification
            sent = self._send_verification_code(provider, phone_number, verification_code)
            
            if sent:
                self._log_transaction(
                    provider=provider,
                    action_type='verification_sent',
                    request_data={'phone_number': phone_number},
                    response_data={'verification_sent': True},
                    success=True
                )
            
            return {
                'success': sent,
                'verification_id': verification.id,
                'expires_at': verification.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Phone verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def confirm_verification(self, verification_id, verification_code):
        """Confirm phone number verification"""
        try:
            verification = MobileMoneyVerification.objects.get(id=verification_id)
            
            if verification.is_expired():
                return {
                    'success': False,
                    'error': 'Verification code has expired'
                }
            
            if verification.verification_attempts >= verification.max_attempts:
                return {
                    'success': False,
                    'error': 'Maximum verification attempts exceeded'
                }
            
            # Increment attempts
            verification.verification_attempts += 1
            
            if verification.verification_code == verification_code:
                verification.is_verified = True
                verification.verified_at = timezone.now()
                verification.save()
                
                return {
                    'success': True,
                    'message': 'Phone number verified successfully'
                }
            else:
                verification.save()
                return {
                    'success': False,
                    'error': 'Invalid verification code',
                    'attempts_remaining': verification.max_attempts - verification.verification_attempts
                }
                
        except MobileMoneyVerification.DoesNotExist:
            return {
                'success': False,
                'error': 'Invalid verification ID'
            }
        except Exception as e:
            logger.error(f"Verification confirmation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_payment_status(self, transaction_id):
        """Check status of mobile money payment"""
        try:
            mobile_payment = MobileMoneyPayment.objects.get(transaction_id=transaction_id)
            provider = mobile_payment.provider
            
            # Check with provider
            status_result = self._check_status_with_provider(provider, mobile_payment)
            
            # Update status if changed
            if status_result['status'] != mobile_payment.status:
                old_status = mobile_payment.status
                mobile_payment.status = status_result['status']
                
                if status_result['status'] == 'completed':
                    mobile_payment.completed_at = timezone.now()
                elif status_result['status'] == 'confirmed':
                    mobile_payment.confirmed_at = timezone.now()
                
                mobile_payment.save()
                
                # Update main payment status
                if status_result['status'] == 'completed':
                    payment = mobile_payment.payment
                    payment.payment_status = 'fully_paid'
                    payment.save()
                
                # Log status change
                self._log_transaction(
                    provider=provider,
                    transaction=mobile_payment,
                    action_type='payment_completed',
                    response_data=status_result['response'],
                    success=True
                )
            
            return {
                'success': True,
                'status': mobile_payment.status,
                'amount': mobile_payment.amount,
                'provider': provider.display_name,
                'confirmed_at': mobile_payment.confirmed_at.isoformat() if mobile_payment.confirmed_at else None,
                'completed_at': mobile_payment.completed_at.isoformat() if mobile_payment.completed_at else None
            }
            
        except MobileMoneyPayment.DoesNotExist:
            return {
                'success': False,
                'error': 'Transaction not found'
            }
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_with_provider(self, provider, mobile_payment, phone_number):
        """Process payment with specific provider"""
        # This is a mock implementation - in production, integrate with actual provider APIs
        
        if provider.code == 'MTN_MOMO':
            return self._process_mtn_payment(mobile_payment, phone_number)
        elif provider.code == 'AIRTEL_MONEY':
            return self._process_airtel_payment(mobile_payment, phone_number)
        elif provider.code == 'STANBIC_MOBILE':
            return self._process_stanbic_payment(mobile_payment, phone_number)
        else:
            # Default processing for other providers
            return self._process_generic_payment(mobile_payment, phone_number)
    
    def _process_mtn_payment(self, mobile_payment, phone_number):
        """Process MTN Mobile Money payment"""
        try:
            # Mock MTN API call
            # In production, integrate with actual MTN MoMo API
            
            # Generate USSD session
            ussd_session = f"MTN_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            # Simulate USSD prompt
            ussd_instructions = {
                'ussd_code': '*165*4#',
                'steps': [
                    'Dial *165*4#',
                    'Enter amount: UGX {:,}'.format(mobile_payment.amount),
                    'Enter PIN to confirm',
                    'Wait for confirmation SMS'
                ]
            }
            
            return {
                'success': True,
                'status': 'pending',
                'confirmation_code': f"CONF_{uuid.uuid4().hex[:6].upper()}",
                'ussd_session_id': ussd_session,
                'instructions': ussd_instructions,
                'response': {
                    'transaction_id': mobile_payment.transaction_id,
                    'ussd_session': ussd_session,
                    'status': 'ussd_initiated'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {'error': 'MTN API error'}
            }
    
    def _process_airtel_payment(self, mobile_payment, phone_number):
        """Process Airtel Money payment"""
        try:
            # Mock Airtel API call
            # In production, integrate with actual Airtel Money API
            
            return {
                'success': True,
                'status': 'confirmed',
                'confirmation_code': f"AIRTEL_{uuid.uuid4().hex[:6].upper()}",
                'instructions': {
                    'app_prompt': 'Open Airtel Money app',
                    'steps': [
                        'Check notification in Airtel Money app',
                        'Enter PIN to authorize payment',
                        'Payment will be processed instantly'
                    ]
                },
                'response': {
                    'transaction_id': mobile_payment.transaction_id,
                    'status': 'app_confirmed'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {'error': 'Airtel API error'}
            }
    
    def _process_stanbic_payment(self, mobile_payment, phone_number):
        """Process Stanbic Mobile payment"""
        try:
            # Mock Stanbic API call
            # In production, integrate with actual Stanbic Mobile API
            
            return {
                'success': True,
                'status': 'completed',
                'confirmation_code': f"STANBIC_{uuid.uuid4().hex[:6].upper()}",
                'instructions': {
                    'app_prompt': 'Open Stanbic Mobile app',
                    'steps': [
                        'Check transaction notification',
                        'Approve payment in app',
                        'Payment processed immediately'
                    ]
                },
                'response': {
                    'transaction_id': mobile_payment.transaction_id,
                    'status': 'completed'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {'error': 'Stanbic API error'}
            }
    
    def _process_generic_payment(self, mobile_payment, phone_number):
        """Generic payment processing for other providers"""
        try:
            return {
                'success': True,
                'status': 'pending',
                'confirmation_code': f"GENERIC_{uuid.uuid4().hex[:6].upper()}",
                'instructions': {
                    'general': f'Follow {mobile_payment.provider.display_name} payment instructions',
                    'steps': [
                        'Check your mobile money app',
                        'Authorize the payment',
                        'Wait for confirmation'
                    ]
                },
                'response': {
                    'transaction_id': mobile_payment.transaction_id,
                    'status': 'initiated'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {'error': 'Provider API error'}
            }
    
    def _check_status_with_provider(self, provider, mobile_payment):
        """Check payment status with provider"""
        try:
            # Mock status check - in production, integrate with actual provider APIs
            import random
            
            # Simulate different status outcomes
            if random.random() > 0.8:  # 20% chance of completion
                return {
                    'status': 'completed',
                    'response': {
                        'transaction_id': mobile_payment.transaction_id,
                        'status': 'completed',
                        'completed_at': timezone.now().isoformat()
                    }
                }
            elif random.random() > 0.5:  # 30% chance of confirmation
                return {
                    'status': 'confirmed',
                    'response': {
                        'transaction_id': mobile_payment.transaction_id,
                        'status': 'confirmed',
                        'confirmed_at': timezone.now().isoformat()
                    }
                }
            else:  # 50% chance of still pending
                return {
                    'status': 'pending',
                    'response': {
                        'transaction_id': mobile_payment.transaction_id,
                        'status': 'pending',
                        'message': 'Payment is being processed'
                    }
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'response': {'error': str(e)}
            }
    
    def _send_verification_code(self, provider, phone_number, verification_code):
        """Send verification code via SMS or USSD"""
        try:
            if provider.supports_ussd:
                # USSD verification for providers that support it
                ussd_message = f"Your RentHu verification code is: {verification_code}"
                # In production, integrate with actual USSD gateway
                logger.info(f"USSD verification sent to {phone_number}: {verification_code}")
                return True
            else:
                # SMS verification
                # In production, integrate with SMS gateway (Twilio, Africa's Talking, etc.)
                logger.info(f"SMS verification sent to {phone_number}: {verification_code}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send verification code: {str(e)}")
            return False
    
    def _log_transaction(self, provider, transaction=None, action_type=None, request_data=None, response_data=None, success=False, error_code=None, error_message=None):
        """Log mobile money transactions"""
        MobileMoneyTransactionLog.objects.create(
            provider=provider,
            transaction=transaction,
            action_type=action_type,
            request_data=request_data or {},
            response_data=response_data or {},
            processing_time_ms=None,  # Would be calculated in real implementation
            success=success,
            error_code=error_code,
            error_message=error_message
        )

# Create service instance
mobile_money_service = MobileMoneyService()
