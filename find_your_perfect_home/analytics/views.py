from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import PropertyAnalytics, PlatformAnalytics, UserActivity
from properties.models import Property
from bookings.models import Booking
from payments.models import Payment
from .serializers import PropertyAnalyticsSerializer, PlatformAnalyticsSerializer, UserActivitySerializer

class PropertyAnalyticsView(generics.RetrieveAPIView):
    serializer_class = PropertyAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        property_id = self.kwargs['pk']
        property_obj = Property.objects.get(id=property_id)
        
        # Check permissions
        user = self.request.user
        if user.role not in ['admin'] and property_obj.owner != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to view these analytics")
        
        analytics, created = PropertyAnalytics.objects.get_or_create(
            property=property_obj
        )
        analytics.update_analytics()
        return analytics

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def platform_analytics(request):
    user = request.user
    if user.role != 'admin':
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get date range from query params
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # User statistics
    from accounts.models import User
    total_users = User.objects.count()
    new_users = User.objects.filter(date_joined__gte=start_date).count()
    
    # Property statistics
    total_properties = Property.objects.count()
    new_properties = Property.objects.filter(created_at__gte=start_date).count()
    approved_properties = Property.objects.filter(is_approved=True).count()
    
    # Booking statistics
    total_bookings = Booking.objects.count()
    new_bookings = Booking.objects.filter(created_at__gte=start_date).count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    completed_bookings = Booking.objects.filter(status='completed').count()
    
    # Revenue statistics
    completed_payments = Payment.objects.filter(payment_status='completed')
    total_revenue = completed_payments.aggregate(total=Sum('amount'))['total'] or 0
    recent_revenue = completed_payments.filter(payment_date__gte=start_date).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_commission = completed_payments.aggregate(total=Sum('commission_amount'))['total'] or 0
    
    # Daily statistics for the period
    daily_stats = []
    for i in range(days):
        date = (timezone.now().date() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_bookings = Booking.objects.filter(created_at__date=date).count()
        day_revenue = completed_payments.filter(payment_date__date=date).aggregate(
            total=Sum('amount')
        )['total'] or 0
        daily_stats.append({
            'date': date,
            'bookings': day_bookings,
            'revenue': float(day_revenue)
        })
    
    data = {
        'user_stats': {
            'total_users': total_users,
            'new_users': new_users,
        },
        'property_stats': {
            'total_properties': total_properties,
            'new_properties': new_properties,
            'approved_properties': approved_properties,
        },
        'booking_stats': {
            'total_bookings': total_bookings,
            'new_bookings': new_bookings,
            'confirmed_bookings': confirmed_bookings,
            'completed_bookings': completed_bookings,
        },
        'revenue_stats': {
            'total_revenue': float(total_revenue),
            'recent_revenue': float(recent_revenue),
            'total_commission': float(total_commission),
        },
        'daily_stats': daily_stats,
    }
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def property_performance_report(request):
    user = request.user
    
    # Filter properties based on user role
    if user.role == 'admin':
        properties = Property.objects.all()
    elif user.role == 'owner':
        properties = Property.objects.filter(owner=user)
    else:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    performance_data = []
    
    for property_obj in properties:
        analytics, created = PropertyAnalytics.objects.get_or_create(
            property=property_obj
        )
        analytics.update_analytics()
        
        performance_data.append({
            'property_id': property_obj.id,
            'property_name': property_obj.name,
            'total_bookings': analytics.total_bookings,
            'occupancy_rate': float(analytics.occupancy_rate),
            'total_revenue': float(analytics.total_revenue),
            'average_rating': float(analytics.average_rating) if analytics.average_rating else 0,
            'total_reviews': analytics.total_reviews,
        })
    
    # Sort by revenue
    performance_data.sort(key=lambda x: x['total_revenue'], reverse=True)
    
    return Response({
        'properties': performance_data,
        'summary': {
            'total_properties': len(performance_data),
            'total_revenue': sum(p['total_revenue'] for p in performance_data),
            'average_occupancy': sum(p['occupancy_rate'] for p in performance_data) / len(performance_data) if performance_data else 0,
        }
    })

class UserActivityListView(generics.ListAPIView):
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_user_activity(request):
    """Track user activity for analytics"""
    activity_type = request.data.get('activity_type')
    description = request.data.get('description', '')
    
    # Get related objects if provided
    property_id = request.data.get('property_id')
    booking_id = request.data.get('booking_id')
    
    activity = UserActivity.objects.create(
        user=request.user,
        activity_type=activity_type,
        description=description,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        property_id=property_id,
        booking_id=booking_id
    )
    
    return Response({'message': 'Activity tracked', 'activity_id': activity.id})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for the current user"""
    user = request.user
    
    if user.role == 'admin':
        # Admin dashboard stats
        data = {
            'total_users': User.objects.count(),
            'total_properties': Property.objects.count(),
            'total_bookings': Booking.objects.count(),
            'pending_bookings': Booking.objects.filter(status='pending').count(),
            'total_revenue': float(Payment.objects.filter(payment_status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0),
        }
    elif user.role == 'owner':
        # Owner dashboard stats
        user_properties = Property.objects.filter(owner=user)
        property_ids = user_properties.values_list('id', flat=True)
        
        data = {
            'total_properties': user_properties.count(),
            'total_bookings': Booking.objects.filter(rental_property__in=property_ids).count(),
            'active_bookings': Booking.objects.filter(
                rental_property__in=property_ids, 
                status='confirmed'
            ).count(),
            'total_revenue': float(Payment.objects.filter(
                booking__rental_property__in=property_ids,
                payment_status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0),
        }
    else:
        # Tenant dashboard stats
        data = {
            'total_bookings': Booking.objects.filter(user=user).count(),
            'active_bookings': Booking.objects.filter(user=user, status='confirmed').count(),
            'completed_bookings': Booking.objects.filter(user=user, status='completed').count(),
            'total_spent': float(Payment.objects.filter(
                booking__user=user,
                payment_status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0),
        }
    
    return Response(data)
