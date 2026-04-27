from decimal import Decimal
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from properties.models import Property, Room
from bookings.models import Booking
from .services import AIService

class StudentAIService(AIService):
    """
    Enhanced AI Service specifically for student accommodation
    """
    
    def __init__(self):
        super().__init__()
        # Add student-specific intent patterns
        self.intent_patterns.update({
            'student_budget_search': [
                r'student.*budget', r'money.*have', r'can.*afford',
                r'budget.*student', r'poor.*student', r'cheap.*student',
                r'limited.*budget', r'student.*price', r'affordable.*student'
            ],
            'booking_appointment': [
                r'book.*appointment', r'schedule.*visit', r'see.*property',
                r'visit.*property', r'tour.*property', r'appointment.*booking',
                r'when.*can.*visit', r'schedule.*viewing'
            ],
            'student_accommodation': [
                r'student.*hostel', r'university.*housing', r'campus.*housing',
                r'student.*room', r'dormitory', r'student.*apartment',
                r'near.*university', r'campus.*near'
            ],
            'payment_planning': [
                r'payment.*plan', r'installment', r'pay.*later',
                r'deposit.*amount', r'first.*payment', r'how.*much.*pay',
                r'payment.*schedule', r'pay.*installment'
            ],
            'availability_validation': [
                r'full.*booked', r'no.*rooms', r'fully.*occupied',
                r'all.*taken', r'no.*vacancy', r'fully.*booked',
                r'rooms.*full', r'hostel.*full', r'available.*rooms',
                r'vacancy.*check', r'room.*status', r'booking.*confirmed'
            ]
        })
        
        # Student-specific price ranges
        self.student_budget_ranges = {
            'very_low': {'min': 0, 'max': 100, 'description': 'Basic shared accommodation'},
            'low': {'min': 100, 'max': 200, 'description': 'Standard student hostel'},
            'medium': {'min': 200, 'max': 350, 'description': 'Comfortable student apartment'},
            'high': {'min': 350, 'max': 500, 'description': 'Premium student housing'}
        }
        
        # Student amenities priority
        self.student_amenities_priority = [
            'wifi', 'study', 'library', 'security', 'quiet', 'kitchen',
            'laundry', 'transport', 'campus', 'affordable'
        ]

    def process_message(self, user_message, user=None):
        """
        Enhanced processing with student-specific features
        """
        try:
            # Detect if this is a student-specific query
            is_student_query = self.is_student_query(user_message)
            
            # Get student profile if available
            student_profile = self.get_student_profile(user) if user else None
            
            # Detect intent
            intent = self.detect_intent(user_message)
            
            # Extract entities
            entities = self.extract_entities(user_message)
            
            # Enhance entities with student profile data
            if student_profile:
                entities = self.enhance_entities_with_profile(entities, student_profile)
            
            # Route to appropriate handler
            if intent == 'student_budget_search':
                return self.handle_student_budget_search(user_message, entities, student_profile)
            elif intent == 'booking_appointment':
                return self.handle_booking_appointment(user_message, entities, user)
            elif intent == 'student_accommodation':
                return self.handle_student_accommodation(user_message, entities, student_profile)
            elif intent == 'payment_planning':
                return self.handle_payment_planning(user_message, entities, student_profile)
            elif intent == 'availability_validation':
                return self.handle_availability_validation(user_message, entities, student_profile)
            else:
                # Use parent class for other intents
                return super().process_message(user_message, user)
                
        except Exception as e:
            return {
                'response': 'I apologize, but I encountered an error processing your request. Please try again.',
                'properties': [],
                'intent': 'error',
                'error': str(e)
            }

    def is_student_query(self, message):
        """Check if the query is student-related"""
        student_keywords = [
            'student', 'university', 'campus', 'college', 'hostel',
            'dormitory', 'study', 'academic', 'semester', 'course',
            'makerere', 'kyambogo', 'muk', 'education'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in student_keywords)

    def get_student_profile(self, user):
        """Get student-specific profile information"""
        if not user:
            return None
            
        # Get user's booking history to understand preferences
        previous_bookings = Booking.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Get user's budget from previous interactions or profile
        # This could be enhanced with actual user profile fields
        profile = {
            'previous_locations': [],
            'average_budget': None,
            'preferred_property_types': [],
            'student_status': user.role == 'tenant'  # Assuming students are tenants
        }
        
        if previous_bookings.exists():
            total_spent = sum(b.final_amount for b in previous_bookings if b.final_amount)
            if previous_bookings.count() > 0:
                profile['average_budget'] = total_spent / previous_bookings.count()
            
            # Extract preferred locations
            for booking in previous_bookings:
                if booking.rental_property.city not in profile['previous_locations']:
                    profile['previous_locations'].append(booking.rental_property.city)
                
                if booking.rental_property.property_type not in profile['preferred_property_types']:
                    profile['preferred_property_types'].append(booking.rental_property.property_type)
        
        return profile

    def enhance_entities_with_profile(self, entities, student_profile):
        """Enhance extracted entities with student profile data"""
        if not student_profile:
            return entities
            
        # Use student's average budget if no price specified
        if not entities['price_max'] and student_profile['average_budget']:
            entities['price_max'] = student_profile['average_budget']
        
        # Add student amenities to amenities list
        student_amenities = ['wifi', 'study', 'security', 'quiet']
        for amenity in student_amenities:
            if amenity not in entities['amenities']:
                entities['amenities'].append(amenity)
        
        return entities

    def handle_student_budget_search(self, message, entities, student_profile):
        """Handle student-specific budget searches"""
        
        # Determine budget category
        budget_category = self.determine_budget_category(entities, student_profile)
        
        # Build student-specific query
        queryset = Property.objects.filter(is_active=True, is_approved=True)
        
        # Apply budget filter
        if budget_category:
            queryset = queryset.filter(
                rent_per_month__gte=budget_category['min'],
                rent_per_month__lte=budget_category['max']
            )
        elif entities['price_max']:
            queryset = queryset.filter(rent_per_month__lte=entities['price_max'])
        
        # Filter for student-friendly properties
        student_friendly_filter = Q(
            Q(target_audience='student') |
            Q(property_type__in=['hostel', 'dormitory', 'paying_guest']) |
            Q(description__icontains__in=['student', 'university', 'campus'])
        )
        queryset = queryset.filter(student_friendly_filter)
        
        # Apply location filter
        if entities['location']:
            location_filter = Q()
            for loc in entities['location']:
                location_filter |= (
                    Q(city__icontains=loc) |
                    Q(locality__icontains=loc) |
                    Q(nearby_landmarks__icontains=loc)
                )
            queryset = queryset.filter(location_filter)
        
        # Prioritize student amenities
        if entities['amenities']:
            amenity_filter = Q()
            for amenity in entities['amenities']:
                amenity_filter |= Q(amenities__icontains=amenity)
            queryset = queryset.filter(amenity_filter)
        
        # Get results
        properties = list(queryset[:10])
        
        if properties:
            property_list = []
            for prop in properties:
                # Calculate affordability score
                affordability_score = self.calculate_affordability_score(prop, budget_category)
                
                property_list.append({
                    'id': prop.id,
                    'name': prop.name,
                    'type': prop.property_type,
                    'location': f"{prop.locality}, {prop.city}",
                    'price': float(prop.rent_per_month),
                    'description': prop.description[:100] + '...' if len(prop.description) > 100 else prop.description,
                    'image': prop.images.first().image.url if prop.images.exists() else None,
                    'affordability_score': affordability_score,
                    'student_features': self.get_student_features(prop),
                    'distance_to_campus': self.estimate_campus_distance(prop),
                    'available_rooms': prop.available_rooms
                })
            
            # Sort by affordability score
            property_list.sort(key=lambda x: x['affordability_score'], reverse=True)
            
            response = f"I found {len(properties)} great student accommodations within your budget! 🎓\n\n"
            
            if budget_category:
                response += f"**Budget Range:** ${budget_category['min']} - ${budget_category['max']} per month\n"
                response += f"**Category:** {budget_category['description']}\n\n"
            
            response += "Here are the best options for you:\n\n"
            
            for i, prop in enumerate(property_list[:3], 1):
                response += f"{i}. **{prop['name']}** - ${prop['price']}/month\n"
                response += f"   📍 {prop['location']}\n"
                response += f"   ⭐ Affordability: {prop['affordability_score']}/10\n"
                response += f"   🏠 {prop['available_rooms']} rooms available\n"
                response += f"   🎓 Student features: {', '.join(prop['student_features'])}\n\n"
            
            response += "Would you like me to help you book a viewing appointment for any of these properties?"
            
            return {
                'response': response,
                'properties': property_list,
                'intent': 'student_budget_search',
                'total_results': len(properties),
                'budget_category': budget_category,
                'student_recommendations': True
            }
        else:
            # Provide budget advice
            advice = self.get_student_budget_advice(budget_category, entities)
            
            return {
                'response': f"I couldn't find student accommodations in your budget range. {advice}",
                'properties': [],
                'intent': 'student_budget_search',
                'total_results': 0,
                'budget_advice': True
            }

    def handle_booking_appointment(self, message, entities, user):
        """Handle booking appointment requests"""
        
        if not user:
            return {
                'response': "Please login first to schedule a property viewing appointment.",
                'properties': [],
                'intent': 'booking_appointment',
                'requires_login': True
            }
        
        # Extract property preference from message or context
        property_id = self.extract_property_id_from_message(message)
        
        if property_id:
            try:
                property_obj = Property.objects.get(id=property_id)
                return self.schedule_property_viewing(property_obj, user, entities)
            except Property.DoesNotExist:
                return {
                    'response': "I couldn't find that property. Would you like me to show you available properties first?",
                    'properties': [],
                    'intent': 'booking_appointment'
                }
        else:
            # Ask which property they want to visit
            return {
                'response': "I'd be happy to help you schedule a property viewing! 🏠\n\n"
                         "Which property would you like to visit? You can:\n"
                         "1. Tell me the property name\n"
                         "2. Say 'schedule viewing for [property name]'\n"
                         "3. Let me show you available properties first\n\n"
                         "When would you prefer to visit? (Today, Tomorrow, This Week, Next Week)",
                'properties': [],
                'intent': 'booking_appointment',
                'next_step': 'property_selection'
            }

    def handle_student_accommodation(self, message, entities, student_profile):
        """Handle student-specific accommodation searches"""
        
        # Focus on university areas
        university_locations = ['makerere', 'kyambogo', 'muk', 'kampala international university']
        
        # If no location specified, assume near universities
        if not entities['location']:
            entities['location'] = university_locations
        
        # Filter for student housing
        queryset = Property.objects.filter(
            is_active=True,
            is_approved=True
        ).filter(
            Q(target_audience='student') |
            Q(property_type__in=['hostel', 'dormitory', 'paying_guest'])
        )
        
        # Apply location filter for universities
        if entities['location']:
            location_filter = Q()
            for loc in entities['location']:
                location_filter |= (
                    Q(city__icontains=loc) |
                    Q(locality__icontains=loc) |
                    Q(nearby_landmarks__icontains=loc) |
                    Q(description__icontains=loc)
                )
            queryset = queryset.filter(location_filter)
        
        properties = list(queryset[:8])
        
        if properties:
            response = f"Here are student accommodations near universities: 🎓\n\n"
            
            property_list = []
            for prop in properties:
                # Calculate distance to nearest university
                nearest_university = self.find_nearest_university(prop)
                
                property_list.append({
                    'id': prop.id,
                    'name': prop.name,
                    'type': prop.property_type,
                    'location': f"{prop.locality}, {prop.city}",
                    'price': float(prop.rent_per_month),
                    'description': prop.description[:100] + '...' if len(prop.description) > 100 else prop.description,
                    'image': prop.images.first().image.url if prop.images.exists() else None,
                    'nearest_university': nearest_university,
                    'student_rating': self.get_student_rating(prop),
                    'popular_features': self.get_popular_student_features(prop)
                })
            
            for i, prop in enumerate(property_list[:5], 1):
                response += f"{i}. **{prop['name']}** - ${prop['price']}/month\n"
                response += f"   📍 {prop['location']}\n"
                response += f"   🎓 Nearest: {prop['nearest_university']}\n"
                response += f"   ⭐ Student Rating: {prop['student_rating']}/5\n"
                response += f"   🔥 Popular: {', '.join(prop['popular_features'])}\n\n"
            
            response += "All these properties offer student-friendly amenities like WiFi, study areas, and flexible payment terms. "
            response += "Would you like to schedule a viewing or get more details about any property?"
            
            return {
                'response': response,
                'properties': property_list,
                'intent': 'student_accommodation',
                'total_results': len(properties),
                'student_focused': True
            }
        else:
            return {
                'response': "I couldn't find student accommodations near universities. Would you like me to search in a different area or show you all available properties?",
                'properties': [],
                'intent': 'student_accommodation',
                'total_results': 0
            }

    def handle_payment_planning(self, message, entities, student_profile):
        """Handle payment planning and deposit information"""
        
        response = "I can help you understand the payment structure for student accommodations! 💰\n\n"
        
        response += "**Typical Payment Structure for Students:**\n\n"
        response += "🏠 **Monthly Rent:** Varies by property type\n"
        response += "   • Shared Hostel Room: $80 - $150/month\n"
        response += "   • Private Hostel Room: $120 - $250/month\n"
        response += "   • Student Apartment: $200 - $400/month\n\n"
        
        response += "💰 **Security Deposit:** Usually 1 month's rent\n"
        response += "   • Refundable at the end of stay\n"
        response += "   • Must be paid before move-in\n\n"
        
        response += "📅 **Payment Schedule Options:**\n"
        response += "   • Monthly: Pay at the beginning of each month\n"
        response += "   • Quarterly: Pay 3 months at a time (5% discount)\n"
        response += "   • Semester: Pay 4-6 months at a time (10% discount)\n\n"
        
        response += "💳 **Payment Methods Accepted:**\n"
        response += "   • Mobile Money (MTN, Airtel)\n"
        response += "   • Bank Transfer\n"
        response += "   • Cash (at property office)\n\n"
        
        if entities['price_max']:
            response += f"**Based on your budget of ${entities['price_max']}:**\n"
            
            if entities['price_max'] <= 150:
                response += "• You can afford shared hostel accommodation\n"
                response += "• Initial payment needed: ~${entities['price_max'] * 2} (1st month + deposit)\n"
            elif entities['price_max'] <= 250:
                response += "• You can afford private hostel rooms\n"
                response += "• Initial payment needed: ~${entities['price_max'] * 2} (1st month + deposit)\n"
            else:
                response += "• You can afford student apartments\n"
                response += "• Initial payment needed: ~${entities['price_max'] * 2} (1st month + deposit)\n"
        
        response += "\n**💡 Student Tips:**\n"
        response += "• Look for semester discounts\n"
        response += "• Consider shared rooms to save money\n"
        response += "• Book early for better rates\n"
        response += "• Ask about student discounts\n\n"
        
        response += "Would you like me to show you properties within your budget, or do you need help with anything else about payments?"
        
        return {
            'response': response,
            'properties': [],
            'intent': 'payment_planning',
            'payment_guide': True
        }

    def handle_availability_validation(self, message, entities, student_profile):
        """Handle availability validation and full hostel scenarios"""
        
        response = "I understand you're checking availability! Let me help you with real-time hostel status 🏠📊\n\n"
        
        # Check if user is asking about specific hostel
        hostel_name = self.extract_hostel_name_from_message(message)
        
        if hostel_name:
            # Check specific hostel availability
            availability_info = self.check_hostel_availability(hostel_name)
            
            if availability_info['is_full']:
                response += f"**{hostel_name} Status:** 🔴 FULLY BOOKED\n\n"
                response += f"**Current Occupancy:** {availability_info['occupancy_rate']}%\n"
                response += f"**Next Available:** {availability_info['next_available']}\n\n"
                
                response += "**Alternative Options:**\n"
                response += f"1. **Join Waiting List** - I can add you to {hostel_name}'s waiting list\n"
                response += f"2. **Check Similar Hostels** - Find nearby alternatives with similar features\n"
                response += f"3. **Set Availability Alert** - I'll notify you when rooms become available\n\n"
                
                response += "**🔔 Want me to help?**\n"
                response += "• **Add to Waiting List**: I can notify you when rooms open up\n"
                response += "• **Find Alternatives**: Similar hostels in the same area\n"
                response += "• **Set Alerts**: Get notified when your preferred dates are available\n"
                response += "• **Check Different Dates**: Maybe different dates have availability\n\n"
                
                response += "Which option would you prefer? I can help you immediately!"
                
                return {
                    'response': response,
                    'properties': [],
                    'intent': 'availability_validation',
                    'hostel_status': 'fully_booked',
                    'hostel_name': hostel_name,
                    'alternatives_available': True,
                    'waiting_list_available': True
                }
            else:
                response += f"**{hostel_name} Status:** 🟢 ROOMS AVAILABLE\n\n"
                response += f"**Available Rooms:** {availability_info['available_rooms']}\n"
                response += f"**Occupancy Rate:** {availability_info['occupancy_rate']}%\n\n"
                
                response += "**Ready to Book:**\n"
                response += "✅ Rooms are available for your dates\n"
                response += "✅ I can help you book immediately\n"
                response += "✅ Student discounts may apply\n\n"
                
                response += "Would you like me to help you book a room at " + hostel_name + "?"
                
                return {
                    'response': response,
                    'properties': availability_info.get('available_properties', []),
                    'intent': 'availability_validation',
                    'hostel_status': 'available',
                    'hostel_name': hostel_name,
                    'ready_to_book': True
                }
        else:
            # General availability check
            response += "**Real-Time Hostel Availability Check** 🏠📊\n\n"
            response += "I can check availability for any hostel you're interested in! Just tell me:\n\n"
            response += "**🏠 Hostel Name**: Which hostel are you checking?\n"
            response += "**📅 Your Dates**: When do you need the room?\n"
            response += "**👥 Room Type**: Shared room, private room, or apartment?\n"
            response += "**💰 Budget Range**: What's your budget range?\n\n"
            
            response += "**💡 Quick Availability Tips:**\n"
            response += "• **Book Early**: Popular hostels fill up quickly\n"
            response += "• **Have Alternatives**: Choose 2-3 backup options\n"
            response += "• **Check Different Dates**: Flexibility increases chances\n"
            response += "• **Contact Directly**: Sometimes faster than online booking\n\n"
            
            response += "**Example Requests:**\n"
            response += "• \"Check availability at Makerere Heights Hostel for next month\"\n"
            response += "• \"Is University Lodge fully booked for September?\"\n"
            response += "• \"Any rooms available at Student Haven for August?\"\n\n"
            
            response += "Which hostel would you like me to check?"
            
            return {
                'response': response,
                'properties': [],
                'intent': 'availability_validation',
                'general_inquiry': True
            }

    def extract_hostel_name_from_message(self, message):
        """Extract hostel name from user message"""
        # Common hostel names and patterns
        hostel_patterns = {
            'makerere heights': ['makerere heights', 'heights hostel'],
            'university lodge': ['university lodge', 'uni lodge'],
            'student haven': ['student haven', 'haven hostel'],
            'campus lodge': ['campus lodge', 'campus hostel'],
            'kyambogo hostel': ['kyambogo hostel', 'kab hostel'],
            'muk hostel': ['muk hostel', 'main hostel']
        }
        
        message_lower = message.lower()
        
        for hostel, patterns in hostel_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return hostel.title()
        
        return None

    def check_hostel_availability(self, hostel_name):
        """Check real-time availability for a specific hostel"""
        # This would ideally connect to a real-time availability system
        # For now, simulate availability checks
        
        # Simulate different scenarios
        import random
        
        # 70% chance hostel is fully booked (realistic for popular student hostels)
        is_full = random.choice([True, False, False, True, False])  # 60% full
        
        if is_full:
            return {
                'is_full': True,
                'occupancy_rate': 100,
                'next_available': self.calculate_next_available_date(),
                'waiting_list_size': random.randint(5, 25),
                'popular_dates': ['September', 'October', 'January']
            }
        else:
            # Simulate partial availability
            available_rooms = random.randint(1, 8)
            total_rooms = 20
            occupancy_rate = ((total_rooms - available_rooms) / total_rooms) * 100
            
            return {
                'is_full': False,
                'available_rooms': available_rooms,
                'occupancy_rate': round(occupancy_rate, 1),
                'room_types': self.get_available_room_types(available_rooms),
                'price_range': '$100-200',
                'available_properties': self.generate_available_properties(hostel_name, available_rooms)
            }

    def calculate_next_available_date(self):
        """Calculate when hostel might have availability"""
        from datetime import datetime, timedelta
        import random
        
        today = datetime.now()
        
        # Simulate next availability (2-8 weeks from now)
        weeks_until_available = random.randint(2, 8)
        next_available = today + timedelta(weeks=weeks_until_available)
        
        return next_available.strftime("%B %d, %Y")

    def get_available_room_types(self, available_rooms):
        """Get types of rooms available"""
        room_types = []
        
        if available_rooms >= 4:
            room_types.extend(['Private Rooms', 'Shared Rooms'])
        if available_rooms >= 2:
            room_types.append('Apartments')
        if available_rooms >= 1:
            room_types.append('Studio Rooms')
        
        return room_types

    def generate_available_properties(self, hostel_name, available_rooms):
        """Generate mock available properties for the hostel"""
        properties = []
        
        for i in range(min(available_rooms, 3)):
            room_types = ['Private Room', 'Shared Room', 'Studio']
            prices = [120, 150, 180, 200]
            
            properties.append({
                'id': i + 1,
                'name': f"{hostel_name} - Room {i + 1}",
                'type': random.choice(room_types),
                'price': random.choice(prices),
                'available_from': 'Next Month',
                'room_features': ['WiFi', 'Study Area', 'Security']
            })
        
        return properties

    # Helper methods
    def determine_budget_category(self, entities, student_profile):
        """Determine student's budget category"""
        if entities['price_max']:
            price = entities['price_max']
            
            for category, range_data in self.student_budget_ranges.items():
                if range_data['min'] <= price <= range_data['max']:
                    return range_data
        
        # Use student profile if available
        if student_profile and student_profile['average_budget']:
            avg_budget = student_profile['average_budget']
            for category, range_data in self.student_budget_ranges.items():
                if range_data['min'] <= avg_budget <= range_data['max']:
                    return range_data
        
        return None

    def calculate_affordability_score(self, property, budget_category):
        """Calculate affordability score for a property"""
        if not budget_category:
            return 5.0  # Neutral score
        
        price = property.rent_per_month
        budget_max = budget_category['max']
        budget_min = budget_category['min']
        
        if price <= budget_min:
            return 10.0  # Very affordable
        elif price <= budget_max:
            # Linear scaling within budget
            score = 10.0 - ((price - budget_min) / (budget_max - budget_min)) * 3
            return round(score, 1)
        else:
            # Over budget
            over_budget = price - budget_max
            score = max(1.0, 7.0 - (over_budget / budget_max) * 5)
            return round(score, 1)

    def get_student_features(self, property):
        """Get student-specific features for a property"""
        features = []
        
        student_keywords = ['wifi', 'study', 'library', 'quiet', 'security', 'campus', 'university']
        description_lower = property.description.lower() + ' ' + property.amenities.lower()
        
        for keyword in student_keywords:
            if keyword in description_lower:
                features.append(keyword.replace('_', ' ').title())
        
        # Add common student features
        if property.property_type in ['hostel', 'dormitory']:
            features.extend(['Student Housing', 'Community'])
        
        if property.target_audience == 'student':
            features.append('Student Focused')
        
        return features[:5]  # Limit to 5 features

    def estimate_campus_distance(self, property):
        """Estimate distance to nearest campus"""
        # This would ideally use actual geolocation data
        campus_keywords = ['makerere', 'kyambogo', 'university', 'campus']
        description_lower = property.description.lower() + ' ' + property.locality.lower()
        
        for keyword in campus_keywords:
            if keyword in description_lower:
                return "Walking Distance"
        
        return "Short Commute"

    def get_student_budget_advice(self, budget_category, entities):
        """Provide budget advice for students"""
        advice = ""
        
        if not budget_category:
            advice = "Here are some budget-friendly options for students:\n\n"
            advice += "💡 **Money-Saving Tips:**\n"
            advice += "• Consider shared rooms to split costs\n"
            advice += "• Look for properties further from campus (lower rent)\n"
            advice += "• Book semester-long stays for discounts\n"
            advice += "• Find properties with inclusive utilities\n\n"
            advice += "💰 **Student Budget Ranges:**\n"
            advice += "• Very Low: $80-$100 (shared rooms)\n"
            advice += "• Low: $100-$200 (standard hostels)\n"
            advice += "• Medium: $200-$350 (comfortable apartments)\n\n"
            advice += "Would you like me to show you properties in a specific price range?"
        
        return advice

    def extract_property_id_from_message(self, message):
        """Extract property ID from user message"""
        # This would ideally use NLP to extract property references
        # For now, return None to prompt for property selection
        return None

    def schedule_property_viewing(self, property, user, entities):
        """Schedule a property viewing appointment"""
        # This would create an actual booking/appointment
        # For now, return a confirmation response
        
        response = f"Great! I can help you schedule a viewing for **{property.name}** 🏠\n\n"
        response += f"**Property Details:**\n"
        response += f"📍 Location: {property.locality}, {property.city}\n"
        response += f"💰 Price: ${property.rent_per_month}/month\n"
        response += f"🏠 Type: {property.property_type}\n"
        response += f"📞 Contact: {property.contact_number}\n\n"
        
        response += "**Next Steps:**\n"
        response += "1. **Call the property**: {property.contact_number}\n"
        response += "2. **Visit during office hours**: 9AM - 6PM\n"
        response += "3. **Bring these documents**:\n"
        response += "   • Student ID or Admission Letter\n"
        response += "   • National ID/Passport\n"
        response += "   • Proof of income (if applicable)\n\n"
        
        response += "**💡 Pro Tips:**\n"
        response += "• Call ahead to confirm availability\n"
        response += "• Ask about student discounts\n"
        response += "• Take photos during your visit\n"
        response += "• Ask about the payment process\n\n"
        
        response += "After you visit the property and like it, I can help you with the booking process. "
        response += "Just let me know if you want to proceed with the booking! 🎓"
        
        return {
            'response': response,
            'properties': [{
                'id': property.id,
                'name': property.name,
                'contact_number': property.contact_number,
                'location': f"{property.locality}, {property.city}",
                'viewing_scheduled': True
            }],
            'intent': 'booking_appointment',
            'action_required': 'contact_property'
        }

    def find_nearest_university(self, property):
        """Find the nearest university to a property"""
        universities = {
            'Makerere University': ['makerere', 'wandegeya'],
            'Kyambogo University': ['kyambogo', 'bweyogerere'],
            'Kampala International University': ['kansanga', 'kampala'],
            'Ndejje University': ['ndejje', 'luwero']
        }
        
        location_text = f"{property.locality} {property.city} {property.description}".lower()
        
        for university, keywords in universities.items():
            for keyword in keywords:
                if keyword in location_text:
                    return university
        
        return "Various Universities"

    def get_student_rating(self, property):
        """Get student rating for a property"""
        # This would ideally be based on actual student reviews
        # For now, calculate based on property features
        rating = 3.5  # Base rating
        
        student_features = self.get_student_features(property)
        rating += len(student_features) * 0.3
        
        if property.target_audience == 'student':
            rating += 0.5
        
        if property.property_type in ['hostel', 'dormitory']:
            rating += 0.3
        
        return min(5.0, round(rating, 1))

    def get_popular_student_features(self, property):
        """Get popular features among students"""
        all_features = self.get_student_features(property)
        
        # Prioritize most popular student features
        priority_features = ['WiFi', 'Security', 'Study', 'Quiet', 'Campus']
        popular = [f for f in all_features if f in priority_features]
        
        return popular[:3]

# Create student AI service instance
student_ai_service = StudentAIService()
