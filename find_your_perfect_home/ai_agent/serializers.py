from rest_framework import serializers
from .models import AIConversation, AIMessage

class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ['id', 'role', 'message', 'created_at', 'intent', 'properties_shown', 'confidence_score']
        read_only_fields = ['id', 'created_at', 'intent', 'properties_shown', 'confidence_score']

class AIConversationSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True, read_only=True)
    last_message = serializers.CharField(source='last_message', read_only=True)
    message_count = serializers.IntegerField(source='message_count', read_only=True)
    
    class Meta:
        model = AIConversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages', 'last_message', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AIConversationListSerializer(serializers.ModelSerializer):
    last_message = serializers.CharField(source='last_message', read_only=True)
    message_count = serializers.IntegerField(source='message_count', read_only=True)
    
    class Meta:
        model = AIConversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'last_message', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)

class ChatResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    properties = serializers.ListField(child=serializers.DictField(), required=False)
    intent = serializers.CharField(required=False)
    total_results = serializers.IntegerField(required=False)
    pricing_data = serializers.DictField(required=False)
    conversation_id = serializers.IntegerField()
    message_id = serializers.IntegerField()
