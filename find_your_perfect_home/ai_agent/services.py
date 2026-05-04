import re
import json
from decimal import Decimal
from django.db.models import Q, Avg
from properties.models import Property, Room
from bookings.models import Booking
from datetime import datetime, timedelta

class AIService:
    """
    Specialized Real Estate AI Service for Uganda rental properties
    """
    
    def __init__(self):
        # Enhanced intent patterns for real estate domain
        self.intent_patterns = {
            'property_search': [
                r'find.*property', r'search.*property', r'looking.*for',
                r'show.*properties', r'property.*near', r'apartment.*near',
                r'hostel.*near', r'room.*near', r'house.*near',
                r'what.*properties', r'available.*properties', r'need.*room',
                r'want.*apartment', r'looking.*hostel', r'self.*contained',
                r'bedsitter', r'single.*room', r'double.*room', r'accommodation',
                r'student.*accommodation', r'what.*apartements', r'what.*hostels',
                r'what.*apartments', r'what.*rooms', r'what.*hostels', r'what.*houses',
                r'bugema.*hostel', r'bugema.*accommodation', r'bugema.*room',
                r'rooms.*bugema', r'hostels.*bugema', r'accommodation.*bugema'
            ],
            'booking_help': [
                r'how.*book', r'booking.*process', r'how.*reserve',
                r'make.*booking', r'booking.*help', r'reserve.*room'
            ],
            'pricing_inquiry': [
                r'how.*much', r'price.*range', r'cost.*per', r'rent.*price',
                r'average.*price', r'budget.*under'
            ],
            'availability_check': [
                r'available.*when', r'when.*available', r'check.*availability',
                r'is.*available', r'vacant.*room'
            ],
            'amenities_inquiry': [
                r'what.*amenities', r'facilities.*include', r'wifi.*available',
                r'parking.*space', r'swimming.*pool', r'gym.*available'
            ],
            'location_inquiry': [
                r'where.*located', r'address.*of', r'near.*landmark',
                r'distance.*from', r'how.*far.*from'
            ],
            'faq': [
                r'what.*is', r'how.*does', r'can.*i', r'do.*you',
                r'help.*me', r'support', r'contact'
            ],
            'uganda_locations': [
                r'kampala', r'entebbe', r'jinja', r'mbarara', r'gulu',
                r'makerere', r'muk', r'kyambogo', r'kabale', r'fort portal',
                r'masaka', r'mbale', r'soroti', r'arua', r'lira',
                r'nansana', r'kira', r'makindye', r'kawempe', r'rubaga',
                r'nakawa', r'central', r'kololo', r'bugolobi', r'ntinda'
            ],
            'property_types': [
                r'apartment', r'hostel', r'self.*contained', r'bedsitter',
                r'single.*room', r'double.*room', r'family.*house',
                r'studio', r'flat', r'condominium', r'townhouse',
                r'guest.*house', r'serviced.*apartment', r'furnished',
                r'unfurnished', r'semi.*furnished'
            ],
            'budget_ranges': [
                r'under.*\d+', r'below.*\d+', r'cheap', r'affordable',
                r'budget.*friendly', r'economic', r'low.*cost',
                r'ugx.*\d+', r'shilling.*\d+', r'price.*range'
            ],
            'amenities_uganda': [
                r'wifi', r'internet', r'generator', r'backup.*power',
                r'solar', r'water.*tank', r'borehole', r'security',
                r'guard', r'cctv', r'parking', r'balcony', r'gym',
                r'swimming.*pool', r'playground', r'garden', r'fence',
                r'gate', r'air.*condition', r'fans', r'wardrobe',
                r'kitchen', r'shower', r'toilet', r'balcony'
            ],
            'rental_terms': [
                r'monthly', r'quarterly', r'annually', r'deposit',
                r'advance.*payment', r'utility.*bills', r'water.*bill',
                r'electricity.*bill', r'garbage.*collection', r'cleaning',
                r'maintenance', r'repair', r'lease.*agreement',
                r'tenancy.*agreement', r'notice.*period'
            ]
        }
        
        # Specialized real estate knowledge base
        self.real_estate_knowledge = {
            'uganda_property_market': {
                'average_prices': {
                    'kampala_studio': 300000,
                    'kampala_one_bedroom': 500000,
                    'kampala_two_bedroom': 800000,
                    'entebbe_apartment': 400000,
                    'makerere_hostel': 200000,
                    'jinja_apartment': 350000,
                    'mbarara_house': 600000
                },
                'popular_areas': {
                    'kampala': ['Kololo', 'Ntinda', 'Bugolobi', 'Muyenga', 'Bukoto'],
                    'makerere': ['Kikoni', 'Bwaise', 'Kawempe', 'Makerere Kikoni'],
                    'entebbe': ['Entebbe Town', 'Katabi', 'Nabweru'],
                    'jinja': ['Jinja Town', 'Masese', 'Walukuba']
                },
                'common_amenities': [
                    'WiFi Internet', 'Generator Backup', 'Solar Power',
                    'Security Guard', 'CCTV Surveillance', 'Parking Space',
                    'Water Tank', 'Borehole Water', 'Balcony',
                    'Air Conditioning', 'Wardrobe', 'Kitchen Cabinets'
                ]
            }
        }
        
        # Enhanced response templates for real estate
        self.response_templates = {
            'property_search': {
                'greeting': "🏠 I'd be happy to help you find the perfect property in Uganda!",
                'location_specific': "📍 Looking for properties in {location}? Let me search for available options.",
                'budget_friendly': "💰 For properties under UGX {budget}, I can suggest these affordable options:",
                'amenity_focused': "✨ You're looking for properties with {amenities}? Here are some great matches:",
                'student_housing': "🎓 For student accommodation near {university}, here are the best options:",
            },
            'pricing_info': {
                'average_prices': "💵 Current average rental prices in Uganda range from UGX {min} to UGX {max} per month.",
                'location_prices': "📍 In {location}, expect to pay between UGX {min} and UGX {max} for {property_type}.",
                'negotiation_tip': "💡 Pro tip: Most landlords in Uganda are open to negotiation, especially for long-term leases!",
            },
            'uganda_specific': {
                'power_backup': "⚡ Most properties in Uganda come with generator or solar backup due to occasional power outages.",
                'security': "🔒 Security is a priority - most properties have 24/7 guards, CCTV, and perimeter walls.",
                'water_supply': "💧 Water tanks and boreholes are common to ensure reliable water supply.",
                'payment_terms': "💳 Typical payment terms: 1-3 months advance plus security deposit.",
            }
        }
        
        self.price_keywords = {
            'cheap': 150000, 'affordable': 300000, 'budget': 200000,
            'expensive': 2000000, 'luxury': 3000000, 'premium': 1500000,
            'moderate': 800000, 'reasonable': 600000, 'low': 100000,
            'very_cheap': 80000, 'very_expensive': 5000000
        }
        
        self.property_type_keywords = {
            'hostel': 'hostel', 'apartment': 'apartment', 'house': 'house',
            'studio': 'studio', 'flat': 'flat', 'bedsitter': 'bedsitter',
            'single_room': 'single_room', 'double_room': 'double_room',
            'self_contained': 'self_contained', 'boys_quarters': 'boys_quarters',
            'servants_quarters': 'servants_quarters', 'shared_room': 'shared_room',
            'commercial': 'commercial', 'office': 'office', 'pg': 'paying_guest'
        }
        
        self.uganda_districts = [
            'kampala', 'wakiso', 'mukono', 'jinja', 'mbale', 'gulu', 'lira', 'masaka',
            'mbarara', 'arua', 'fort_portal', 'hoima', 'iganga', 'kabale', 'kasese',
            'entebbe', 'kira', 'muyenga', 'ntinda', 'bugolobi', 'kololo', 'nakasero',
            'wandegeya', 'kikoni', 'bwaise', 'kawempe', 'makindye', 'rubaga', 'nakawa',
            'buikwe', 'bugema', 'kangulumira', 'nyenga', 'jinga'
        ]
        
        self.university_areas = {
            'makerere': ['wandegeya', 'kikoni', 'bweyogerere'],
            'kyambogo': ['kira', 'naguru', 'bweyogerere'],
            'ucu': ['mukono', 'seeta', 'naguru'],
            'mbarara': ['mbarara', 'kashaka', 'kikoni'],
            'gulu': ['gulu', 'layibi', 'pece'],
            'must': ['mbarara', 'kashaka'],
            'bugema': ['bugema', 'buikwe', 'kangulumira', 'nyenga', 'jinga']
        }

    def process_message(self, user_message, user=None):
        """
        Main method to process user message and generate AI response
        """
        try:
            # Step 1: Detect intent
            intent = self.detect_intent(user_message)
            
            # Step 2: Extract entities and parameters
            entities = self.extract_entities(user_message)
            
            # Step 3: Generate response based on intent
            if intent == 'property_search':
                return self.handle_property_search(user_message, entities)
            elif intent == 'booking_help':
                return self.handle_booking_help(user_message, entities)
            elif intent == 'pricing_inquiry':
                return self.handle_pricing_inquiry(user_message, entities)
            elif intent == 'availability_check':
                return self.handle_availability_check(user_message, entities)
            elif intent == 'amenities_inquiry':
                return self.handle_amenities_inquiry(user_message, entities)
            elif intent == 'location_inquiry':
                return self.handle_location_inquiry(user_message, entities)
            else:
                return self.handle_faq(user_message, entities)
                
        except Exception as e:
            return {
                'response': 'I apologize, but I encountered an error processing your request. Please try again or contact support.',
                'properties': [],
                'intent': 'error',
                'error': str(e)
            }

    def detect_intent(self, message):
        """
        Detect the user's intent based on message content
        """
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return 'faq'

    def extract_entities(self, message):
        """
        Extract key entities from user message
        """
        entities = {
            'location': [],
            'price_max': None,
            'price_min': None,
            'property_type': None,
            'amenities': [],
            'keywords': []
        }
        
        message_lower = message.lower()
        
        # Extract price information - updated for UGX and Uganda format
        price_pattern = r'(?:ugx\s*[\d,]+|[\d,]+\s*(?:ugx|shillings?|k)|\$[\d,]+|[\d,]+(?:k|thousand|m|million))'
        price_matches = re.findall(price_pattern, message_lower)
        if price_matches:
            for match in price_matches:
                # Convert various price formats to UGX numbers
                price_str = match.replace(',', '').replace('ugx', '').replace('shillings', '').replace('$', '')
                if 'k' in price_str.lower():
                    price = int(float(price_str.lower().replace('k', '')) * 1000)
                elif 'm' in price_str.lower():
                    price = int(float(price_str.lower().replace('m', '')) * 1000000)
                else:
                    price = int(price_str)
                
                # Convert USD to UGX (approximate rate 1 USD = 3800 UGX)
                if '$' in match.lower() and 'ugx' not in match.lower():
                    price = price * 3800
                    
                if 'under' in message_lower or 'less than' in message_lower or 'below' in message_lower:
                    entities['price_max'] = price
                elif 'over' in message_lower or 'above' in message_lower or 'more than' in message_lower:
                    entities['price_min'] = price
                else:
                    entities['price_max'] = price
        
        # Extract price keywords
        for keyword, price in self.price_keywords.items():
            if keyword in message_lower:
                if entities['price_max'] is None:
                    entities['price_max'] = price
        
        # Extract property type
        for keyword, prop_type in self.property_type_keywords.items():
            if keyword in message_lower:
                entities['property_type'] = prop_type
                break
        
        # Extract location (Uganda districts, universities, landmarks, areas)
        for district in self.uganda_districts:
            if district in message_lower:
                entities['location'].append(district)
        
        # Check for university areas
        for university, areas in self.university_areas.items():
            if university in message_lower:
                entities['location'].append(university)
                entities['location'].extend(areas)
        
        # General location keywords
        general_locations = [
            'campus', 'university', 'college', 'school', 'hospital',
            'city centre', 'downtown', 'cbd', 'industrial area', 'town'
        ]
        
        for location in general_locations:
            if location in message_lower:
                entities['location'].append(location)
        
        # Extract amenities - updated for Uganda
        amenities = [
            'wifi', 'parking', 'swimming', 'pool', 'gym', 'fitness',
            'security', 'cctv', 'aircon', 'ac', 'balcony', 'kitchen',
            'laundry', 'study', 'library', 'cable', 'tv', 'internet',
            'generator', 'solar', 'water tank', 'borehole', 'fence',
            'warden', 'meals', 'prayer room', 'common room', 'tv room'
        ]
        
        for amenity in amenities:
            if amenity in message_lower:
                entities['amenities'].append(amenity)
        
        return entities

    def handle_property_search(self, message, entities):
        """
        Handle property search requests
        """
        # Build query
        queryset = Property.objects.filter(is_active=True, is_approved=True)
        
        # Apply filters based on entities
        if entities['price_max']:
            queryset = queryset.filter(rent_per_month__lte=entities['price_max'])
        
        if entities['property_type']:
            queryset = queryset.filter(property_type__icontains=entities['property_type'])
        
        if entities['location']:
            location_filter = Q()
            for loc in entities['location']:
                location_filter |= (
                    Q(district__icontains=loc) |
                    Q(village__icontains=loc) |
                    Q(county__icontains=loc) |
                    Q(description__icontains=loc) |
                    Q(nearby_landmarks__icontains=loc)
                )
            queryset = queryset.filter(location_filter)
        
        # Execute query
        properties = list(queryset[:10])  # Limit to 10 results
        
        # Generate enhanced response using real estate language model
        if properties:
            property_list = []
            for prop in properties:
                property_list.append({
                    'id': prop.id,
                    'name': prop.name,
                    'type': prop.property_type,
                    'location': f"{prop.village or prop.district}, {prop.district}",
                    'price': float(prop.rent_per_month),
                    'description': prop.description[:100] + '...' if len(prop.description) > 100 else prop.description,
                    'image': prop.images.first().image.url if prop.images.exists() else None,
                    'amenities': self.extract_amenities_from_description(prop.description),
                    'price_range': self.categorize_price(float(prop.rent_per_month)),
                    'uganda_specifics': self.get_uganda_specific_info(prop)
                })
            
            response = f"I found {len(properties)} properties matching your criteria."
            
            return {
                'response': enhanced_response,
                'properties': property_list,
                'intent': 'property_search',
                'uganda_insights': self.get_uganda_market_insights(entities),
                'suggestions': self.generate_real_estate_suggestions(entities, properties),
                'market_tips': self.get_uganda_rental_tips()
            }
        else:
            response = "I couldn't find any properties matching your criteria. "
            if entities['price_max']:
                response += f"Try adjusting your budget above UGX {entities['price_max']:,}. "
            if entities['location']:
                response += f"Consider trying different areas near {', '.join(entities['location'])}. "
            response += "Would you like me to search with different criteria?"
            
            return {
                'response': response,
                'properties': [],
                'intent': 'property_search',
                'total_results': 0
            }

    def handle_booking_help(self, message, entities):
        """
        Handle booking process inquiries
        """
        response = """
        I can help you with the booking process! Here's how it works:

        1. **Search & Select**: Browse properties and choose your preferred room
        2. **Check Availability**: Verify your desired dates are available
        3. **Book Online**: Submit your booking request with necessary details
        4. **Upload Documents**: Provide ID and verification documents
        5. **Make Payment**: Pay the required amount (rent + deposit)
        6. **Receive Confirmation**: Get your booking confirmation via email

        **Required Documents:**
        - National ID or Passport
        - Proof of income (for long-term stays)
        - Passport photo

        Would you like me to help you find available properties or explain any specific step?
        """
        
        return {
            'response': response,
            'properties': [],
            'intent': 'booking_help'
        }

    def handle_pricing_inquiry(self, message, entities):
        """
        Handle pricing-related inquiries
        """
        # Get average prices by property type
        pricing_data = {}
        property_types = ['hostel', 'apartment', 'house', 'studio']
        
        for prop_type in property_types:
            avg_price = Property.objects.filter(
                property_type__icontains=prop_type,
                is_active=True,
                is_approved=True
            ).aggregate(avg_price=models.Avg('rent_per_month'))['avg_price']
            
            if avg_price:
                pricing_data[prop_type] = float(avg_price)
        
        response = "Here are the average monthly prices in Kampala:\n\n"
        for prop_type, price in pricing_data.items():
            response += f"• {prop_type.title()}: ${price:.0f}\n"
        
        response += "\nPrices vary based on location, amenities, and season. Would you like me to show you specific properties within your budget?"
        
        return {
            'response': response,
            'properties': [],
            'intent': 'pricing_inquiry',
            'pricing_data': pricing_data
        }

    def handle_availability_check(self, message, entities):
        """
        Handle availability inquiries
        """
        response = """
        To check availability, I'll need:
        - Your preferred move-in date
        - Duration of stay
        - Property or area preference
        
        You can say something like: "Check availability for a 3-month stay starting next month near Makerere"

        Most properties require:
        - Minimum 1 month stay
        - Advance booking (1-2 weeks)
        - Security deposit (1 month's rent)

        Would you like me to help you check specific availability?
        """
        
        return {
            'response': response,
            'properties': [],
            'intent': 'availability_check'
        }

    def handle_amenities_inquiry(self, message, entities):
        """
        Handle amenities-related inquiries
        """
        common_amenities = [
            "High-speed WiFi", "24/7 Security", "Parking Space",
            "Clean Water", "Electricity Backup", "Laundry Services",
            "Study Areas", "Kitchen Access", "TV Lounge", "Cleaning Services"
        ]
        
        response = "Most of our properties include these standard amenities:\n\n"
        for amenity in common_amenities:
            response += f"✓ {amenity}\n"
        
        if entities['amenities']:
            response += f"\nYou specifically asked about: {', '.join(entities['amenities'])}. "
            response += "I can help you find properties with these specific amenities. Would you like me to search for them?"
        
        return {
            'response': response,
            'properties': [],
            'intent': 'amenities_inquiry'
        }

    def handle_location_inquiry(self, message, entities):
        """
        Handle location-related inquiries
        """
        if entities['location']:
            location = entities['location'][0]
            properties = Property.objects.filter(
                Q(city__icontains=location) | Q(locality__icontains=location),
                is_active=True,
                is_approved=True
            )[:5]
            
            if properties:
                response = f"I found {len(properties)} properties in/near {location.title()}:\n\n"
                for prop in properties:
                    response += f"• {prop.name} - ${prop.rent_per_month}/month\n"
                    response += f"  {prop.locality}, {prop.city}\n\n"
                
                return {
                    'response': response,
                    'properties': [{'id': p.id, 'name': p.name, 'price': float(p.rent_per_month)} for p in properties],
                    'intent': 'location_inquiry'
                }
            else:
                return {
                    'response': f"I couldn't find any properties in/near {location.title()}. Try searching for a different area.",
                    'properties': [],
                    'intent': 'location_inquiry'
                }
        else:
            response = """
            I can help you find properties in various locations! Popular areas include:
            
            **Near Universities:**
            - Makerere University area
            - Kyambogo University vicinity
            - Kampala International University
            
            **City Areas:**
            - City Centre / CBD
            - Nakawa
            - Makindye
            - Kawempe
            
            **Suburban Areas:**
            - Entebbe Road
            - Jinja Road
            - Mbarara Road
            
            Which area are you interested in?
            """
            
            return {
                'response': response,
                'properties': [],
                'intent': 'location_inquiry'
            }

    def handle_faq(self, message, entities):
        """
        Handle general FAQ and other inquiries
        """
        faq_responses = {
            'payment': """
            **Payment Options:**
            - Mobile Money (MTN, Airtel)
            - Bank Transfer
            - Cash (at office)
            - Credit/Debit Card (coming soon)
            
            **Payment Schedule:**
            - 1st month + deposit upfront
            - Monthly payments thereafter
            - Deposit refundable at checkout
            """,
            
            'requirements': """
            **Booking Requirements:**
            - Valid National ID/Passport
            - Passport photo
            - Contact person details
            - Proof of income (for 6+ months stay)
            
            **Age Requirement:**
            - Minimum 18 years old
            - Under 18 needs guardian consent
            """,
            
            'cancellation': """
            **Cancellation Policy:**
            - 7+ days before: Full refund minus 10% fee
            - 3-6 days before: 50% refund
            - Less than 3 days: No refund
            - Medical emergencies: Full refund with proof
            """,
            
            'contact': """
            **Contact Information:**
            📞 Phone: +256 123 456 789
            📧 Email: info@perfecthome.ug
            🏢 Office: Kampala City Centre, Building 123
            
            **Working Hours:**
            Monday - Friday: 8AM - 6PM
            Saturday: 9AM - 4PM
            Sunday: Closed
            """
        }
        
        message_lower = message.lower()
        
        if 'payment' in message_lower or 'pay' in message_lower:
            response = faq_responses['payment']
        elif 'requirement' in message_lower or 'need' in message_lower or 'document' in message_lower:
            response = faq_responses['requirements']
        elif 'cancel' in message_lower or 'refund' in message_lower:
            response = faq_responses['cancellation']
        elif 'contact' in message_lower or 'phone' in message_lower or 'email' in message_lower:
            response = faq_responses['contact']
        else:
            response = """
            I'm here to help! I can assist you with:
            
            🔍 **Property Search** - Find your perfect home
            📅 **Booking Help** - Guide you through the process
            💰 **Pricing Info** - Understand costs and budgets
            📍 **Location Details** - Find properties in specific areas
            🏠 **Amenities** - Learn about available facilities
            ❓ **General Questions** - Any other inquiries
            
            What would you like to know more about?
            """
        
        return {
            'response': response,
            'properties': [],
            'intent': 'faq'
        }

    def generate_real_estate_response(self, properties, entities):
        """Generate specialized real estate responses"""
        response = f"🏠 I found {len(properties)} amazing properties in Uganda for you!\n\n"
        
        if entities['location']:
            response += f"📍 **Location**: Near {', '.join(entities['location'])}\n"
        
        if entities['price_max']:
            response += f"💰 **Budget**: Under UGX {entities['price_max']:,}/month\n"
        
        response += "\n**Featured Properties:**\n"
        for i, prop in enumerate(properties[:3], 1):
            response += f"\n{i}. **{prop.name}** - {prop.property_type}\n"
            response += f"   📍 {prop.village or prop.district}, {prop.district}\n"
            response += f"   💵 UGX {prop.rent_per_month:,}/month\n"
            
            # Add Uganda-specific insights
            amenities = self.extract_amenities_from_description(prop.description)
            if amenities:
                response += f"   ✨ {', '.join(amenities[:3])}\n"
        
        response += f"\n🎯 **Uganda Market Tip**: {self.get_uganda_rental_tips()}"
        
        return response

    def extract_amenities_from_description(self, description):
        """Extract amenities from property description"""
        amenities = []
        common_amenities = self.real_estate_knowledge['uganda_property_market']['common_amenities']
        
        desc_lower = description.lower()
        for amenity in common_amenities:
            if any(word in desc_lower for word in amenity.lower().split()):
                amenities.append(amenity)
        
        return amenities[:5]  # Return top 5 amenities

    def categorize_price(self, price):
        """Categorize property price for Uganda market"""
        if price <= 150000:
            return "Budget-Friendly"
        elif price <= 300000:
            return "Affordable"
        elif price <= 600000:
            return "Mid-Range"
        elif price <= 1000000:
            return "Premium"
        else:
            return "Luxury"

    def get_uganda_specific_info(self, property):
        """Get Uganda-specific property information"""
        info = {
            'power_backup': 'generator' in property.description.lower() or 'solar' in property.description.lower(),
            'security': any(word in property.description.lower() for word in ['security', 'guard', 'cctv']),
            'water_supply': any(word in property.description.lower() for word in ['tank', 'borehole', 'water']),
            'parking': 'parking' in property.description.lower()
        }
        return info

    def get_uganda_market_insights(self, entities):
        """Provide Uganda-specific market insights"""
        insights = []
        
        if entities['location']:
            location = entities['location'][0].lower()
            if 'kampala' in location:
                insights.append("Kampala has the highest rental demand in Uganda")
            elif 'makerere' in location:
                insights.append("Makerere area is perfect for students - many hostels available")
            elif 'entebbe' in location:
                insights.append("Entebbe offers peaceful living near the airport")
        
        if entities['price_max'] and entities['price_max'] <= 200000:
            insights.append("Budget properties get rented quickly - act fast!")
        
        return insights

    def generate_real_estate_suggestions(self, entities, properties):
        """Generate contextual suggestions for real estate"""
        suggestions = []
        
        if properties:
            suggestions.append("📞 Would you like me to help you contact the property owners?")
            suggestions.append("📅 Need help with the booking process?")
        
        if entities['price_max']:
            suggestions.append(f"💡 Consider properties slightly above UGX {entities['price_max']:,} for better amenities")
        
        if not entities['location']:
            suggestions.append("🗺️ Want to explore properties in specific areas like Kampala, Entebbe, or Jinja?")
        
        suggestions.append("🔍 Ask me about security, power backup, or water supply - crucial for Uganda living!")
        
        return suggestions[:4]

    def get_uganda_rental_tips(self):
        """Provide Uganda-specific rental tips"""
        tips = [
            "Always ask about generator backup - power can be unreliable",
            "Check water supply - tanks and boreholes are common solutions",
            "Security is important - look for properties with guards and CCTV",
            "Most landlords require 2-3 months advance payment plus deposit",
            "Negotiate prices - most landlords are flexible, especially for long-term leases"
        ]
        
        import random
        return random.choice(tips)

# Singleton instance
ai_service = AIService()
