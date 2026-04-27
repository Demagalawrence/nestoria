from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import AIConversation, AIMessage
from .serializers import (
    AIConversationSerializer, AIConversationListSerializer, 
    ChatRequestSerializer, ChatResponseSerializer
)
from .services import ai_service
from .student_services import student_ai_service
from .tenant_services import tenant_ai_service

class AIConversationListView(generics.ListAPIView):
    serializer_class = AIConversationListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)

class AIConversationDetailView(generics.RetrieveAPIView):
    serializer_class = AIConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_ai(request):
    """
    Main chat endpoint for AI interaction
    """
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message = serializer.validated_data['message']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    try:
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(
                AIConversation, 
                id=conversation_id, 
                user=request.user
            )
        else:
            # Create new conversation
            conversation = AIConversation.objects.create(
                user=request.user,
                title=message[:50] + '...' if len(message) > 50 else message
            )
        
        # Save user message
        user_message = AIMessage.objects.create(
            conversation=conversation,
            role='user',
            message=message
        )
        
        # Process with AI service (intelligent routing)
        if request.user.role == 'tenant':  # Students are tenants
            # Check if it's a student query or general tenant query
            if student_ai_service.is_student_query(message):
                ai_response = student_ai_service.process_message(message, request.user)
            else:
                ai_response = tenant_ai_service.process_message(message, request.user)
        else:
            ai_response = ai_service.process_message(message, request.user)
        
        # Save AI response
        ai_message = AIMessage.objects.create(
            conversation=conversation,
            role='ai',
            message=ai_response['response'],
            intent=ai_response.get('intent', 'unknown'),
            properties_shown=ai_response.get('properties', []),
            confidence_score=0.85  # Default confidence score
        )
        
        # Prepare response
        response_data = {
            'response': ai_response['response'],
            'properties': ai_response.get('properties', []),
            'intent': ai_response.get('intent', 'unknown'),
            'conversation_id': conversation.id,
            'message_id': ai_message.id
        }
        
        # Add optional fields
        if 'total_results' in ai_response:
            response_data['total_results'] = ai_response['total_results']
        if 'pricing_data' in ai_response:
            response_data['pricing_data'] = ai_response['pricing_data']
        
        response_serializer = ChatResponseSerializer(response_data)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to process your message',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_new_conversation(request):
    """
    Create a new conversation
    """
    try:
        conversation = AIConversation.objects.create(
            user=request.user,
            title="New Conversation"
        )
        
        serializer = AIConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Failed to create conversation',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_conversation(request, pk):
    """
    Delete a conversation
    """
    try:
        conversation = get_object_or_404(
            AIConversation, 
            id=pk, 
            user=request.user
        )
        conversation.delete()
        
        return Response({'message': 'Conversation deleted successfully'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to delete conversation',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_statistics(request):
    """
    Get user's conversation statistics
    """
    try:
        conversations = AIConversation.objects.filter(user=request.user)
        messages = AIMessage.objects.filter(conversation__user=request.user)
        
        stats = {
            'total_conversations': conversations.count(),
            'total_messages': messages.count(),
            'user_messages': messages.filter(role='user').count(),
            'ai_messages': messages.filter(role='ai').count(),
            'recent_conversations': conversations.count() // 10,  # Last 10 conversations
            'most_common_intents': {}
        }
        
        # Calculate most common intents
        intents = messages.values_list('intent', flat=True)
        for intent in set(intents):
            if intent:  # Exclude None/empty intents
                stats['most_common_intents'][intent] = intents.count(intent)
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to get statistics',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_capabilities(request):
    """
    Get AI agent capabilities and help
    """
    capabilities = {
        'intents': [
            {
                'name': 'property_search',
                'description': 'Find properties based on location, price, and preferences',
                'examples': [
                    'Find me a hostel near Makerere University under $150',
                    'Show me apartments in Kampala below $1000',
                    'Looking for a cheap room near campus'
                ]
            },
            {
                'name': 'booking_help',
                'description': 'Get help with the booking process',
                'examples': [
                    'How do I book a property?',
                    'What documents do I need?',
                    'Explain the booking process'
                ]
            },
            {
                'name': 'pricing_inquiry',
                'description': 'Get information about pricing and costs',
                'examples': [
                    'What are the average prices?',
                    'How much does a hostel cost?',
                    'Show me properties under $500'
                ]
            },
            {
                'name': 'availability_check',
                'description': 'Check property availability',
                'examples': [
                    'Is this property available next month?',
                    'When can I move in?',
                    'Check availability for 3 months'
                ]
            },
            {
                'name': 'amenities_inquiry',
                'description': 'Learn about property amenities',
                'examples': [
                    'What amenities are included?',
                    'Is WiFi available?',
                    'Do you have parking space?'
                ]
            },
            {
                'name': 'location_inquiry',
                'description': 'Get location-specific information',
                'examples': [
                    'Where is this property located?',
                    'Properties near Makerere',
                    'How far is it from the city centre?'
                ]
            },
            {
                'name': 'faq',
                'description': 'General questions and support',
                'examples': [
                    'What payment methods do you accept?',
                    'How do I contact support?',
                    'What is your cancellation policy?'
                ]
            }
        ],
        'features': [
            'Natural language processing',
            'Context-aware conversations',
            'Property database integration',
            'Personalized recommendations',
            'Real-time availability checking',
            'Multi-language support (coming soon)'
        ],
        'tips': [
            'Be specific about location and budget for better results',
            'You can ask follow-up questions in the same conversation',
            'The AI remembers your preferences within a conversation',
            'Use natural language - no need for specific commands'
        ]
    }
    
    return Response(capabilities, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_assistant(request):
    """
    Specialized endpoint for student housing assistance
    """
    if request.user.role != 'tenant':
        return Response({
            'error': 'This endpoint is for students only',
            'message': 'Please use the regular chat endpoint for general assistance'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message = serializer.validated_data['message']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    try:
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(
                AIConversation, 
                id=conversation_id, 
                user=request.user
            )
        else:
            # Create new student conversation
            conversation = AIConversation.objects.create(
                user=request.user,
                title=f"Student: {message[:50]}..." if len(message) > 50 else message
            )
        
        # Save user message
        user_message = AIMessage.objects.create(
            conversation=conversation,
            role='user',
            message=message
        )
        
        # Process with Student AI Service
        ai_response = student_ai_service.process_message(message, request.user)
        
        # Save AI response
        ai_message = AIMessage.objects.create(
            conversation=conversation,
            role='ai',
            message=ai_response['response'],
            intent=ai_response.get('intent', 'student_help'),
            properties_shown=ai_response.get('properties', []),
            confidence_score=0.90  # Higher confidence for student-specific responses
        )
        
        # Prepare response
        response_data = {
            'response': ai_response['response'],
            'properties': ai_response.get('properties', []),
            'intent': ai_response.get('intent', 'student_help'),
            'conversation_id': conversation.id,
            'message_id': ai_message.id,
            'student_mode': True
        }
        
        # Add student-specific fields
        if 'budget_category' in ai_response:
            response_data['budget_category'] = ai_response['budget_category']
        if 'student_recommendations' in ai_response:
            response_data['student_recommendations'] = ai_response['student_recommendations']
        if 'affordability_score' in ai_response:
            response_data['affordability_score'] = ai_response['affordability_score']
        if 'payment_guide' in ai_response:
            response_data['payment_guide'] = ai_response['payment_guide']
        if 'next_step' in ai_response:
            response_data['next_step'] = ai_response['next_step']
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to process your student housing request',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_housing_guide(request):
    """
    Get comprehensive student housing guide
    """
    if request.user.role != 'tenant':
        return Response({
            'error': 'This guide is for students only'
        }, status=status.HTTP_403_FORBIDDEN)
    
    guide = {
        'welcome_message': "🎓 Welcome to Your Student Housing Assistant!",
        'how_it_works': [
            "Tell me your budget and preferred location",
            "I'll find student-friendly accommodations",
            "Schedule property viewings",
            "Get help with booking and payments"
        ],
        'budget_ranges': {
            'very_low': {
                'range': '$80 - $100',
                'description': 'Shared rooms in basic hostels',
                'features': ['Shared bathroom', 'Common kitchen', 'Basic WiFi']
            },
            'low': {
                'range': '$100 - $200',
                'description': 'Standard student hostels',
                'features': ['Private or shared room', 'Study areas', 'Security', 'WiFi']
            },
            'medium': {
                'range': '$200 - $350',
                'description': 'Comfortable student apartments',
                'features': ['Private room', 'Private kitchen', 'Study space', 'Better amenities']
            },
            'high': {
                'range': '$350 - $500',
                'description': 'Premium student housing',
                'features': ['En-suite room', 'Modern facilities', 'Gym', 'Premium location']
            }
        },
        'popular_university_areas': [
            {
                'university': 'Makerere University',
                'areas': ['Wandegeya', 'Kikoni', 'Bwaise'],
                'average_price': '$120 - $250',
                'transport': 'Walking distance or short taxi ride'
            },
            {
                'university': 'Kyambogo University',
                'areas': ['Bweyogerere', 'Kira', 'Naguru'],
                'average_price': '$100 - $200',
                'transport': 'Campus shuttle or taxi'
            },
            {
                'university': 'Kampala International University',
                'areas': ['Kansanga', 'Ggaba', 'Muyenga'],
                'average_price': '$150 - $300',
                'transport': 'Taxi or boda-boda'
            }
        ],
        'booking_process': [
            {
                'step': 1,
                'title': 'Find Your Perfect Home',
                'description': 'Chat with me to find accommodations within your budget',
                'estimated_time': '5-10 minutes'
            },
            {
                'step': 2,
                'title': 'Schedule Viewing',
                'description': 'Visit the property to see if it meets your needs',
                'estimated_time': '30-60 minutes'
            },
            {
                'step': 3,
                'title': 'Complete Booking',
                'description': 'Submit required documents and pay deposit',
                'estimated_time': '1-2 days'
            },
            {
                'step': 4,
                'title': 'Move In',
                'description': 'Pay first month\'s rent and collect your keys',
                'estimated_time': 'Move-in day'
            }
        ],
        'required_documents': [
            {
                'document': 'Student ID / Admission Letter',
                'description': 'Proof that you are a student',
                'required': 'Yes'
            },
            {
                'document': 'National ID / Passport',
                'description': 'Government-issued identification',
                'required': 'Yes'
            },
            {
                'document': 'Passport Photos',
                'description': 'Recent passport-sized photographs',
                'required': 'Yes'
            },
            {
                'document': 'Guarantor Letter',
                'description': 'Letter from parent/guardian (if under 21)',
                'required': 'Sometimes'
            },
            {
                'document': 'Proof of Income',
                'description': 'For students with part-time jobs',
                'required': 'Sometimes'
            }
        ],
        'payment_tips': [
            '💰 Pay semester-long stays to get discounts (5-10%)',
            '💳 Use mobile money for convenient payments',
            '📅 Pay on time to avoid late fees',
            '🏦 Keep payment receipts for your records',
            '💡 Ask about student discounts and special offers'
        ],
        'example_conversations': [
            {
                'user_message': "I'm a student at Makerere with $150 budget, need a room",
                'ai_response': "I found 5 great hostels near Makerere within your $150 budget! All include WiFi and study areas..."
            },
            {
                'user_message': "How much do I need to pay upfront?",
                'ai_response': "For student accommodations, you typically need: 1st month rent + 1 month security deposit..."
            },
            {
                'user_message': "Can I schedule a viewing for tomorrow?",
                'ai_response': "Absolutely! Which property would you like to visit? I can help you contact them..."
            }
        ],
        'emergency_contacts': [
            {
                'service': 'Property Emergency',
                'contact': 'Call your property manager directly'
            },
            {
                'service': 'Platform Support',
                'contact': '+256 123 456 789'
            },
            {
                'service': 'University Housing Office',
                'contact': 'Contact your university for assistance'
            }
        ]
    }
    
    return Response(guide, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tenant_assistant(request):
    """
    Specialized endpoint for tenant housing assistance
    """
    if request.user.role != 'tenant':
        return Response({
            'error': 'This endpoint is for tenants only',
            'message': 'Please use the regular chat endpoint for general assistance'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message = serializer.validated_data['message']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    try:
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(
                AIConversation, 
                id=conversation_id, 
                user=request.user
            )
        else:
            # Create new tenant conversation
            conversation = AIConversation.objects.create(
                user=request.user,
                title=f"Tenant: {message[:50]}..." if len(message) > 50 else message
            )
        
        # Save user message
        user_message = AIMessage.objects.create(
            conversation=conversation,
            role='user',
            message=message
        )
        
        # Process with Tenant AI Service
        ai_response = tenant_ai_service.process_message(message, request.user)
        
        # Save AI response
        ai_message = AIMessage.objects.create(
            conversation=conversation,
            role='ai',
            message=ai_response['response'],
            intent=ai_response.get('intent', 'tenant_help'),
            properties_shown=ai_response.get('properties', []),
            confidence_score=0.90  # Higher confidence for tenant-specific responses
        )
        
        # Prepare response
        response_data = {
            'response': ai_response['response'],
            'properties': ai_response.get('properties', []),
            'intent': ai_response.get('intent', 'tenant_help'),
            'conversation_id': conversation.id,
            'message_id': ai_message.id,
            'tenant_mode': True
        }
        
        # Add tenant-specific fields
        if 'family_focused' in ai_response:
            response_data['family_focused'] = ai_response['family_focused']
        if 'professional_focused' in ai_response:
            response_data['professional_focused'] = ai_response['professional_focused']
        if 'furnished' in ai_response:
            response_data['furnished'] = ai_response['furnished']
        if 'pet_friendly' in ai_response:
            response_data['pet_friendly'] = ai_response['pet_friendly']
        if 'parking_available' in ai_response:
            response_data['parking_available'] = ai_response['parking_available']
        if 'lease_info' in ai_response:
            response_data['lease_info'] = ai_response['lease_info']
        if 'support_info' in ai_response:
            response_data['support_info'] = ai_response['support_info']
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to process your tenant housing request',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tenant_housing_guide(request):
    """
    Get comprehensive tenant housing guide
    """
    if request.user.role != 'tenant':
        return Response({
            'error': 'This guide is for tenants only'
        }, status=status.HTTP_403_FORBIDDEN)
    
    guide = {
        'welcome_message': "🏠 Welcome to Your Tenant Housing Assistant!",
        'how_it_works': [
            "Tell me about your housing needs and preferences",
            "I'll find suitable accommodations for your lifestyle",
            "Help with booking appointments and negotiations",
            "Provide tenant rights and legal support"
        ],
        'tenant_types': [
            {
                'type': 'Family Housing',
                'description': 'Spacious homes for families with children',
                'budget_range': '$400 - $2000/month',
                'key_features': ['Multiple bedrooms', 'Security', 'Parking', 'Near schools'],
                'example_query': 'I need a 3-bedroom house for my family near good schools'
            },
            {
                'type': 'Professional Housing',
                'description': 'Modern apartments for working professionals',
                'budget_range': '$500 - $1500/month',
                'key_features': ['WiFi', 'Gym', 'Parking', 'City center access'],
                'example_query': 'Looking for a modern apartment near city center for work'
            },
            {
                'type': 'Long-term Rental',
                'description': 'Extended lease options with better rates',
                'budget_range': '$300 - $1200/month',
                'key_features': ['Lease discounts', 'Stable pricing', 'Home customization'],
                'example_query': 'I want to rent a house for 2 years with good monthly rates'
            },
            {
                'type': 'Furnished Apartments',
                'description': 'Move-in ready with all furniture included',
                'budget_range': '$600 - $1800/month',
                'key_features': ['Furniture included', 'Appliances', 'Immediate move-in'],
                'example_query': 'Need a furnished apartment I can move into this month'
            },
            {
                'type': 'Pet-Friendly Homes',
                'description': 'Properties that welcome your furry friends',
                'budget_range': '$400 - $1200/month',
                'key_features': ['Pet allowed', 'Pet areas', 'Near parks'],
                'example_query': 'I have a dog, need a pet-friendly apartment with garden'
            },
            {
                'type': 'Parking Required',
                'description': 'Homes with secure vehicle parking',
                'budget_range': '$500 - $1500/month',
                'key_features': ['Secure parking', 'Garage', 'Vehicle security'],
                'example_query': 'Need an apartment with secure parking for my car'
            }
        ],
        'budget_ranges': {
            'budget': {
                'range': '$200 - $400',
                'description': 'Basic apartments and rooms',
                'suitable_for': 'Single professionals, budget-conscious tenants'
            },
            'standard': {
                'range': '$400 - $700',
                'description': 'Quality apartments and small houses',
                'suitable_for': 'Couples, small families, professionals'
            },
            'comfortable': {
                'range': '$700 - $1200',
                'description': 'Spacious apartments and family homes',
                'suitable_for': 'Families, established professionals'
            },
            'premium': {
                'range': '$1200 - $2000',
                'description': 'Luxury apartments and large houses',
                'suitable_for': 'Executives, large families, expatriates'
            },
            'luxury': {
                'range': '$2000 - $5000',
                'description': 'High-end luxury housing',
                'suitable_for': 'Senior executives, diplomats'
            }
        },
        'popular_areas': [
            {
                'area': 'City Centre / CBD',
                'description': 'Prime business and commercial area',
                'average_price': '$800 - $2000',
                'best_for': 'Professionals, executives',
                'features': 'Modern apartments, offices, restaurants'
            },
            {
                'area': 'Nakasero / Kololo',
                'description': 'Upscale residential neighborhoods',
                'average_price': '$1200 - $3000',
                'best_for': 'Executives, expatriates',
                'features': 'Luxury homes, embassies, quiet environment'
            },
            {
                'area': 'Ntinda / Naguru',
                'description': 'Middle-class residential areas',
                'average_price': '$600 - $1200',
                'best_for': 'Families, professionals',
                'features': 'Family homes, good schools, shopping'
            },
            {
                'area': 'Muyenga / Bugolobi',
                'description': 'Suburban family neighborhoods',
                'average_price': '$800 - $1800',
                'best_for': 'Families, expatriates',
                'features': 'Spacious houses, international schools'
            },
            {
                'area': 'Bweyogerere / Kira',
                'description': 'Growing suburban areas',
                'average_price': '$400 - $800',
                'best_for': 'Budget-conscious families',
                'features': 'New developments, affordable housing'
            }
        ],
        'booking_process': [
            {
                'step': 1,
                'title': 'Find Your Perfect Home',
                'description': 'Tell me your needs and I\'ll find matching properties',
                'estimated_time': '5-15 minutes'
            },
            {
                'step': 2,
                'title': 'Schedule Property Viewing',
                'description': 'Visit the property to see if it meets your needs',
                'estimated_time': '30-60 minutes per property'
            },
            {
                'step': 3,
                'title': 'Negotiate Terms',
                'description': 'Discuss rent, lease terms, and conditions',
                'estimated_time': '1-2 days'
            },
            {
                'step': 4,
                'title': 'Sign Lease Agreement',
                'description': 'Review and sign the rental contract',
                'estimated_time': '1 day'
            },
            {
                'step': 5,
                'title': 'Make Payment',
                'description': 'Pay deposit and first month\'s rent',
                'estimated_time': 'Immediate'
            },
            {
                'step': 6,
                'title': 'Move In',
                'description': 'Collect keys and move into your new home',
                'estimated_time': 'Move-in day'
            }
        ],
        'required_documents': [
            {
                'document': 'National ID / Passport',
                'description': 'Government-issued identification',
                'required': 'Yes'
            },
            {
                'document': 'Proof of Income',
                'description': 'Payslips, employment letter, or business registration',
                'required': 'Yes'
            },
            {
                'document': 'Bank Statements',
                'description': 'Last 3-6 months bank statements',
                'required': 'Usually'
            },
            {
                'document': 'Referee Letters',
                'description': 'References from previous landlords or employers',
                'required': 'Sometimes'
            },
            {
                'document': 'Work Permit',
                'description': 'For non-Ugandan citizens',
                'required': 'If foreigner'
            }
        ],
        'tenant_rights': [
            {
                'right': 'Right to Habitable Property',
                'description': 'Property must be safe, clean, and livable'
            },
            {
                'right': 'Right to Privacy',
                'description': 'Landlord must give notice before entering'
            },
            {
                'right': 'Right to Quiet Enjoyment',
                'description': 'Peaceful living without disturbances'
            },
            {
                'right': 'Right to Fair Rent',
                'description': 'No arbitrary increases during lease term'
            },
            {
                'right': 'Right to Receipts',
                'description': 'Must receive receipts for all payments'
            },
            {
                'right': 'Right to Dispute Resolution',
                'description': 'Legal process for resolving disputes'
            }
        ],
        'payment_options': [
            {
                'method': 'Mobile Money',
                'providers': ['MTN Mobile Money', 'Airtel Money'],
                'best_for': 'Quick, convenient payments',
                'limits': 'Up to UGX 5,000,000 per transaction'
            },
            {
                'method': 'Bank Transfer',
                'providers': ['All Ugandan banks'],
                'best_for': 'Large payments, record keeping',
                'limits': 'No limit'
            },
            {
                'method': 'Cash',
                'providers': 'Direct payment to landlord',
                'best_for': 'Small amounts, immediate payment',
                'limits': 'Not recommended for large amounts'
            },
            {
                'method': 'Credit/Debit Card',
                'providers': 'Visa, MasterCard (coming soon)',
                'best_for': 'Online payments, international tenants',
                'limits': 'Varies by bank'
            }
        ],
        'example_conversations': [
            {
                'scenario': 'Family Looking for House',
                'user_message': "I'm looking for a 3-bedroom house for my family near good schools, budget $1500",
                'ai_response': "I found several family-friendly homes near good schools within your $1500 budget..."
            },
            {
                'scenario': 'Professional Seeking Apartment',
                'user_message': "Need a modern apartment near city center with parking, budget $1000",
                'ai_response': "Here are excellent options for working professionals in prime locations..."
            },
            {
                'scenario': 'Long-term Rental',
                'user_message': "Want to rent a furnished apartment for 2 years, what discounts can I get?",
                'ai_response': "For 2-year leases, you can get 15% discount on monthly rates..."
            },
            {
                'scenario': 'Pet Owner',
                'user_message': "I have a cat and dog, need pet-friendly housing with garden",
                'ai_response': "I found pet-friendly properties with gardens for your furry friends..."
            },
            {
                'scenario': 'Tenant Rights Question',
                'user_message': "My landlord wants to increase rent suddenly, what are my rights?",
                'ai_response': "According to tenant rights, landlords cannot increase rent arbitrarily..."
            }
        ],
        'emergency_contacts': [
            {
                'service': 'Legal Aid',
                'contact': 'Uganda Law Society - +256 414 237 191',
                'description': 'Free legal advice for tenants'
            },
            {
                'service': 'Tenant Association',
                'contact': 'Uganda Tenants Association',
                'description': 'Tenant rights advocacy and support'
            },
            {
                'service': 'Dispute Resolution',
                'contact': 'Local Council Courts',
                'description': 'Local dispute resolution services'
            },
            {
                'service': 'Platform Support',
                'contact': '+256 123 456 789',
                'description': 'Our tenant support team'
            }
        ],
        'tips_for_tenants': [
            '🏠 Always inspect property thoroughly before signing',
            '📋 Read lease agreement carefully, ask questions',
            '📸 Take photos of property condition when moving in',
            '💰 Keep records of all payments and receipts',
            '🤝 Maintain good communication with landlord',
            '📞 Know your tenant rights and responsibilities',
            '🔑 Get copies of all keys and access cards',
            '📝 Document any issues in writing',
            '🏡 Consider location convenience for work/school',
            '💡 Compare multiple properties before deciding'
        ]
    }
    
    return Response(guide, status=status.HTTP_200_OK)
