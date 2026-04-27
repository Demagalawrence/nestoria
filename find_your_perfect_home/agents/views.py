from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    AgentProfile, AgentRequest, AgentAvailability, 
    AgentReview, AgentCommission
)
from .serializers import (
    AgentProfileSerializer, AgentRequestSerializer, 
    AgentAvailabilitySerializer, AgentReviewSerializer,
    AgentCommissionSerializer
)

User = get_user_model()

class AgentProfileListView(generics.ListAPIView):
    """List available agents"""
    serializer_class = AgentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AgentProfile.objects.select_related('user').filter(
            is_verified=True, 
            is_available=True,
            user__role='agent'
        )
        
        # Filter by service area
        area = self.request.query_params.get('area')
        if area:
            queryset = queryset.filter(service_areas__contains=[area])
        
        # Filter by specialization
        specialization = self.request.query_params.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        
        # Filter by language
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(languages__contains=[language])
        
        return queryset.order_by('-average_rating')

class AgentRequestListCreateView(generics.ListCreateAPIView):
    """Create and list agent requests"""
    serializer_class = AgentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'agent':
            return AgentRequest.objects.filter(assigned_agent=user)
        else:
            return AgentRequest.objects.filter(customer=user)
    
    def perform_create(self, serializer):
        """Auto-assign best available agent"""
        customer = self.request.user
        request_data = serializer.validated_data
        
        # Find best agent based on criteria
        best_agent = self.find_best_agent(request_data)
        
        serializer.save(customer=customer, assigned_agent=best_agent)
    
    def find_best_agent(self, request_data):
        """Find the best available agent for the request"""
        property_obj = request_data.get('property')
        request_type = request_data.get('request_type')
        
        # Base queryset
        agents = AgentProfile.objects.filter(
            is_verified=True,
            is_available=True,
            user__role='agent'
        ).select_related('user')
        
        # Filter by specialization
        if property_obj:
            property_type = property_obj.property_type
            if property_type in ['hostel', 'apartment']:
                agents = agents.filter(
                    Q(specialization='student_housing') | 
                    Q(specialization='residential') | 
                    Q(specialization='all_types')
                )
        
        # Filter by service area
        if property_obj and property_obj.district:
            agents = agents.filter(service_areas__contains=[property_obj.district])
        
        # Filter by availability (working hours)
        current_time = timezone.now()
        current_day = current_time.strftime('%A').lower()
        available_agents = []
        
        for agent in agents:
            if agent.is_online:
                available_agents.append(agent)
        
        # If no agents are currently online, get all verified agents
        if not available_agents:
            available_agents = list(agents)
        
        # Sort by rating and response rate
        available_agents.sort(
            key=lambda x: (x.average_rating, x.response_rate), 
            reverse=True
        )
        
        return available_agents[0].user if available_agents else None

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def agent_statistics(request):
    """Get agent performance statistics"""
    user = request.user
    
    if user.role != 'agent':
        return Response(
            {'error': 'Only agents can view statistics'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        agent_profile = user.agent_profile
        
        # Calculate statistics
        total_requests = AgentRequest.objects.filter(assigned_agent=user).count()
        completed_requests = AgentRequest.objects.filter(
            assigned_agent=user, 
            status='completed'
        ).count()
        
        pending_requests = AgentRequest.objects.filter(
            assigned_agent=user, 
            status='assigned'
        ).count()
        
        # Average response time (placeholder - would need actual tracking)
        avg_response_time = "1 hour"  # This would be calculated from actual data
        
        # Recent reviews
        recent_reviews = AgentReview.objects.filter(
            agent=user
        ).order_by('-created_at')[:5]
        
        data = {
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'pending_requests': pending_requests,
            'completion_rate': (completed_requests / total_requests * 100) if total_requests > 0 else 0,
            'average_rating': agent_profile.average_rating,
            'total_clients': agent_profile.total_clients,
            'successful_deals': agent_profile.successful_deals,
            'response_rate': agent_profile.response_rate,
            'recent_reviews': AgentReviewSerializer(recent_reviews, many=True).data
        }
        
        return Response(data)
        
    except AgentProfile.DoesNotExist:
        return Response(
            {'error': 'Agent profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_agent_manually(request, request_id):
    """Manually assign an agent to a request"""
    if request.user.role not in ['admin']:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        agent_request = AgentRequest.objects.get(id=request_id)
        agent_id = request.data.get('agent_id')
        
        if not agent_id:
            return Response(
                {'error': 'Agent ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        agent = User.objects.get(id=agent_id, role='agent')
        
        agent_request.assigned_agent = agent
        agent_request.status = 'assigned'
        agent_request.assigned_at = timezone.now()
        agent_request.save()
        
        return Response(AgentRequestSerializer(agent_request).data)
        
    except AgentRequest.DoesNotExist:
        return Response(
            {'error': 'Request not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'Agent not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
