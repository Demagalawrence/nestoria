from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AgentProfile, AgentRequest, AgentAvailability, 
    AgentReview, AgentCommission
)
from properties.serializers import PropertySerializer

User = get_user_model()

class AgentProfileSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    is_online = serializers.ReadOnlyField()
    
    class Meta:
        model = AgentProfile
        fields = '__all__'
        read_only_fields = ['user', 'is_verified', 'verified_at', 'average_rating']
    
    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': obj.user.get_full_name(),
            'email': obj.user.email,
            'contact_number': obj.user.contact_number,
            'profile_picture': obj.user.profile_picture.url if obj.user.profile_picture else None
        }

class AgentAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentAvailability
        fields = '__all__'

class AgentRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    agent_name = serializers.CharField(source='assigned_agent.get_full_name', read_only=True)
    property_details = PropertySerializer(source='property', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AgentRequest
        fields = '__all__'
        read_only_fields = ['customer', 'assigned_agent', 'created_at', 'assigned_at', 'completed_at']

class AgentReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    
    class Meta:
        model = AgentReview
        fields = '__all__'
        read_only_fields = ['customer', 'agent', 'agent_request', 'created_at', 'updated_at']

class AgentCommissionSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = AgentCommission
        fields = '__all__'
        read_only_fields = ['agent', 'booking', 'property', 'created_at', 'updated_at']
