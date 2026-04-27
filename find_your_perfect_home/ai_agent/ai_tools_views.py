"""
AI Assistant Tools API Views
Add hostel booking tools to existing AI agent
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from properties.models import Property, Room
from bookings.models import Booking
from accounts.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_search_hostels(request):
    """AI-powered hostel search with Uganda-specific filters"""
    try:
        data = request.data
        
        # Build query filters
        filters = Q(is_active=True)
        
        # Location filter
        if data.get('location'):
            location = data['location'].lower()
            filters &= (
                Q(location__icontains=location) |
                Q(address__icontains=location) |
                Q(district__icontains=location)
            )
        
        # University filter
        if data.get('university'):
            university = data['university'].lower()
            university_areas = {
                'makerere': ['kikoni', 'wandegeya', 'bwaise', 'kasubi'],
                'kyambogo': ['kyambogo', 'banda', 'ntinda'],
                'bugema': ['bugema', 'wobulenzi', 'zirobwe'],
                'ucu': ['mukono', 'seeta', 'najjembe'],
                'must': ['mbarara', 'kakoba', 'ruharo']
            }
            
            if university in university_areas:
                areas = university_areas[university]
                location_filter = Q(location__in=[area.capitalize() for area in areas])
                filters &= location_filter
        
        # Price filter
        if data.get('max_price'):
            filters &= Q(price__lte=data['max_price'])
        
        # Room type filter
        if data.get('room_type'):
            filters &= Q(room_type__icontains=data['room_type'])
        
        # Gender filter
        if data.get('gender'):
            filters &= Q(gender_preference__icontains=data['gender'])
        
        # Amenities filter
        if data.get('amenities'):
            for amenity in data['amenities']:
                filters &= Q(amenities__icontains=amenity)
        
        # Distance to university filter
        if data.get('distance_to_university'):
            max_distance = data['distance_to_university']
            filters &= Q(distance_to_university__lte=max_distance)
        
        # Query properties
        properties = Property.objects.filter(filters).select_related('owner').prefetch_related('rooms')
        
        # Sort by relevance (featured first, then price)
        properties = properties.order_by('-is_featured', 'price')
        
        # Serialize results
        hostels = []
        for prop in properties:
            # Get available rooms
            available_rooms = prop.rooms.filter(is_available=True).count()
            
            hostel_data = {
                'id': prop.id,
                'name': prop.name,
                'location': prop.location,
                'district': prop.district,
                'price': prop.price,
                'rating': prop.rating or 0,
                'reviews_count': prop.reviews_count or 0,
                'description': prop.description,
                'images': [img.image.url for img in prop.images.all()[:3]],
                'amenities': prop.amenities.split(',') if prop.amenities else [],
                'gender_preference': prop.gender_preference,
                'distance_to_university': prop.distance_to_university,
                'available_rooms': available_rooms,
                'is_featured': prop.is_featured,
                'owner': {
                    'name': prop.owner.get_full_name(),
                    'phone': prop.owner.phone_number,
                    'verified': prop.owner.is_verified
                }
            }
            hostels.append(hostel_data)
        
        return Response({
            'success': True,
            'count': len(hostels),
            'results': hostels,
            'message': f'Found {len(hostels)} hostels matching your criteria'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Search failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_get_hostel_details(request, hostel_id):
    """Get detailed information about a specific hostel"""
    try:
        property = Property.objects.get(id=hostel_id, is_active=True)
        
        # Get rooms
        rooms = property.rooms.all()
        
        # Get recent reviews
        recent_reviews = property.reviews.all().order_by('-created_at')[:5]
        
        # Get similar hostels
        similar_hostels = Property.objects.filter(
            location=property.location,
            is_active=True
        ).exclude(id=property.id)[:3]
        
        hostel_data = {
            'id': property.id,
            'name': property.name,
            'location': property.location,
            'district': property.district,
            'address': property.address,
            'price': property.price,
            'rating': property.rating or 0,
            'reviews_count': property.reviews_count or 0,
            'description': property.description,
            'amenities': property.amenities.split(',') if property.amenities else [],
            'rules': property.rules.split(',') if property.rules else [],
            'gender_preference': property.gender_preference,
            'distance_to_university': property.distance_to_university,
            'is_featured': property.is_featured,
            'images': [img.image.url for img in property.images.all()],
            'rooms': [
                {
                    'id': room.id,
                    'type': room.room_type,
                    'capacity': room.capacity,
                    'price': room.price,
                    'is_available': room.is_available,
                    'amenities': room.amenities.split(',') if room.amenities else []
                }
                for room in rooms
            ],
            'reviews': [
                {
                    'user': review.user.get_full_name(),
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at
                }
                for review in recent_reviews
            ],
            'similar_hostels': [
                {
                    'id': similar.id,
                    'name': similar.name,
                    'location': similar.location,
                    'price': similar.price,
                    'rating': similar.rating or 0
                }
                for similar in similar_hostels
            ],
            'owner': {
                'name': property.owner.get_full_name(),
                'phone': property.owner.phone_number,
                'email': property.owner.email,
                'verified': property.owner.is_verified,
                'response_rate': property.owner.response_rate or 95
            }
        }
        
        return Response({
            'success': True,
            'hostel': hostel_data,
            'message': f'Here are the details for {property.name}'
        })
        
    except Property.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Hostel not found',
            'message': 'The hostel you requested was not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to get hostel details.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_check_availability(request, hostel_id):
    """Check room availability for specific dates"""
    try:
        data = request.data
        check_in = datetime.strptime(data['check_in'], '%Y-%m-%d').date()
        check_out = datetime.strptime(data['check_out'], '%Y-%m-%d').date()
        
        property = Property.objects.get(id=hostel_id, is_active=True)
        
        # Check if dates are valid
        if check_in >= check_out:
            return Response({
                'success': False,
                'error': 'Invalid dates',
                'message': 'Check-out date must be after check-in date.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if property is available for these dates
        conflicting_bookings = Booking.objects.filter(
            property=property,
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out,
            check_out__gt=check_in
        )
        
        # Get available rooms
        all_rooms = property.rooms.all()
        available_rooms = []
        
        for room in all_rooms:
            # Check if room has conflicting bookings
            room_conflicts = conflicting_bookings.filter(room=room)
            
            if not room_conflicts.exists():
                available_rooms.append({
                    'id': room.id,
                    'type': room.room_type,
                    'capacity': room.capacity,
                    'price': room.price,
                    'amenities': room.amenities.split(',') if room.amenities else []
                })
        
        # Calculate prices
        nights = (check_out - check_in).days
        base_price = property.price * nights
        
        # Add fees
        service_fee = base_price * Decimal('0.05')  # 5% service fee
        cleaning_fee = Decimal('10000')  # Fixed cleaning fee
        security_deposit = property.price  # One month's rent as deposit
        
        total = base_price + service_fee + cleaning_fee
        
        return Response({
            'success': True,
            'available': len(available_rooms) > 0,
            'rooms': available_rooms,
            'prices': {
                'base_price': base_price,
                'service_fee': service_fee,
                'cleaning_fee': cleaning_fee,
                'security_deposit': security_deposit,
                'total': total,
                'nights': nights,
                'currency': 'UGX'
            },
            'message': f'Rooms are available from {data["check_in"]} to {data["check_out"]}' if available_rooms else 'No rooms available for the selected dates'
        })
        
    except Property.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Hostel not found',
            'message': 'The hostel you requested was not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to check availability.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_calculate_booking_cost(request):
    """Calculate total cost for booking including fees and taxes"""
    try:
        data = request.data
        
        property = Property.objects.get(id=data['hostel_id'], is_active=True)
        check_in = datetime.strptime(data['check_in'], '%Y-%m-%d').date()
        check_out = datetime.strptime(data['check_out'], '%Y-%m-%d').date()
        guests = data.get('guests', 1)
        
        # Calculate nights
        nights = (check_out - check_in).days
        
        # Base price
        if data.get('room_type'):
            room = property.rooms.get(room_type=data['room_type'])
            base_price = room.price * nights
        else:
            base_price = property.price * nights
        
        # Additional guest fee
        if guests > 1:
            extra_guest_fee = (guests - 1) * Decimal('20000') * nights
            base_price += extra_guest_fee
        
        # Fees
        service_fee = base_price * Decimal('0.05')  # 5% service fee
        cleaning_fee = Decimal('10000')  # Fixed cleaning fee
        security_deposit = property.price  # One month's rent as deposit
        
        # Payment method fees
        payment_method = data.get('payment_method', 'mobile_money')
        payment_fees = {
            'mobile_money': {'fee': Decimal('0.025'), 'fixed': Decimal('500')},
            'credit_card': {'fee': Decimal('0.029'), 'fixed': Decimal('1500')},
            'cash': {'fee': Decimal('0'), 'fixed': Decimal('2000')}
        }
        
        payment_fee_info = payment_fees.get(payment_method, payment_fees['mobile_money'])
        payment_fee = (base_price * payment_fee_info['fee']) + payment_fee_info['fixed']
        
        total = base_price + service_fee + cleaning_fee + payment_fee
        
        return Response({
            'success': True,
            'cost_breakdown': {
                'base_price': base_price,
                'service_fee': service_fee,
                'cleaning_fee': cleaning_fee,
                'security_deposit': security_deposit,
                'payment_fee': payment_fee,
                'total': total,
                'nights': nights,
                'guests': guests,
                'currency': 'UGX'
            },
            'payment_options': [
                {
                    'method': 'Mobile Money',
                    'providers': [
                        {'name': 'MTN MoMo', 'code': 'MTN_MOMO', 'ussd': '*165*4#'},
                        {'name': 'Airtel Money', 'code': 'AIRTEL_MONEY', 'ussd': '*185#'},
                        {'name': 'Stanbic Mobile', 'code': 'STANBIC_MOBILE', 'ussd': '*290#'}
                    ]
                },
                {
                    'method': 'Credit Card',
                    'providers': [
                        {'name': 'Stripe', 'cards': ['Visa', 'Mastercard']},
                        {'name': 'Flutterwave', 'cards': ['Visa', 'Mastercard', 'UnionPay']}
                    ]
                }
            ],
            'message': f'Total cost: UGX {total:,}'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to calculate booking cost.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_compare_hostels(request):
    """Compare multiple hostels side by side"""
    try:
        hostel_ids = request.data.get('hostel_ids', [])
        criteria = request.data.get('criteria', ['price', 'location', 'amenities'])
        
        if len(hostel_ids) < 2:
            return Response({
                'success': False,
                'error': 'Need at least 2 hostels to compare',
                'message': 'Please select at least 2 hostels to compare.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        hostels = Property.objects.filter(
            id__in=hostel_ids,
            is_active=True
        ).prefetch_related('rooms', 'reviews')
        
        comparison_data = []
        
        for hostel in hostels:
            avg_rating = hostel.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
            
            hostel_data = {
                'id': hostel.id,
                'name': hostel.name,
                'location': hostel.location,
                'district': hostel.district,
                'price': hostel.price,
                'rating': round(avg_rating, 1),
                'reviews_count': hostel.reviews_count or 0,
                'amenities': hostel.amenities.split(',') if hostel.amenities else [],
                'gender_preference': hostel.gender_preference,
                'distance_to_university': hostel.distance_to_university,
                'available_rooms': hostel.rooms.filter(is_available=True).count(),
                'is_featured': hostel.is_featured,
                'images': [img.image.url for img in hostel.images.all()[:2]]
            }
            comparison_data.append(hostel_data)
        
        # Sort by price (default)
        comparison_data.sort(key=lambda x: x['price'])
        
        return Response({
            'success': True,
            'comparison': comparison_data,
            'criteria': criteria,
            'message': f'Comparing {len(comparison_data)} hostels'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to compare hostels.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_get_booking_status(request, booking_id):
    """Check the status of an existing booking"""
    try:
        # Try to find booking by ID or confirmation code
        booking = Booking.objects.filter(
            Q(id=booking_id) | Q(confirmation_code=booking_id)
        ).first()
        
        if not booking:
            return Response({
                'success': False,
                'error': 'Booking not found',
                'message': 'The booking you requested was not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user owns this booking
        if booking.user != request.user:
            return Response({
                'success': False,
                'error': 'Access denied',
                'message': 'You can only check your own bookings.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        booking_data = {
            'id': booking.id,
            'confirmation_code': booking.confirmation_code,
            'status': booking.status,
            'property': {
                'id': booking.property.id,
                'name': booking.property.name,
                'location': booking.property.location,
                'address': booking.property.address
            },
            'room': {
                'type': booking.room.room_type if booking.room else 'Not specified',
                'capacity': booking.room.capacity if booking.room else 0
            },
            'check_in': booking.check_in,
            'check_out': booking.check_out,
            'guests': booking.guests,
            'total_amount': booking.total_amount,
            'payment_method': booking.payment_method,
            'payment_status': booking.payment_status,
            'created_at': booking.created_at,
            'updated_at': booking.updated_at
        }
        
        return Response({
            'success': True,
            'booking': booking_data,
            'status': booking.status,
            'message': f'Your booking is {booking.status}'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to get booking status.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def ai_get_universities_info(request):
    """Get information about universities in Uganda"""
    universities = {
        'makerere': {
            'name': 'Makerere University',
            'location': 'Kampala',
            'popular_areas': ['Kikoni', 'Wandegeya', 'Bwaise', 'Kasubi'],
            'average_hostel_price': 150000,
            'student_population': 40000,
            'nearby_hostels_count': 156,
            'description': "Uganda's premier university with excellent transport links",
            'coordinates': {'lat': 0.3176, 'lng': 32.5825}
        },
        'kyambogo': {
            'name': 'Kyambogo University',
            'location': 'Kampala',
            'popular_areas': ['Kyambogo', 'Banda', 'Ntinda'],
            'average_hostel_price': 120000,
            'student_population': 25000,
            'nearby_hostels_count': 89,
            'description': "Modern university with growing hostel options",
            'coordinates': {'lat': 0.3533, 'lng': 32.6022}
        },
        'bugema': {
            'name': 'Bugema University',
            'location': 'Luweero',
            'popular_areas': ['Bugema', 'Wobulenzi', 'Zirobwe'],
            'average_hostel_price': 80000,
            'student_population': 8000,
            'nearby_hostels_count': 34,
            'description': "Peaceful learning environment with affordable hostels",
            'coordinates': {'lat': 0.5667, 'lng': 32.6167}
        },
        'ucu': {
            'name': 'Uganda Christian University',
            'location': 'Mukono',
            'popular_areas': ['Mukono', 'Seeta', 'Najjembe'],
            'average_hostel_price': 180000,
            'student_population': 15000,
            'nearby_hostels_count': 67,
            'description': "Private university with quality hostel facilities",
            'coordinates': {'lat': 0.3533, 'lng': 32.6022}
        },
        'must': {
            'name': 'Mbarara University of Science and Technology',
            'location': 'Mbarara',
            'popular_areas': ['Mbarara', 'Kakoba', 'Ruharo'],
            'average_hostel_price': 100000,
            'student_population': 12000,
            'nearby_hostels_count': 45,
            'description': "Leading science university with modern accommodations",
            'coordinates': {'lat': -0.6033, 'lng': 30.6542}
        }
    }
    
    return Response({
        'success': True,
        'universities': universities,
        'message': 'University information retrieved successfully'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def ai_get_areas_info(request):
    """Get information about areas and neighborhoods in Uganda"""
    areas = {
        'kikoni': {
            'name': 'Kikoni',
            'location': 'Kampala',
            'description': 'Popular student area near Makerere University',
            'advantages': ['Walking distance to Makerere', 'Affordable prices', 'Many amenities'],
            'average_price': 150000,
            'transport_options': ['Boda boda', 'Taxi', 'Walking'],
            'security_level': 'Good',
            'popular_with': 'Makerere students',
            'coordinates': {'lat': 0.3276, 'lng': 32.5729}
        },
        'wandegeya': {
            'name': 'Wandegeya',
            'location': 'Kampala',
            'description': 'Vibrant student area with lots of entertainment',
            'advantages': ['Great nightlife', 'Many restaurants', 'Shopping centers'],
            'average_price': 180000,
            'transport_options': ['Boda boda', 'Taxi', 'Minibus'],
            'security_level': 'Good',
            'popular_with': 'Makerere and Kyambogo students',
            'coordinates': {'lat': 0.3176, 'lng': 32.5825}
        },
        'bwaise': {
            'name': 'Bwaise',
            'location': 'Kampala',
            'description': 'Budget-friendly area with good transport links',
            'advantages': ['Very affordable', 'Good transport', 'Local markets'],
            'average_price': 100000,
            'transport_options': ['Boda boda', 'Taxi', 'Minibus'],
            'security_level': 'Fair',
            'popular_with': 'Budget-conscious students',
            'coordinates': {'lat': 0.3376, 'lng': 32.5625}
        },
        'mukono': {
            'name': 'Mukono',
            'location': 'Mukono District',
            'description': 'Quiet town home to Uganda Christian University',
            'advantages': ['Peaceful environment', 'Clean air', 'Lower cost of living'],
            'average_price': 120000,
            'transport_options': ['Taxi', 'Private transport'],
            'security_level': 'Excellent',
            'popular_with': 'UCU students',
            'coordinates': {'lat': 0.3533, 'lng': 32.6022}
        },
        'mbarara': {
            'name': 'Mbarara',
            'location': 'Mbarara District',
            'description': 'Growing city home to MUST',
            'advantages': ['Modern facilities', 'Good security', 'Affordable living'],
            'average_price': 100000,
            'transport_options': ['Taxi', 'Boda boda', 'Minibus'],
            'security_level': 'Good',
            'popular_with': 'MUST students',
            'coordinates': {'lat': -0.6033, 'lng': 30.6542}
        }
    }
    
    return Response({
        'success': True,
        'areas': areas,
        'message': 'Area information retrieved successfully'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def ai_get_booking_tips(request):
    """Get helpful tips for booking hostels in Uganda"""
    topic = request.GET.get('topic', 'general')
    
    tips = {
        'budget': [
            "Book early to get better prices",
            "Consider shared rooms to save money",
            "Look for hostels slightly further from campus",
            "Check for student discounts",
            "Compare prices across different areas"
        ],
        'location': [
            "Consider transport costs when choosing location",
            "Check security ratings of the area",
            "Look for nearby amenities (markets, hospitals)",
            "Consider distance to your university",
            "Check public transport availability"
        ],
        'safety': [
            "Choose hostels with good security",
            "Check reviews from other students",
            "Verify the hostel is registered",
            "Know the emergency contacts",
            "Keep your valuables secure"
        ],
        'payment': [
            "Use secure payment methods",
            "Get receipts for all payments",
            "Be wary of unusually low prices",
            "Verify the hostel before paying",
            "Use mobile money for small deposits"
        ],
        'general': [
            "Read recent reviews from other students",
            "Check photos and virtual tours",
            "Understand the cancellation policy",
            "Know what's included in the price",
            "Keep contact information handy"
        ]
    }
    
    topic_tips = tips.get(topic, tips['general'])
    
    return Response({
        'success': True,
        'tips': topic_tips,
        'topic': topic,
        'message': f'Helpful tips for {topic}'
    })
