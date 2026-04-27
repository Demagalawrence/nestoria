import re
import json
from decimal import Decimal
from django.db.models import Q, Avg
from properties.models import Property, Room
from bookings.models import Booking
from datetime import datetime, timedelta

class AIService:
    """
    Main AI Service for handling user queries and generating intelligent responses
    """
    
    def __init__(self):
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
            ]
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
        
        # Generate response
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
                    'image': prop.images.first().image.url if prop.images.exists() else None
                })
            
            response = f"I found {len(properties)} properties matching your criteria."
            if entities['price_max']:
                response += f" All are under UGX {entities['price_max']:,} per month."
            if entities['location']:
                response += f" Located near {', '.join(entities['location'])}."
            
            return {
                'response': response,
                'properties': property_list,
                'intent': 'property_search',
                'total_results': len(properties)
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

# Singleton instance
ai_service = AIService()
