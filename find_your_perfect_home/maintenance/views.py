from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    MaintenanceCategory, MaintenanceRequest, MaintenanceImage, 
    MaintenanceComment, MaintenanceHistory
)
from .serializers import (
    MaintenanceCategorySerializer, MaintenanceRequestSerializer,
    MaintenanceRequestCreateSerializer, MaintenanceRequestUpdateSerializer,
    MaintenanceImageSerializer, MaintenanceCommentSerializer,
    MaintenanceCommentCreateSerializer, MaintenanceHistorySerializer,
    MaintenanceStatsSerializer
)
from properties.models import Property, Room

User = get_user_model()

class MaintenanceCategoryListView(generics.ListAPIView):
    """List all maintenance categories"""
    queryset = MaintenanceCategory.objects.filter(is_active=True)
    serializer_class = MaintenanceCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class MaintenanceRequestListCreateView(generics.ListCreateAPIView):
    """List and create maintenance requests"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter requests based on user role"""
        user = self.request.user
        queryset = MaintenanceRequest.objects.select_related(
            'property', 'room', 'tenant', 'assigned_to', 'category'
        ).prefetch_related('images', 'comments', 'history')
        
        # Filter based on user role
        if user.role == 'tenant':
            # Tenants can only see their own requests
            queryset = queryset.filter(tenant=user)
        elif user.role == 'owner':
            # Property owners can see requests for their properties
            queryset = queryset.filter(property__owner=user)
        elif user.role == 'admin':
            # Admins can see all requests
            pass
        else:
            # Staff/landlords can see assigned requests
            queryset = queryset.filter(Q(assigned_to=user) | Q(property__owner=user))
        
        # Apply filters from query parameters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        property_filter = self.request.query_params.get('property')
        if property_filter:
            queryset = queryset.filter(property_id=property_filter)
        
        category_filter = self.request.query_params.get('category')
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(reference_number__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for list vs create"""
        if self.request.method == 'POST':
            return MaintenanceRequestCreateSerializer
        return MaintenanceRequestSerializer
    
    def perform_create(self, serializer):
        """Set tenant from request user"""
        serializer.save(tenant=self.request.user)

class MaintenanceRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a maintenance request"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get requests user has access to"""
        user = self.request.user
        queryset = MaintenanceRequest.objects.select_related(
            'property', 'room', 'tenant', 'assigned_to', 'category'
        ).prefetch_related('images', 'comments', 'history')
        
        if user.role == 'tenant':
            queryset = queryset.filter(tenant=user)
        elif user.role == 'owner':
            queryset = queryset.filter(property__owner=user)
        elif user.role != 'admin':
            queryset = queryset.filter(Q(assigned_to=user) | Q(property__owner=user))
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers for different methods"""
        if self.request.method in ['PUT', 'PATCH']:
            return MaintenanceRequestUpdateSerializer
        return MaintenanceRequestSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def maintenance_stats(request):
    """Get maintenance statistics"""
    user = request.user
    
    # Base queryset based on user role
    if user.role == 'tenant':
        requests = MaintenanceRequest.objects.filter(tenant=user)
    elif user.role == 'owner':
        requests = MaintenanceRequest.objects.filter(property__owner=user)
    elif user.role == 'admin':
        requests = MaintenanceRequest.objects.all()
    else:
        requests = MaintenanceRequest.objects.filter(
            Q(assigned_to=user) | Q(property__owner=user)
        )
    
    # Calculate statistics
    total_requests = requests.count()
    pending_requests = requests.filter(status='pending').count()
    in_progress_requests = requests.filter(status='in_progress').count()
    completed_requests = requests.filter(status='completed').count()
    urgent_requests = requests.filter(priority='urgent').count()
    
    # Calculate overdue requests
    from datetime import timedelta
    now = timezone.now()
    overdue_requests = 0
    
    for request in requests.filter(status__in=['pending', 'in_progress']):
        days_open = (now.date() - request.requested_date.date()).days
        thresholds = {'urgent': 1, 'high': 3, 'medium': 7, 'low': 14}
        if days_open > thresholds.get(request.priority, 7):
            overdue_requests += 1
    
    # Calculate average completion time
    completed_with_time = requests.filter(
        status='completed', 
        completed_date__isnull=False
    )
    avg_completion_time = completed_with_time.aggregate(
        avg_time=Avg(F('completed_date') - F('requested_date'))
    )['avg_time']
    
    if avg_completion_time:
        avg_completion_time = avg_completion_time.days
    else:
        avg_completion_time = 0
    
    completion_rate = (completed_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Requests by category
    requests_by_category = dict(
        requests.values('category__name')
        .annotate(count=Count('id'))
        .values_list('category__name', 'count')
    )
    
    # Requests by priority
    requests_by_priority = dict(
        requests.values('priority')
        .annotate(count=Count('id'))
        .values_list('priority', 'count')
    )
    
    # Recent requests
    recent_requests = requests.order_by('-created_at')[:5]
    
    data = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
        'urgent_requests': urgent_requests,
        'overdue_requests': overdue_requests,
        'avg_completion_time': avg_completion_time,
        'completion_rate': round(completion_rate, 2),
        'requests_by_category': requests_by_category,
        'requests_by_priority': requests_by_priority,
        'recent_requests': MaintenanceRequestSerializer(
            recent_requests, many=True, context={'request': request}
        ).data
    }
    
    serializer = MaintenanceStatsSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_maintenance_requests(request):
    """Get maintenance requests for the current user"""
    user = request.user
    
    if user.role == 'tenant':
        requests = MaintenanceRequest.objects.filter(tenant=user)
    else:
        # For staff/owners, get assigned requests
        requests = MaintenanceRequest.objects.filter(assigned_to=user)
    
    # Apply filters
    status_filter = request.query_params.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    serializer = MaintenanceRequestSerializer(
        requests.order_by('-created_at'), 
        many=True, 
        context={'request': request}
    )
    
    return Response(serializer.data)
