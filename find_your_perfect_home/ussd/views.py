"""
USSD API Views for Uganda Rental Platform
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.db import models
from datetime import timedelta
from .services import ussd_service
from .models import USSDSession, USSDRequestLog
import json
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class USSDWebhookView(generics.GenericAPIView):
    """USSD webhook endpoint for handling requests from USSD gateway"""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Handle USSD webhook request"""
        try:
            # Parse webhook data
            data = json.loads(request.body)
            
            # Extract USSD parameters
            phone_number = data.get('phoneNumber', '')
            request_text = data.get('text', '')
            session_id = data.get('sessionId', '')
            
            # Validate required fields
            if not phone_number:
                return Response({
                    'status': 'error',
                    'message': 'Phone number is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process USSD request
            result = ussd_service.process_ussd_request(phone_number, request_text, session_id)
            
            if result['success']:
                # Format USSD response
                response_data = {
                    'text': result['response_text'],
                    'continueSession': result['continue_session'],
                    'sessionId': result['session_id'],
                    'screen': result['screen']
                }
                
                return JsonResponse(response_data)
            else:
                # Error response
                return JsonResponse({
                    'text': result.get('response_text', 'Service temporarily unavailable'),
                    'continueSession': False,
                    'sessionId': session_id or '',
                    'screen': 'error'
                })
                
        except json.JSONDecodeError:
            return Response({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"USSD webhook error: {str(e)}")
            return JsonResponse({
                'text': 'Service temporarily unavailable. Please try again later.',
                'continueSession': False,
                'sessionId': '',
                'screen': 'error'
            })

@api_view(['GET'])
def ussd_status(request):
    """Get USSD system status"""
    try:
        # Get system statistics
        active_sessions = USSDSession.objects.filter(status='active').count()
        total_requests_today = USSDRequestLog.objects.filter(
            request_time__date=timezone.now().date()
        ).count()
        
        # Get recent activity
        recent_requests = USSDRequestLog.objects.filter(
            request_time__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        return Response({
            'status': 'active',
            'active_sessions': active_sessions,
            'requests_today': total_requests_today,
            'requests_last_hour': recent_requests,
            'service_uptime': '99.9%',
            'last_updated': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"USSD status error: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def ussd_test(request):
    """Test USSD endpoint for development"""
    try:
        data = request.data
        phone_number = data.get('phone_number', '+256772123456')
        request_text = data.get('text', '')
        session_id = data.get('session_id', '')
        
        # Process test request
        result = ussd_service.process_ussd_request(phone_number, request_text, session_id)
        
        return Response({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"USSD test error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def ussd_analytics(request):
    """Get USSD analytics data"""
    try:
        # Session analytics
        total_sessions = USSDSession.objects.count()
        active_sessions = USSDSession.objects.filter(status='active').count()
        completed_sessions = USSDSession.objects.filter(status='completed').count()
        
        # Request analytics
        total_requests = USSDRequestLog.objects.count()
        successful_requests = USSDRequestLog.objects.filter(success=True).count()
        
        # Popular screens
        popular_screens = USSDRequestLog.objects.values('response_screen').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'sessions': {
                'total': total_sessions,
                'active': active_sessions,
                'completed': completed_sessions,
                'completion_rate': f"{(completed_sessions / total_sessions * 100):.1f}%" if total_sessions > 0 else "0%"
            },
            'requests': {
                'total': total_requests,
                'successful': successful_requests,
                'success_rate': f"{(successful_requests / total_requests * 100):.1f}%" if total_requests > 0 else "0%"
            },
            'popular_screens': list(popular_screens),
            'last_updated': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"USSD analytics error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def usd_send_sms(request):
    """Send SMS notification (for USSD users)"""
    try:
        data = request.data
        phone_number = data.get('phone_number', '')
        message = data.get('message', '')
        
        if not phone_number or not message:
            return Response({
                'success': False,
                'error': 'Phone number and message are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Here you would integrate with an SMS service like Twilio, Africa's Talking, etc.
        # For now, we'll just log it
        logger.info(f"SMS to {phone_number}: {message}")
        
        return Response({
            'success': True,
            'message': 'SMS sent successfully (mock implementation)'
        })
        
    except Exception as e:
        logger.error(f"SMS send error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# USSD Gateway Integration Endpoints

@api_view(['POST'])
def ussd_gateway_mtn(request):
    """Handle MTN USSD gateway requests"""
    return handle_ussd_gateway_request(request, 'MTN')

@api_view(['POST'])
def ussd_gateway_airtel(request):
    """Handle Airtel USSD gateway requests"""
    return handle_ussd_gateway_request(request, 'Airtel')

@api_view(['POST'])
def ussd_gateway_generic(request):
    """Handle generic USSD gateway requests"""
    return handle_ussd_gateway_request(request, 'Generic')

def handle_ussd_gateway_request(request, gateway_name):
    """Generic USSD gateway handler"""
    try:
        # Different gateways have different data formats
        if gateway_name == 'MTN':
            # MTN USSD format
            phone_number = request.data.get('MSISDN', '')
            request_text = request.data.get('USERDATA', '')
            session_id = request.data.get('SESSIONID', '')
            
        elif gateway_name == 'Airtel':
            # Airtel USSD format
            phone_number = request.data.get('msisdn', '')
            request_text = request.data.get('input', '')
            session_id = request.data.get('sessionId', '')
            
        else:
            # Generic format
            phone_number = request.data.get('phone_number', '')
            request_text = request.data.get('text', '')
            session_id = request.data.get('session_id', '')
        
        # Process the USSD request
        result = ussd_service.process_ussd_request(phone_number, request_text, session_id)
        
        if result['success']:
            # Format response for the specific gateway
            if gateway_name == 'MTN':
                response_data = {
                    'RESPONSE': result['response_text'],
                    'CONTINUESESSION': '1' if result['continue_session'] else '0'
                }
            elif gateway_name == 'Airtel':
                response_data = {
                    'response': result['response_text'],
                    'continueSession': result['continue_session']
                }
            else:
                response_data = {
                    'text': result['response_text'],
                    'continueSession': result['continue_session']
                }
            
            return JsonResponse(response_data)
        else:
            # Error response
            if gateway_name == 'MTN':
                response_data = {
                    'RESPONSE': result.get('response_text', 'Service unavailable'),
                    'CONTINUESESSION': '0'
                }
            elif gateway_name == 'Airtel':
                response_data = {
                    'response': result.get('response_text', 'Service unavailable'),
                    'continueSession': False
                }
            else:
                response_data = {
                    'text': result.get('response_text', 'Service unavailable'),
                    'continueSession': False
                }
            
            return JsonResponse(response_data)
            
    except Exception as e:
        logger.error(f"USSD gateway error ({gateway_name}): {str(e)}")
        
        # Return error response
        if gateway_name == 'MTN':
            return JsonResponse({
                'RESPONSE': 'Service temporarily unavailable',
                'CONTINUESESSION': '0'
            })
        elif gateway_name == 'Airtel':
            return JsonResponse({
                'response': 'Service temporarily unavailable',
                'continueSession': False
            })
        else:
            return JsonResponse({
                'text': 'Service temporarily unavailable',
                'continueSession': False
            })

# Development and testing endpoints

@api_view(['GET'])
def usd_debug_sessions(request):
    """Debug endpoint to view active sessions"""
    if not settings.DEBUG:
        return Response({'error': 'Debug endpoint not available in production'}, status=403)
    
    sessions = USSDSession.objects.filter(status='active').order_by('-started_at')
    
    session_data = []
    for session in sessions:
        session_data.append({
            'session_id': session.session_id,
            'phone_number': session.phone_number,
            'current_screen': session.current_screen,
            'started_at': session.started_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'expires_at': session.expires_at.isoformat(),
            'is_authenticated': session.is_authenticated,
            'user': session.user.username if session.user else None
        })
    
    return Response({
        'active_sessions': session_data,
        'total_count': len(session_data)
    })

@api_view(['GET'])
def usd_debug_logs(request):
    """Debug endpoint to view recent logs"""
    if not settings.DEBUG:
        return Response({'error': 'Debug endpoint not available in production'}, status=403)
    
    limit = int(request.GET.get('limit', 50))
    logs = USSDRequestLog.objects.order_by('-request_time')[:limit]
    
    log_data = []
    for log in logs:
        log_data.append({
            'phone_number': log.phone_number,
            'request_text': log.request_text,
            'response_text': log.response_text[:100],  # Truncate
            'response_screen': log.response_screen,
            'request_time': log.request_time.isoformat(),
            'processing_time_ms': log.processing_time_ms,
            'success': log.success,
            'error_message': log.error_message
        })
    
    return Response({
        'recent_logs': log_data,
        'total_count': len(log_data)
    })

@api_view(['POST'])
def usd_clear_expired_sessions(request):
    """Clear expired sessions (maintenance endpoint)"""
    if not settings.DEBUG:
        return Response({'error': 'Debug endpoint not available in production'}, status=403)
    
    try:
        expired_count = ussd_service.cleanup_expired_sessions()
        
        return Response({
            'success': True,
            'expired_sessions_cleared': expired_count
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
