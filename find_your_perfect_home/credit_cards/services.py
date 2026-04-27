"""
Credit Card Payment Services for Uganda Rental Platform
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
from .models import CreditCardProvider, CreditCardPayment, SavedCreditCard, CreditCardVerification, CreditCardTransactionLog
from payments.models import Payment
from bookings.models import Booking
import logging

logger = logging.getLogger(__name__)

class CreditCardService:
    """Service for handling credit card payments"""
    
    def __init__(self):
        self.providers_cache = {}
    
    def get_provider(self, provider_code):
        """Get credit card provider by code"""
        if provider_code not in self.providers_cache:
            try:
                provider = CreditCardProvider.objects.get(code=provider_code, is_active=True)
                self.providers_cache[provider_code] = provider
            except CreditCardProvider.DoesNotExist:
                raise ValueError(f"Provider {provider_code} not found or inactive")
        return self.providers_cache[provider_code]
    
    def initiate_payment(self, payment, provider_code, card_data):
        """Initiate credit card payment"""
        try:
            provider = self.get_provider(provider_code)
            
            # Validate amount
            if payment.amount < provider.min_amount or payment.amount > provider.max_amount:
                raise ValueError(f"Amount must be between UGX {provider.min_amount:,} and UGX {provider.max_amount:,}")
            
            # Validate card data
            self._validate_card_data(card_data)
            
            # Create credit card payment record
            credit_payment = CreditCardPayment.objects.create(
                payment=payment,
                provider=provider,
                transaction_id=f"CC_{provider.code}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
                card_type=self._detect_card_type(card_data['card_number']),
                card_last_four=card_data['card_number'][-4:],
                card_expiry_month=int(card_data['expiry_date'].split('/')[0]),
                card_expiry_year=int(card_data['expiry_date'].split('/')[1]),
                cardholder_name=card_data['cardholder_name'],
                billing_address=card_data.get('billing_address', {}),
                amount=payment.amount,
                currency='UGX',
            )
            
            # Create verification record
            verification = CreditCardVerification.objects.create(
                payment=credit_payment,
                ip_address=card_data.get('ip_address', '127.0.0.1'),
                user_agent=card_data.get('user_agent', ''),
            )
            
            # Perform fraud check
            fraud_result = self._perform_fraud_check(credit_payment, card_data)
            verification.fraud_score = fraud_result['score']
            verification.risk_level = fraud_result['risk_level']
            verification.save()
            
            # Log initiation
            self._log_transaction(
                provider=provider,
                transaction=credit_payment,
                action_type='payment_initiated',
                request_data={
                    'amount': str(payment.amount),
                    'card_type': credit_payment.card_type,
                    'card_last_four': credit_payment.card_last_four,
                    'fraud_score': fraud_result['score']
                },
                success=True,
                ip_address=card_data.get('ip_address'),
                user_agent=card_data.get('user_agent')
            )
            
            # Process with provider
            result = self._process_with_provider(provider, credit_payment, card_data)
            
            # Update credit payment record
            credit_payment.status = result['status']
            credit_payment.provider_response = result['response']
            credit_payment.authorization_code = result.get('authorization_code', '')
            credit_payment.requires_3ds = result.get('requires_3ds', False)
            credit_payment.three_d_secure_url = result.get('three_d_secure_url', '')
            credit_payment.save()
            
            # Log result
            self._log_transaction(
                provider=provider,
                transaction=credit_payment,
                action_type='payment_completed' if result['success'] else 'payment_failed',
                request_data=result.get('request_data', {}),
                response_data=result['response'],
                success=result['success'],
                error_code=result.get('error_code'),
                error_message=result.get('error_message')
            )
            
            return {
                'success': result['success'],
                'transaction_id': credit_payment.transaction_id,
                'status': credit_payment.status,
                'requires_3ds': credit_payment.requires_3ds,
                'three_d_secure_url': credit_payment.three_d_secure_url,
                'authorization_code': credit_payment.authorization_code,
                'fraud_score': fraud_result['score'],
                'risk_level': fraud_result['risk_level']
            }
            
        except Exception as e:
            logger.error(f"Credit card payment initiation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_card_for_user(self, user, provider_code, card_data):
        """Save credit card for future use"""
        try:
            provider = self.get_provider(provider_code)
            
            # Validate card data
            self._validate_card_data(card_data)
            
            # Check if card already exists
            existing_card = SavedCreditCard.objects.filter(
                user=user,
                card_last_four=card_data['card_number'][-4:],
                card_expiry_month=int(card_data['expiry_date'].split('/')[0]),
                card_expiry_year=int(card_data['expiry_date'].split('/')[1])
            ).first()
            
            if existing_card:
                return {
                    'success': False,
                    'error': 'Card already saved'
                }
            
            # Create saved card record
            saved_card = SavedCreditCard.objects.create(
                user=user,
                card_type=self._detect_card_type(card_data['card_number']),
                card_last_four=card_data['card_number'][-4:],
                card_expiry_month=int(card_data['expiry_date'].split('/')[0]),
                card_expiry_year=int(card_data['expiry_date'].split('/')[1]),
                cardholder_name=card_data['cardholder_name'],
                provider_token=f"token_{uuid.uuid4().hex}",
                provider=provider,
                billing_address=card_data.get('billing_address', {}),
                nickname=card_data.get('nickname', f'{self._detect_card_type(card_data["card_number"]).title()} *{card_data["card_number"][-4:]}'),
                expires_at=datetime(card_data['expiry_date'].split('/')[1], card_data['expiry_date'].split('/')[0], 1)
            )
            
            return {
                'success': True,
                'card_id': saved_card.id,
                'masked_card': saved_card.masked_card_number,
                'card_type': saved_card.card_type,
                'expires_at': saved_card.expires_at
            }
            
        except Exception as e:
            logger.error(f"Save card failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def initiate_payment_with_saved_card(self, payment, saved_card_id):
        """Initiate payment using saved card"""
        try:
            saved_card = SavedCreditCard.objects.get(id=saved_card_id)
            
            # Check if card is expired
            if saved_card.is_expired:
                return {
                    'success': False,
                    'error': 'Card has expired'
                }
            
            # Create payment data from saved card
            card_data = {
                'card_number': f"****-****-****-{saved_card.card_last_four}",
                'cardholder_name': saved_card.cardholder_name,
                'expiry_date': f"{saved_card.card_expiry_month:02d}/{saved_card.card_expiry_year}",
                'billing_address': saved_card.billing_address,
                'use_saved_token': True,
                'provider_token': saved_card.provider_token,
            }
            
            # Process payment
            result = self.initiate_payment(payment, saved_card.provider.code, card_data)
            
            # Update usage count
            if result['success']:
                saved_card.usage_count += 1
                saved_card.last_used_at = timezone.now()
                saved_card.save()
            
            return result
            
        except SavedCreditCard.DoesNotExist:
            return {
                'success': False,
                'error': 'Saved card not found'
            }
        except Exception as e:
            logger.error(f"Saved card payment failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_payment_status(self, transaction_id):
        """Check status of credit card payment"""
        try:
            credit_payment = CreditCardPayment.objects.get(transaction_id=transaction_id)
            provider = credit_payment.provider
            
            # Check with provider
            status_result = self._check_status_with_provider(provider, credit_payment)
            
            # Update status if changed
            if status_result['status'] != credit_payment.status:
                old_status = credit_payment.status
                credit_payment.status = status_result['status']
                
                if status_result['status'] == 'completed':
                    credit_payment.completed_at = timezone.now()
                elif status_result['status'] == 'authorized':
                    credit_payment.authorized_at = timezone.now()
                elif status_result['status'] == 'captured':
                    credit_payment.captured_at = timezone.now()
                
                credit_payment.save()
                
                # Update main payment status
                if status_result['status'] == 'completed':
                    payment = credit_payment.payment
                    payment.payment_status = 'fully_paid'
                    payment.save()
                
                # Log status change
                self._log_transaction(
                    provider=provider,
                    transaction=credit_payment,
                    action_type='payment_completed',
                    response_data=status_result['response'],
                    success=True
                )
            
            return {
                'success': True,
                'status': credit_payment.status,
                'amount': credit_payment.amount,
                'currency': credit_payment.currency,
                'provider': provider.display_name,
                'card_type': credit_payment.card_type,
                'card_last_four': credit_payment.card_last_four,
                'authorized_at': credit_payment.authorized_at.isoformat() if credit_payment.authorized_at else None,
                'completed_at': credit_payment.completed_at.isoformat() if credit_payment.completed_at else None
            }
            
        except CreditCardPayment.DoesNotExist:
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
    
    def _validate_card_data(self, card_data):
        """Validate credit card data"""
        import re
        
        # Validate card number
        card_number = card_data.get('card_number', '').replace('-', '').replace(' ', '')
        if not re.match(r'^\d{13,19}$', card_number):
            raise ValueError('Invalid card number')
        
        # Validate expiry date
        expiry_date = card_data.get('expiry_date', '')
        if not re.match(r'^(0[1-9]|1[0-2])/\d{2,4}$', expiry_date):
            raise ValueError('Invalid expiry date format. Use MM/YY or MM/YYYY')
        
        # Check if card is expired
        month, year = expiry_date.split('/')
        year = int(year)
        if year < 100:
            year += 2000
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if year < current_year or (year == current_year and int(month) < current_month):
            raise ValueError('Card has expired')
        
        # Validate cardholder name
        if not card_data.get('cardholder_name', '').strip():
            raise ValueError('Cardholder name is required')
    
    def _detect_card_type(self, card_number):
        """Detect card type from card number"""
        card_number = card_number.replace('-', '').replace(' ', '')
        
        if card_number.startswith('4'):
            return 'visa'
        elif card_number.startswith('5') or card_number.startswith('2'):
            return 'mastercard'
        elif card_number.startswith('34') or card_number.startswith('37'):
            return 'american_express'
        elif card_number.startswith('65') or card_number.startswith('6011'):
            return 'discover'
        elif card_number.startswith('62'):
            return 'unionpay'
        else:
            return 'other'
    
    def _perform_fraud_check(self, credit_payment, card_data):
        """Perform basic fraud detection"""
        score = 0
        risk_factors = []
        
        # Check amount
        if credit_payment.amount > 1000000:  # High amount
            score += 20
            risk_factors.append('high_amount')
        
        # Check IP address (basic)
        ip_address = card_data.get('ip_address', '')
        if ip_address.startswith('127.') or ip_address.startswith('192.168.'):
            score += 10
            risk_factors.append('private_ip')
        
        # Check card expiry (soon to expire)
        expiry_month = credit_payment.card_expiry_month
        expiry_year = credit_payment.card_expiry_year
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        months_until_expiry = (expiry_year - current_year) * 12 + (expiry_month - current_month)
        if months_until_expiry < 3:
            score += 15
            risk_factors.append('expiring_soon')
        
        # Determine risk level
        if score < 30:
            risk_level = 'low'
        elif score < 60:
            risk_level = 'medium'
        elif score < 80:
            risk_level = 'high'
        else:
            risk_level = 'very_high'
        
        return {
            'score': score,
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }
    
    def _process_with_provider(self, provider, credit_payment, card_data):
        """Process payment with specific provider"""
        # This is a mock implementation - in production, integrate with actual provider APIs
        
        if provider.code == 'STRIPE':
            return self._process_stripe_payment(credit_payment, card_data)
        elif provider.code == 'FLUTTERWAVE':
            return self._process_flutterwave_payment(credit_payment, card_data)
        elif provider.code == 'PAYSTACK':
            return self._process_paystack_payment(credit_payment, card_data)
        elif provider.code == 'DPO_UGANDA':
            return self._process_dpo_payment(credit_payment, card_data)
        else:
            # Default processing for other providers
            return self._process_generic_payment(credit_payment, card_data)
    
    def _process_stripe_payment(self, credit_payment, card_data):
        """Process Stripe payment"""
        try:
            # Mock Stripe API call
            # In production, integrate with actual Stripe API
            
            return {
                'success': True,
                'status': 'completed',
                'authorization_code': f"STRIPE_{uuid.uuid4().hex[:16].upper()}",
                'response': {
                    'transaction_id': credit_payment.transaction_id,
                    'status': 'succeeded',
                    'payment_intent_id': f"pi_{uuid.uuid4().hex}"
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {'error': 'Stripe API error'}
            }
    
    def _process_flutterwave_payment(self, credit_payment, card_data):
        """Process Flutterwave payment"""
        try:
            # Mock Flutterwave API call
            # In production, integrate with actual Flutterwave API
            
            return {
                'success': True,
                'status': 'completed',
                'authorization_code': f"FW_{uuid.uuid4().hex[:16].upper()}",
                'response': {
                    'transaction_id': credit_payment.transaction_id,
                    'status': 'successful',
                    'flw_ref': f"FLW_{uuid.uuid4().hex}"
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {'error': 'Flutterwave API error'}
            }
    
    def _process_paystack_payment(self, credit_payment, card_data):
        """Process Paystack payment"""
        try:
            # Mock Paystack API call
            # In production, integrate with actual Paystack API
            
            return {
                'success': True,
                'status': 'completed',
                'authorization_code': f"PS_{uuid.uuid4().hex[:16].upper()}",
                'response': {
                    'transaction_id': credit_payment.transaction_id,
                    'status': 'success',
                    'reference': f"paystack_{uuid.uuid4().hex}"
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {'error': 'Paystack API error'}
            }
    
    def _process_dpo_payment(self, credit_payment, card_data):
        """Process DPO Uganda payment"""
        try:
            # Mock DPO API call
            # In production, integrate with actual DPO API
            
            return {
                'success': True,
                'status': 'completed',
                'authorization_code': f"DPO_{uuid.uuid4().hex[:16].upper()}",
                'response': {
                    'transaction_id': credit_payment.transaction_id,
                    'status': 'completed',
                    'dpo_ref': f"DPO_{uuid.uuid4().hex}"
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {'error': 'DPO API error'}
            }
    
    def _process_generic_payment(self, credit_payment, card_data):
        """Generic payment processing for other providers"""
        try:
            return {
                'success': True,
                'status': 'completed',
                'authorization_code': f"GENERIC_{uuid.uuid4().hex[:16].upper()}",
                'response': {
                    'transaction_id': credit_payment.transaction_id,
                    'status': 'completed'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {'error': 'Provider API error'}
            }
    
    def _check_status_with_provider(self, provider, credit_payment):
        """Check payment status with provider"""
        try:
            # Mock status check - in production, integrate with actual provider APIs
            import random
            
            # Simulate different status outcomes
            if random.random() > 0.8:  # 20% chance of completion
                return {
                    'status': 'completed',
                    'response': {
                        'transaction_id': credit_payment.transaction_id,
                        'status': 'completed',
                        'completed_at': timezone.now().isoformat()
                    }
                }
            elif random.random() > 0.5:  # 30% chance of authorization
                return {
                    'status': 'authorized',
                    'response': {
                        'transaction_id': credit_payment.transaction_id,
                        'status': 'authorized',
                        'authorized_at': timezone.now().isoformat()
                    }
                }
            else:  # 50% chance of still processing
                return {
                    'status': 'processing',
                    'response': {
                        'transaction_id': credit_payment.transaction_id,
                        'status': 'processing',
                        'message': 'Payment is being processed'
                    }
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'response': {'error': str(e)}
            }
    
    def _log_transaction(self, provider, transaction=None, action_type=None, request_data=None, response_data=None, success=False, error_code=None, error_message=None, ip_address=None, user_agent=None):
        """Log credit card transactions"""
        CreditCardTransactionLog.objects.create(
            provider=provider,
            transaction=transaction,
            action_type=action_type,
            request_data=request_data or {},
            response_data=response_data or {},
            processing_time_ms=None,  # Would be calculated in real implementation
            success=success,
            error_code=error_code,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent
        )

# Create service instance
credit_card_service = CreditCardService()
