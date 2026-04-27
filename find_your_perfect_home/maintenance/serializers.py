from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    MaintenanceCategory, MaintenanceRequest, MaintenanceImage, 
    MaintenanceComment, MaintenanceHistory
)
from properties.serializers import PropertySerializer, RoomSerializer

User = get_user_model()

class MaintenanceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceCategory
        fields = '__all__'

class MaintenanceImageSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = MaintenanceImage
        fields = ['id', 'image', 'caption', 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']

class MaintenanceCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_role = serializers.CharField(source='author.role', read_only=True)
    
    class Meta:
        model = MaintenanceComment
        fields = [
            'id', 'author', 'author_name', 'author_role', 'comment', 
            'is_internal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

class MaintenanceHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = MaintenanceHistory
        fields = '__all__'
        read_only_fields = ['changed_by', 'timestamp']

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for maintenance requests"""
    property_details = PropertySerializer(source='property', read_only=True)
    room_details = RoomSerializer(source='room', read_only=True)
    tenant_name = serializers.CharField(source='tenant.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    # Nested serializers for related data
    images = MaintenanceImageSerializer(many=True, read_only=True)
    comments = MaintenanceCommentSerializer(many=True, read_only=True)
    history = MaintenanceHistorySerializer(many=True, read_only=True)
    
    # Additional computed fields
    days_open = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = MaintenanceRequest
        fields = '__all__'
        read_only_fields = [
            'reference_number', 'tenant', 'created_at', 'updated_at', 
            'requested_date', 'completed_date'
        ]
    
    def get_days_open(self, obj):
        """Calculate how many days the request has been open"""
        from django.utils import timezone
        if obj.status == 'completed' and obj.completed_date:
            return (obj.completed_date.date() - obj.requested_date.date()).days
        return (timezone.now().date() - obj.requested_date.date()).days
    
    def get_is_overdue(self, obj):
        """Check if request is overdue based on priority"""
        from django.utils import timezone
        
        if obj.status == 'completed':
            return False
            
        days_open = self.get_days_open(obj)
        overdue_thresholds = {
            'urgent': 1,    # 1 day
            'high': 3,      # 3 days
            'medium': 7,    # 1 week
            'low': 14,      # 2 weeks
        }
        
        return days_open > overdue_thresholds.get(obj.priority, 7)

class MaintenanceRequestCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating maintenance requests"""
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'title', 'description', 'category', 'priority', 'property', 
            'room', 'preferred_date', 'estimated_cost', 'access_instructions',
            'permission_to_enter', 'tenant_present'
        ]
    
    def create(self, validated_data):
        """Create maintenance request and trigger notification"""
        request = self.context['request']
        validated_data['tenant'] = request.user
        
        maintenance_request = super().create(validated_data)
        
        # Create notification for new request
        from notifications.models import Notification
        
        # Notify property owner
        if hasattr(maintenance_request.property, 'owner'):
            Notification.objects.create(
                user=maintenance_request.property.owner,
                notification_type='maintenance_request_created',
                title=f'New Maintenance Request - {maintenance_request.reference_number}',
                message=f'New maintenance request "{maintenance_request.title}" at {maintenance_request.property.name}.',
                maintenance_request=maintenance_request,
                property=maintenance_request.property
            )
        
        # Notify admin users (you may want to implement this logic)
        # This could be based on user roles or permissions
        
        # Create history entry
        MaintenanceHistory.objects.create(
            maintenance_request=maintenance_request,
            action='created',
            changed_by=request.user,
            notes='Maintenance request created'
        )
        
        return maintenance_request

class MaintenanceRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating maintenance requests"""
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'title', 'description', 'category', 'priority', 'status', 
            'assigned_to', 'preferred_date', 'estimated_cost', 'actual_cost',
            'access_instructions', 'permission_to_enter', 'tenant_present'
        ]
    
    def update(self, instance, validated_data):
        """Update request and track changes"""
        request = self.context['request']
        old_values = {}
        
        # Track changes for history
        for field in ['status', 'priority', 'assigned_to', 'estimated_cost', 'actual_cost']:
            if field in validated_data and getattr(instance, field) != validated_data[field]:
                old_values[field] = getattr(instance, field)
        
        instance = super().update(instance, validated_data)
        
        # Create history entries for tracked changes
        for field, old_value in old_values.items():
            new_value = validated_data[field]
            action_map = {
                'status': 'status_changed',
                'priority': 'priority_changed',
                'assigned_to': 'assigned',
                'estimated_cost': 'cost_updated',
                'actual_cost': 'cost_updated'
            }
            
            MaintenanceHistory.objects.create(
                maintenance_request=instance,
                action=action_map.get(field, 'updated'),
                old_value=str(old_value) if old_value else '',
                new_value=str(new_value) if new_value else '',
                changed_by=request.user,
                notes=f'{field.replace("_", " ").title()} changed'
            )
        
        return instance

class MaintenanceCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    
    class Meta:
        model = MaintenanceComment
        fields = ['comment', 'is_internal']
    
    def create(self, validated_data):
        """Create comment and trigger notification"""
        request = self.context['request']
        maintenance_request = self.context['maintenance_request']
        
        validated_data['author'] = request.user
        validated_data['maintenance_request'] = maintenance_request
        
        comment = super().create(validated_data)
        
        # Create history entry
        MaintenanceHistory.objects.create(
            maintenance_request=maintenance_request,
            action='comment_added',
            changed_by=request.user,
            notes=f'Comment added: {comment.comment[:100]}...'
        )
        
        return comment

class MaintenanceStatsSerializer(serializers.Serializer):
    """Serializer for maintenance statistics"""
    total_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    in_progress_requests = serializers.IntegerField()
    completed_requests = serializers.IntegerField()
    urgent_requests = serializers.IntegerField()
    overdue_requests = serializers.IntegerField()
    avg_completion_time = serializers.FloatField()
    completion_rate = serializers.FloatField()
    
    # Stats by category
    requests_by_category = serializers.DictField()
    
    # Stats by priority
    requests_by_priority = serializers.DictField()
    
    # Recent activity
    recent_requests = MaintenanceRequestSerializer(many=True)
