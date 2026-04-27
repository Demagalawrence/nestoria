from decimal import Decimal
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from properties.models import Property, Room
from bookings.models import Booking
from .services import AIService

class TenantAIService(AIService):
    """
    Enhanced AI Service specifically for general tenant accommodation
    """
    
    def __init__(self):
        super().__init__()
        # Add tenant-specific intent patterns
        self.intent_patterns.update({
            'family_accommodation': [
                r'family.*house', r'kids', r'children', r'married.*couple',
                r'family.*apartment', r'bedrooms.*for.*family', r'spacious.*family',
                r'parents.*children', r'school.*district', r'family.*home'
            ],
            'professional_housing': [
                r'working.*professional', r'young.*professional', r'career',
                r'executive', r'working.*adult', r'professional.*apartment',
                r'downtown.*apartment', r'city.*center', r'close.*work'
            ],
            'long_term_rental': [
                r'long.*term', r'yearly', r'annual', r'six.*months',
                r'permanent', r'rent.*year', r'extended.*stay',
                r'lease.*agreement', r'contract'
            ],
            'furnished_apartment': [
                r'furnished', r'fully.*furnished', r'sofa', 'bed',
                r'kitchen.*appliances', r'ready.*move', r'tv.*included',
                r'wardrobe', 'dining', 'washing.*machine'
            ],
            'pet_friendly': [
                r'pet', r'dog', 'cat', r'animal', r'pet.*friendly',
                r'allow.*pets', r'pets.*allowed', r'pet.*policy'
            ],
            'parking_required': [
                r'parking', r'car', r'vehicle', r'garage', r'parking.*space',
                r'secure.*parking', r'car.*parking', r'vehicle.*storage'
            ],
            'tenant_support': [
                r'tenant.*rights', r'landlord', r'rental.*agreement',
                r'tenant.*support', r'legal.*help', r'dispute', r'maintenance',
                r'repair', r'contract', r'lease'
            ],
            'availability_validation': [
                r'full.*booked', r'no.*rooms', r'fully.*occupied',
                r'all.*taken', r'no.*vacancy', r'fully.*booked',
                r'rooms.*full', r'apartment.*full', r'available.*rooms',
                r'vacancy.*check', r'room.*status', r'booking.*confirmed'
            ]
        })
        
        # Tenant budget ranges (different from students)
        self.tenant_budget_ranges = {
            'budget': {'min': 200, 'max': 400, 'description': 'Budget-friendly apartments'},
            'standard': {'min': 400, 'max': 700, 'description': 'Standard quality apartments'},
            'comfortable': {'min': 700, 'max': 1200, 'description': 'Comfortable modern apartments'},
            'premium': {'min': 1200, 'max': 2000, 'description': 'Premium and luxury apartments'},
            'luxury': {'min': 2000, 'max': 5000, 'description': 'High-end luxury housing'}
        }
        
        # Tenant amenities priority
        self.tenant_amenities_priority = [
            'parking', 'security', 'wifi', 'kitchen', 'laundry', 'aircon',
            'balcony', 'storage', 'elevator', 'backup', 'gym', 'pool'
        ]

    def process_message(self, user_message, user=None):
        """
        Enhanced processing with tenant-specific features
        """
        try:
            # Detect if this is a tenant-specific query
            is_tenant_query = self.is_tenant_query(user_message)
            
            # Get tenant profile if available
            tenant_profile = self.get_tenant_profile(user) if user else None
            
            # Detect intent
            intent = self.detect_intent(user_message)
            
            # Extract entities
            entities = self.extract_entities(user_message)
            
            # Enhance entities with tenant profile data
            if tenant_profile:
                entities = self.enhance_entities_with_tenant_profile(entities, tenant_profile)
            
            # Route to appropriate handler
            if intent == 'family_accommodation':
                return self.handle_family_accommodation(user_message, entities, tenant_profile)
            elif intent == 'professional_housing':
                return self.handle_professional_housing(user_message, entities, tenant_profile)
            elif intent == 'long_term_rental':
                return self.handle_long_term_rental(user_message, entities, tenant_profile)
            elif intent == 'furnished_apartment':
                return self.handle_furnished_apartment(user_message, entities, tenant_profile)
            elif intent == 'pet_friendly':
                return self.handle_pet_friendly(user_message, entities, tenant_profile)
            elif intent == 'parking_required':
                return self.handle_parking_required(user_message, entities, tenant_profile)
            elif intent == 'tenant_support':
                return self.handle_tenant_support(user_message, entities, tenant_profile)
            elif intent == 'availability_validation':
                return self.handle_availability_validation(user_message, entities, tenant_profile)
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

    def is_tenant_query(self, message):
        """Check if the query is tenant-related (not student)"""
        tenant_keywords = [
            'family', 'married', 'children', 'kids', 'working', 'professional',
            'career', 'executive', 'downtown', 'city', 'apartment', 'house',
            'furnished', 'parking', 'pet', 'long term', 'yearly', 'lease'
        ]
        
        student_keywords = [
            'student', 'university', 'campus', 'college', 'hostel',
            'dormitory', 'makerere', 'kyambogo', 'semester'
        ]
        
        message_lower = message.lower()
        
        # If student keywords present, it's likely a student query
        if any(keyword in message_lower for keyword in student_keywords):
            return False
        
        # If tenant keywords present, it's a tenant query
        return any(keyword in message_lower for keyword in tenant_keywords)

    def get_tenant_profile(self, user):
        """Get tenant-specific profile information"""
        if not user:
            return None
            
        # Get user's booking history to understand preferences
        previous_bookings = Booking.objects.filter(user=user).order_by('-created_at')[:10]
        
        profile = {
            'previous_locations': [],
            'average_budget': None,
            'preferred_property_types': [],
            'rental_duration': 'medium',  # short, medium, long
            'family_status': 'single',    # single, couple, family
            'has_pets': False,
            'needs_parking': False,
            'prefers_furnished': False
        }
        
        if previous_bookings.exists():
            total_spent = sum(b.final_amount for b in previous_bookings if b.final_amount)
            if previous_bookings.count() > 0:
                profile['average_budget'] = total_spent / previous_bookings.count()
            
            # Calculate average stay duration
            durations = []
            for booking in previous_bookings:
                if booking.start_date and booking.end_date:
                    duration = (booking.end_date - booking.start_date).days
                    durations.append(duration)
            
            if durations:
                avg_duration = sum(durations) / len(durations)
                if avg_duration < 90:
                    profile['rental_duration'] = 'short'
                elif avg_duration < 365:
                    profile['rental_duration'] = 'medium'
                else:
                    profile['rental_duration'] = 'long'
            
            # Extract preferences
            for booking in previous_bookings:
                if booking.rental_property.city not in profile['previous_locations']:
                    profile['previous_locations'].append(booking.rental_property.city)
                
                if booking.rental_property.property_type not in profile['preferred_property_types']:
                    profile['preferred_property_types'].append(booking.rental_property.property_type)
        
        return profile

    def enhance_entities_with_tenant_profile(self, entities, tenant_profile):
        """Enhance extracted entities with tenant profile data"""
        if not tenant_profile:
            return entities
            
        # Use tenant's average budget if no price specified
        if not entities['price_max'] and tenant_profile['average_budget']:
            entities['price_max'] = tenant_profile['average_budget']
        
        # Add tenant amenities to amenities list
        tenant_amenities = ['parking', 'security', 'wifi', 'kitchen', 'laundry']
        for amenity in tenant_amenities:
            if amenity not in entities['amenities']:
                entities['amenities'].append(amenity)
        
        # Add tenant preferences
        entities['rental_duration'] = tenant_profile['rental_duration']
        entities['family_status'] = tenant_profile['family_status']
        
        return entities

    def handle_family_accommodation(self, message, entities, tenant_profile):
        """Handle family-specific accommodation searches"""
        
        # Build family-friendly query
        queryset = Property.objects.filter(is_active=True, is_approved=True)
        
        # Apply budget filter
        if entities['price_max']:
            queryset = queryset.filter(rent_per_month__lte=entities['price_max'])
        
        # Filter for family-friendly properties
        family_filter = Q(
            Q(property_type__in=['apartment', 'house']) |
            Q(description__icontains__in=['family', 'spacious', 'bedrooms']) |
            Q(amenities__icontains__in=['family', 'children', 'playground'])
        )
        queryset = queryset.filter(family_filter)
        
        # Prioritize properties with multiple bedrooms
        queryset = queryset.filter(total_rooms__gte=2)
        
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
        
        # Filter for family amenities
        family_amenities = ['security', 'parking', 'playground', 'garden', 'quiet']
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
                # Calculate family suitability score
                family_score = self.calculate_family_suitability_score(prop, entities)
                
                property_list.append({
                    'id': prop.id,
                    'name': prop.name,
                    'type': prop.property_type,
                    'location': f"{prop.locality}, {prop.city}",
                    'price': float(prop.rent_per_month),
                    'description': prop.description[:100] + '...' if len(prop.description) > 100 else prop.description,
                    'image': prop.images.first().image.url if prop.images.exists() else None,
                    'family_score': family_score,
                    'family_features': self.get_family_features(prop),
                    'bedrooms': prop.total_rooms,
                    'school_district': self.check_school_district(prop),
                    'family_amenities': self.get_family_amenities(prop)
                })
            
            # Sort by family suitability score
            property_list.sort(key=lambda x: x['family_score'], reverse=True)
            
            response = f"I found {len(properties)} great family accommodations for you! 👨‍👩‍👧‍👦\n\n"
            
            if entities['price_max']:
                response += f"**Budget:** Up to ${entities['price_max']}/month\n\n"
            
            response += "Here are the best family-friendly options:\n\n"
            
            for i, prop in enumerate(property_list[:3], 1):
                response += f"{i}. **{prop['name']}** - ${prop['price']}/month\n"
                response += f"   📍 {prop['location']}\n"
                response += f"   🏠 {prop['bedrooms']} bedrooms\n"
                response += f"   ⭐ Family Score: {prop['family_score']}/10\n"
                response += f"   🎒 School District: {prop['school_district']}\n"
                response += f"   👨‍👩‍👧‍👦 Family Features: {', '.join(prop['family_features'])}\n\n"
            
            response += "All properties are family-friendly with security, parking, and good school access. "
            response += "Would you like to schedule a viewing or get more details about any property?"
            
            return {
                'response': response,
                'properties': property_list,
                'intent': 'family_accommodation',
                'total_results': len(properties),
                'family_focused': True
            }
        else:
            advice = self.get_family_accommodation_advice(entities)
            
            return {
                'response': f"I couldn't find family accommodations matching your criteria. {advice}",
                'properties': [],
                'intent': 'family_accommodation',
                'total_results': 0,
                'family_advice': True
            }

    def handle_professional_housing(self, message, entities, tenant_profile):
        """Handle professional/working adult housing searches"""
        
        # Build professional housing query
        queryset = Property.objects.filter(is_active=True, is_approved=True)
        
        # Apply budget filter
        if entities['price_max']:
            queryset = queryset.filter(rent_per_month__lte=entities['price_max'])
        
        # Filter for professional-friendly properties
        professional_filter = Q(
            Q(property_type__in=['apartment', 'condominium', 'studio']) |
            Q(description__icontains__in=['modern', 'executive', 'professional', 'downtown']) |
            Q(target_audience='professional')
        )
        queryset = queryset.filter(professional_filter)
        
        # Prioritize city center and business areas
        business_areas = ['city centre', 'cbd', 'downtown', 'nakasero', 'kololo', 'industrial area']
        area_filter = Q()
        for area in business_areas:
            area_filter |= Q(locality__icontains=area) | Q(city__icontains=area)
        
        if entities['location']:
            for loc in entities['location']:
                area_filter |= Q(locality__icontains=loc) | Q(city__icontains=loc)
        
        queryset = queryset.filter(area_filter)
        
        # Filter for professional amenities
        professional_amenities = ['wifi', 'parking', 'security', 'gym', 'elevator', 'backup']
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
                # Calculate professional suitability score
                professional_score = self.calculate_professional_suitability_score(prop, entities)
                
                property_list.append({
                    'id': prop.id,
                    'name': prop.name,
                    'type': prop.property_type,
                    'location': f"{prop.locality}, {prop.city}",
                    'price': float(prop.rent_per_month),
                    'description': prop.description[:100] + '...' if len(prop.description) > 100 else prop.description,
                    'image': prop.images.first().image.url if prop.images.exists() else None,
                    'professional_score': professional_score,
                    'professional_features': self.get_professional_features(prop),
                    'commute_time': self.estimate_commute_time(prop),
                    'business_district': self.check_business_district(prop),
                    'modern_amenities': self.get_modern_amenities(prop)
                })
            
            # Sort by professional suitability score
            property_list.sort(key=lambda x: x['professional_score'], reverse=True)
            
            response = f"I found {len(properties)} perfect accommodations for working professionals! 💼\n\n"
            
            if entities['price_max']:
                response += f"**Budget:** Up to ${entities['price_max']}/month\n\n"
            
            response += "Here are the best options for professionals:\n\n"
            
            for i, prop in enumerate(property_list[:3], 1):
                response += f"{i}. **{prop['name']}** - ${prop['price']}/month\n"
                response += f"   📍 {prop['location']}\n"
                response += f"   ⭐ Professional Score: {prop['professional_score']}/10\n"
                response += f"   🚗 Commute Time: {prop['commute_time']}\n"
                response += f"   🏢 Business District: {prop['business_district']}\n"
                response += f"   💼 Professional Features: {', '.join(prop['professional_features'])}\n\n"
            
            response += "All properties offer modern amenities perfect for professionals. "
            response += "Would you like to schedule a viewing or get more details?"
            
            return {
                'response': response,
                'properties': property_list,
                'intent': 'professional_housing',
                'total_results': len(properties),
                'professional_focused': True
            }
        else:
            advice = self.get_professional_housing_advice(entities)
            
            return {
                'response': f"I couldn't find professional accommodations matching your criteria. {advice}",
                'properties': [],
                'intent': 'professional_housing',
                'total_results': 0,
                'professional_advice': True
            }

    def handle_long_term_rental(self, message, entities, tenant_profile):
        """Handle long-term rental inquiries"""
        
        response = "I can help you find long-term rental options! 🏠\n\n"
        
        response += "**Long-Term Rental Benefits:**\n"
        response += "💰 **Better Rates**: Monthly discounts for 6+ month leases\n"
        response += "🔒 **Price Stability**: Fixed rent for your lease term\n"
        response += "🏠 **Home Feeling**: Make it truly your own space\n"
        response += "📋 **Legal Protection**: Lease agreement protects both parties\n\n"
        
        response += "**Typical Long-Term Options:**\n\n"
        
        # Find properties available for long-term
        queryset = Property.objects.filter(is_active=True, is_approved=True)
        
        if entities['price_max']:
            queryset = queryset.filter(rent_per_month__lte=entities['price_max'])
        
        # Filter for properties allowing long-term
        long_term_properties = queryset.filter(
            Q(minimum_stay_months__lte=6) | Q(minimum_stay_months__isnull=True)
        )[:5]
        
        if long_term_properties:
            response += "**Available for Long-Term Rental:**\n\n"
            
            for prop in long_term_properties:
                monthly_price = float(prop.rent_per_month)
                yearly_discount = 0.10  # 10% yearly discount
                discounted_monthly = monthly_price * (1 - yearly_discount)
                
                response += f"🏠 **{prop.name}** - {prop.locality}\n"
                response += f"   Regular: ${monthly_price}/month\n"
                response += f"   Yearly: ${discounted_monthly:.0f}/month (Save ${monthly_price * yearly_discount:.0f}/month)\n"
                response += f"   Type: {prop.property_type}\n\n"
        
        response += "**Lease Terms Available:**\n"
        response += "• **6 Months**: 5% discount on monthly rate\n"
        response += "• **12 Months**: 10% discount on monthly rate\n"
        response += "• **24 Months**: 15% discount on monthly rate\n"
        response += "• **Custom**: Negotiable for 3+ years\n\n"
        
        response += "**Requirements for Long-Term Rental:**\n"
        response += "• Valid ID and proof of income\n"
        response += "• Employment contract or business registration\n"
        response += "• Referee contact information\n"
        response += "• 2-month security deposit\n\n"
        
        if entities['price_max']:
            response += f"**Based on your ${entities['price_max']} budget:**\n"
            response += f"• You can access quality apartments and houses\n"
            response += f"• Yearly lease could save you ${entities['price_max'] * 0.10:.0f}/month\n"
            response += f"• Total initial payment: ~${entities['price_max'] * 2} (first month + deposit)\n\n"
        
        response += "Would you like me to show you specific properties available for long-term rental, "
        response += "or do you have questions about lease agreements?"
        
        return {
            'response': response,
            'properties': [
                {
                    'id': p.id,
                    'name': p.name,
                    'price': float(p.rent_per_month),
                    'location': f"{p.locality}, {p.city}",
                    'long_term_available': True
                } for p in long_term_properties
            ],
            'intent': 'long_term_rental',
            'lease_info': True
        }

    def handle_furnished_apartment(self, message, entities, tenant_profile):
        """Handle furnished apartment searches"""
        
        # Build furnished apartment query
        queryset = Property.objects.filter(is_active=True, is_approved=True)
        
        # Filter for furnished properties
        furnished_filter = Q(
            Q(description__icontains__in=['furnished', 'fully furnished', 'ready to move']) |
            Q(amenities__icontains__in=['sofa', 'bed', 'wardrobe', 'dining', 'tv'])
        )
        queryset = queryset.filter(furnished_filter)
        
        # Apply other filters
        if entities['price_max']:
            queryset = queryset.filter(rent_per_month__lte=entities['price_max'])
        
        if entities['location']:
            location_filter = Q()
            for loc in entities['location']:
                location_filter |= (
                    Q(city__icontains=loc) |
                    Q(locality__icontains=loc)
                )
            queryset = queryset.filter(location_filter)
        
        properties = list(queryset[:8])
        
        if properties:
            response = f"I found {len(properties)} furnished apartments ready for you to move in! 🛋️\n\n"
            
            property_list = []
            for prop in properties:
                furnished_items = self.get_furnished_items(prop)
                
                property_list.append({
                    'id': prop.id,
                    'name': prop.name,
                    'type': prop.property_type,
                    'location': f"{prop.locality}, {prop.city}",
                    'price': float(prop.rent_per_month),
                    'description': prop.description[:100] + '...' if len(prop.description) > 100 else prop.description,
                    'image': prop.images.first().image.url if prop.images.exists() else None,
                    'furnished_items': furnished_items,
                    'move_in_ready': True,
                    'savings_estimate': self.calculate_furnishing_savings(prop)
                })
            
            response += "**Furnished Apartments - Move In Ready!**\n\n"
            
            for i, prop in enumerate(property_list[:3], 1):
                response += f"{i}. **{prop['name']}** - ${prop['price']}/month\n"
                response += f"   📍 {prop['location']}\n"
                response += f"   🛋️ Furnished: {', '.join(prop['furnished_items'])}\n"
                response += f"   💰 You save: ~${prop['savings_estimate']} on furniture\n\n"
            
            response += "**Benefits of Furnished Apartments:**\n"
            response += "✅ No furniture purchase needed\n"
            response += "✅ Move in immediately\n"
            response += "✅ Professional interior design\n"
            response += "✅ All essential appliances included\n\n"
            
            response += "Would you like to schedule a viewing or get details about what's included?"
            
            return {
                'response': response,
                'properties': property_list,
                'intent': 'furnished_apartment',
                'total_results': len(properties),
                'furnished': True
            }
        else:
            return {
                'response': "I couldn't find furnished apartments matching your criteria. Would you like me to show you unfurnished options where you can furnish according to your taste?",
                'properties': [],
                'intent': 'furnished_apartment',
                'total_results': 0
            }

    def handle_pet_friendly(self, message, entities, tenant_profile):
        """Handle pet-friendly accommodation searches"""
        
        # Build pet-friendly query
        queryset = Property.objects.filter(is_active=True, is_approved=True, pet_friendly=True)
        
        # Apply other filters
        if entities['price_max']:
            queryset = queryset.filter(rent_per_month__lte=entities['price_max'])
        
        if entities['location']:
            location_filter = Q()
            for loc in entities['location']:
                location_filter |= (
                    Q(city__icontains=loc) |
                    Q(locality__icontains=loc)
                )
            queryset = queryset.filter(location_filter)
        
        properties = list(queryset[:8])
        
        if properties:
            response = f"I found {len(properties)} pet-friendly homes for you and your furry friend! 🐕🐈\n\n"
            
            property_list = []
            for prop in properties:
                pet_features = self.get_pet_features(prop)
                
                property_list.append({
                    'id': prop.id,
                    'name': prop.name,
                    'type': prop.property_type,
                    'location': f"{prop.locality}, {prop.city}",
                    'price': float(prop.rent_per_month),
                    'description': prop.description[:100] + '...' if len(prop.description) > 100 else prop.description,
                    'image': prop.images.first().image.url if prop.images.exists() else None,
                    'pet_features': pet_features,
                    'pet_policy': self.get_pet_policy(prop),
                    'pet_deposit': self.get_pet_deposit_info(prop)
                })
            
            response += "**Pet-Friendly Properties:**\n\n"
            
            for i, prop in enumerate(property_list[:3], 1):
                response += f"{i}. **{prop['name']}** - ${prop['price']}/month\n"
                response += f"   📍 {prop['location']}\n"
                response += f"   🐕 Pet Features: {', '.join(prop['pet_features'])}\n"
                response += f"   📋 Pet Policy: {prop['pet_policy']}\n"
                response += f"   💰 Pet Deposit: {prop['pet_deposit']}\n\n"
            
            response += "**Pet-Friendly Benefits:**\n"
            response += "🐕 No need to rehome your beloved pet\n"
            response += "🏠 Spacious areas for pet comfort\n"
            response += "🌳 Nearby parks and walking areas\n"
            response += "🧹 Easy-to-clean flooring\n\n"
            
            response += "Would you like to schedule a visit to see if it's perfect for you and your pet?"
            
            return {
                'response': response,
                'properties': property_list,
                'intent': 'pet_friendly',
                'total_results': len(properties),
                'pet_friendly': True
            }
        else:
            return {
                'response': "I couldn't find pet-friendly accommodations. Many properties have pet restrictions, but I can help you find properties that might consider pets with additional deposits or references. Would you like me to show you those options?",
                'properties': [],
                'intent': 'pet_friendly',
                'total_results': 0
            }

    def handle_parking_required(self, message, entities, tenant_profile):
        """Handle parking requirement searches"""
        
        # Build parking query
        queryset = Property.objects.filter(is_active=True, is_approved=True)
        
        # Filter for properties with parking
        parking_filter = Q(
            Q(has_parking=True) |
            Q(amenities__icontains__in=['parking', 'garage', 'car', 'vehicle'])
        )
        queryset = queryset.filter(parking_filter)
        
        # Apply other filters
        if entities['price_max']:
            queryset = queryset.filter(rent_per_month__lte=entities['price_max'])
        
        if entities['location']:
            location_filter = Q()
            for loc in entities['location']:
                location_filter |= (
                    Q(city__icontains=loc) |
                    Q(locality__icontains=loc)
                )
            queryset = queryset.filter(location_filter)
        
        properties = list(queryset[:8])
        
        if properties:
            response = f"I found {len(properties)} properties with secure parking for your vehicle! 🚗\n\n"
            
            property_list = []
            for prop in properties:
                parking_details = self.get_parking_details(prop)
                
                property_list.append({
                    'id': prop.id,
                    'name': prop.name,
                    'type': prop.property_type,
                    'location': f"{prop.locality}, {prop.city}",
                    'price': float(prop.rent_per_month),
                    'description': prop.description[:100] + '...' if len(prop.description) > 100 else prop.description,
                    'image': prop.images.first().image.url if prop.images.exists() else None,
                    'parking_details': parking_details,
                    'parking_security': self.get_parking_security(prop),
                    'parking_cost': self.get_parking_cost(prop)
                })
            
            response += "**Properties with Secure Parking:**\n\n"
            
            for i, prop in enumerate(property_list[:3], 1):
                response += f"{i}. **{prop['name']}** - ${prop['price']}/month\n"
                response += f"   📍 {prop['location']}\n"
                response += f"   🚗 Parking: {prop['parking_details']}\n"
                response += f"   🔒 Security: {prop['parking_security']}\n"
                response += f"   💰 Cost: {prop['parking_cost']}\n\n"
            
            response += "**Parking Benefits:**\n"
            response += "🔒 24/7 security monitoring\n"
            response += "🚗 Covered parking spaces\n"
            response += "🏠 Easy access to your vehicle\n"
            response += "🛡️ Protection from weather and theft\n\n"
            
            response += "Would you like to schedule a viewing to check the parking facilities?"
            
            return {
                'response': response,
                'properties': property_list,
                'intent': 'parking_required',
                'total_results': len(properties),
                'parking_available': True
            }
        else:
            return {
                'response': "I couldn't find properties with dedicated parking. However, some properties might have street parking or nearby parking facilities. Would you like me to show you those options?",
                'properties': [],
                'intent': 'parking_required',
                'total_results': 0
            }

    def handle_tenant_support(self, message, entities, tenant_profile):
        """Handle tenant support and legal questions"""
        
        response = "I'm here to help you with tenant rights and support! 🏠⚖️\n\n"
        
        if 'rights' in message.lower() or 'legal' in message.lower():
            response += "**Tenant Rights in Uganda:**\n\n"
            response += "🔒 **Right to Quiet Enjoyment**: Landlord cannot disturb your peaceful living\n"
            response += "🏠 **Right to Habitable Property**: Must be safe, clean, and livable\n"
            response += "💰 **Right to Fair Rent**: No arbitrary rent increases during lease term\n"
            response += "🔐 **Right to Privacy**: Landlord must give notice before entering\n"
            response += "📋 **Right to Receipt**: Must receive receipts for all payments\n"
            response += "⚖️ **Right to Dispute Resolution**: Legal process for disputes\n\n"
            
        elif 'landlord' in message.lower() or 'dispute' in message.lower():
            response += "**Dealing with Landlord Issues:**\n\n"
            response += "📞 **Communication First**: Try to resolve issues directly\n"
            response += "📝 **Document Everything**: Keep records of all communications\n"
            response += "📧 **Written Notice**: Give formal written notice for issues\n"
            response += "🏛️ **Legal Aid**: Seek help from Uganda Law Society if needed\n"
            response += "📋 **Lease Agreement**: Review your lease terms carefully\n"
            response += "⏰ **Response Time**: Landlords must respond within reasonable time\n\n"
            
        elif 'maintenance' in message.lower() or 'repair' in message.lower():
            response += "**Maintenance and Repairs:**\n\n"
            response += "🔧 **Landlord Responsibility**: Major repairs and structural issues\n"
            response += "💡 **Tenant Responsibility**: Minor maintenance and cleanliness\n"
            response += "📞 **Report Promptly**: Report issues as soon as they occur\n"
            response += "📝 **Written Requests**: Submit repair requests in writing\n"
            response += "⏰ **Response Time**: Usually 3-7 days for non-emergency repairs\n"
            response += "🚨 **Emergency Repairs**: Must be addressed immediately (24 hours)\n\n"
            
        elif 'contract' in message.lower() or 'lease' in message.lower():
            response += "**Understanding Your Lease Agreement:**\n\n"
            response += "📋 **Key Clauses to Review**:\n"
            response += "• Rent amount and payment schedule\n"
            response += "• Lease duration and renewal terms\n"
            response += "• Security deposit conditions\n"
            response += "• Maintenance responsibilities\n"
            response += "• House rules and restrictions\n"
            response += "• Termination notice periods\n"
            response += "• Utility payment responsibilities\n\n"
            response += "⚠️ **Red Flags to Watch For**:\n"
            response += "• Unusually high deposits\n"
            response += "• Vague maintenance terms\n"
            response += "• Unreasonable restrictions\n"
            response += "• No clear termination process\n\n"
            
        else:
            response += "**How I Can Help You:**\n\n"
            response += "🏠 **Property Issues**: Maintenance, repairs, habitability\n"
            response += "⚖️ **Legal Rights**: Understanding your tenant protections\n"
            response += "🤝 **Landlord Relations**: Communication and dispute resolution\n"
            response += "📋 **Contract Help**: Understanding lease agreements\n"
            response += "💰 **Financial Issues**: Rent disputes, deposit returns\n"
            response += "🔒 **Security**: Safety and security concerns\n\n"
            response += "**Common Tenant Concerns:**\n"
            response += "• Rent increases and notices\n"
            response += "• Security deposit deductions\n"
            response += "• Property maintenance delays\n"
            response += "• Entry without proper notice\n"
            response += "• Utility billing disputes\n"
            response += "• Lease termination issues\n\n"
            
            response += "What specific tenant issue can I help you with today?"
        
        response += "\n**📞 Need Immediate Help?**\n"
        response += "• **Legal Aid**: Uganda Law Society - +256 414 237 191\n"
        response += "• **Tenant Association**: Uganda Tenants Association\n"
        response += "• **Dispute Resolution**: Local Council courts\n"
        response += "• **Emergency**: Property manager or local authorities"
        
        return {
            'response': response,
            'properties': [],
            'intent': 'tenant_support',
            'support_info': True
        }

    def handle_availability_validation(self, message, entities, tenant_profile):
        """Handle availability validation for tenant housing"""
        
        response = "I can help you check real-time availability for any property! 🏠📊\n\n"
        
        # Check if user is asking about specific property
        property_name = self.extract_property_name_from_message(message)
        
        if property_name:
            # Check specific property availability
            availability_info = self.check_property_availability(property_name)
            
            if availability_info['is_full']:
                response += f"**{property_name} Status:** 🔴 FULLY BOOKED\n\n"
                response += f"**Current Occupancy:** {availability_info['occupancy_rate']}%\n"
                response += f"**Next Available:** {availability_info['next_available']}\n\n"
                
                response += "**Alternative Options:**\n"
                response += f"1. **Join Waiting List** - I can add you to {property_name}'s waiting list\n"
                response += f"2. **Find Similar Properties** - Search for nearby alternatives\n"
                response += f"3. **Set Availability Alert** - I'll notify you when units become available\n"
                response += f"4. **Check Different Dates** - Maybe other dates have availability\n\n"
                
                response += "**🔔 What would you prefer?**\n"
                response += "• **Waiting List**: Get notified first when something opens up\n"
                response += "• **Similar Properties**: Find alternatives in same area\n"
                response += "• **Availability Alerts**: Get notifications for your preferred dates\n"
                response += "• **Different Dates**: Check availability for other time periods\n\n"
                
                response += "I can help you with any of these options immediately!"
                
                return {
                    'response': response,
                    'properties': [],
                    'intent': 'availability_validation',
                    'property_status': 'fully_booked',
                    'property_name': property_name,
                    'alternatives_available': True,
                    'waiting_list_available': True
                }
            else:
                response += f"**{property_name} Status:** 🟢 UNITS AVAILABLE\n\n"
                response += f"**Available Units:** {availability_info['available_units']}\n"
                response += f"**Occupancy Rate:** {availability_info['occupancy_rate']}%\n"
                response += f"**Unit Types:** {', '.join(availability_info['unit_types'])}\n\n"
                
                response += "**Ready to View:**\n"
                response += "✅ Units are available for your dates\n"
                response += "✅ I can help you schedule a viewing\n"
                response += "✅ Immediate booking possible\n"
                response += "✅ Tenant-friendly terms available\n\n"
                
                response += "Would you like me to help you book a viewing at " + property_name + "?"
                
                return {
                    'response': response,
                    'properties': availability_info.get('available_properties', []),
                    'intent': 'availability_validation',
                    'property_status': 'available',
                    'property_name': property_name,
                    'ready_to_book': True
                }
        else:
            # General availability check
            response += "**Real-Time Property Availability Check** 🏠📊\n\n"
            response += "I can check availability for any property you're interested in! Just tell me:\n\n"
            response += "**🏠 Property Name**: Which property are you checking?\n"
            response += "**📅 Your Dates**: When do you need to move in?\n"
            response += "**👥 Property Type**: Apartment, house, or studio?\n"
            response += "**👥 Bedrooms**: How many bedrooms do you need?\n"
            response += "**💰 Budget Range**: What's your budget range?\n\n"
            
            response += "**💡 Quick Availability Tips:**\n"
            response += "• **Book Early**: Popular properties fill up quickly\n"
            response += "• **Have Backup Options**: Choose 2-3 alternative properties\n"
            response += "• **Be Flexible**: Different dates increase availability chances\n"
            response += "• **Contact Directly**: Sometimes faster than online booking\n"
            response += "• **Set Alerts**: Get notified for new listings\n\n"
            
            response += "**Example Requests:**\n"
            response += "• \"Check availability at Green Valley Apartments for next month\"\n"
            response += "• \"Is Executive Heights fully booked for September?\"\n"
            response += "• \"Any units available at Urban Lofts for August?\"\n\n"
            
            response += "Which property would you like me to check?"
            
            return {
                'response': response,
                'properties': [],
                'intent': 'availability_validation',
                'general_inquiry': True
            }

    def extract_property_name_from_message(self, message):
        """Extract property name from user message"""
        # Common property name patterns
        property_patterns = {
            'green valley': ['green valley', 'valley apartments'],
            'executive heights': ['executive heights', 'executive heights apartments'],
            'urban lofts': ['urban lofts', 'loft apartments'],
            'city centre apartments': ['city centre', 'cbd apartments'],
            'nakasero heights': ['nakasero heights', 'nakasero apartments'],
            'kololo residence': ['kololo residence', 'kololo apartments'],
            'ntinda gardens': ['ntinda gardens', 'ntinda homes'],
            'muyenga estates': ['muyenga estates', 'muyenga homes']
        }
        
        message_lower = message.lower()
        
        for property, patterns in property_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return property.title()
        
        return None

    def check_property_availability(self, property_name):
        """Check real-time availability for a specific property"""
        # This would ideally connect to a real-time availability system
        # For now, simulate availability checks
        
        import random
        
        # 50% chance property is fully booked (realistic for popular properties)
        is_full = random.choice([True, False, True, False])  # 50% full
        
        if is_full:
            return {
                'is_full': True,
                'occupancy_rate': 100,
                'next_available': self.calculate_next_available_date(),
                'waiting_list_size': random.randint(3, 15),
                'popular_dates': ['September', 'October', 'January']
            }
        else:
            # Simulate partial availability
            available_units = random.randint(1, 6)
            total_units = 15
            occupancy_rate = ((total_units - available_units) / total_units) * 100
            
            return {
                'is_full': False,
                'available_units': available_units,
                'occupancy_rate': round(occupancy_rate, 1),
                'unit_types': self.get_available_unit_types(available_units),
                'price_range': '$800-2000',
                'available_properties': self.generate_available_properties(property_name, available_units)
            }

    def get_available_unit_types(self, available_units):
        """Get types of units available"""
        unit_types = []
        
        if available_units >= 3:
            unit_types.extend(['1-Bedroom', '2-Bedroom'])
        if available_units >= 2:
            unit_types.append('Studio')
        if available_units >= 1:
            unit_types.append('3-Bedroom')
        
        return unit_types

    def generate_available_properties(self, property_name, available_units):
        """Generate mock available properties for the property"""
        properties = []
        
        for i in range(min(available_units, 3)):
            unit_types = ['1-Bedroom', '2-Bedroom', 'Studio', '3-Bedroom']
            prices = [800, 1200, 1500, 1800, 2000]
            
            properties.append({
                'id': i + 1,
                'name': f"{property_name} - Unit {i + 1}",
                'type': random.choice(unit_types),
                'price': random.choice(prices),
                'available_from': 'Next Month',
                'unit_features': ['Parking', 'Security', 'Modern Kitchen', 'WiFi']
            })
        
        return properties

    # Helper methods for tenant-specific scoring and features
    def calculate_family_suitability_score(self, property, entities):
        """Calculate family suitability score"""
        score = 5.0  # Base score
        
        # Add points for bedrooms
        if property.total_rooms >= 3:
            score += 2.0
        elif property.total_rooms >= 2:
            score += 1.5
        
        # Add points for family amenities
        family_amenities = ['security', 'parking', 'playground', 'garden', 'quiet']
        description_lower = (property.description + ' ' + property.amenities).lower()
        
        for amenity in family_amenities:
            if amenity in description_lower:
                score += 0.3
        
        # Add points for location
        if 'school' in description_lower or 'educational' in description_lower:
            score += 1.0
        
        return min(10.0, round(score, 1))

    def calculate_professional_suitability_score(self, property, entities):
        """Calculate professional suitability score"""
        score = 5.0  # Base score
        
        # Add points for modern amenities
        professional_amenities = ['wifi', 'gym', 'elevator', 'backup', 'security', 'parking']
        description_lower = (property.description + ' ' + property.amenities).lower()
        
        for amenity in professional_amenities:
            if amenity in description_lower:
                score += 0.4
        
        # Add points for location
        business_areas = ['city centre', 'cbd', 'downtown', 'nakasero', 'kololo']
        for area in business_areas:
            if area in description_lower:
                score += 1.5
                break
        
        # Add points for property type
        if property.property_type in ['apartment', 'condominium']:
            score += 1.0
        
        return min(10.0, round(score, 1))

    def get_family_features(self, property):
        """Get family-specific features"""
        features = []
        description_lower = (property.description + ' ' + property.amenities).lower()
        
        family_keywords = {
            'security': '24/7 Security',
            'parking': 'Secure Parking',
            'playground': 'Children Playground',
            'garden': 'Garden Area',
            'quiet': 'Quiet Environment',
            'spacious': 'Spacious Layout',
            'storage': 'Extra Storage'
        }
        
        for keyword, feature in family_keywords.items():
            if keyword in description_lower:
                features.append(feature)
        
        return features[:5]

    def get_professional_features(self, property):
        """Get professional-specific features"""
        features = []
        description_lower = (property.description + ' ' + property.amenities).lower()
        
        professional_keywords = {
            'wifi': 'High-Speed WiFi',
            'gym': 'Fitness Center',
            'elevator': 'Elevator Access',
            'backup': 'Power Backup',
            'security': '24/7 Security',
            'parking': 'Dedicated Parking',
            'modern': 'Modern Design',
            'executive': 'Executive Finish'
        }
        
        for keyword, feature in professional_keywords.items():
            if keyword in description_lower:
                features.append(feature)
        
        return features[:5]

    def check_school_district(self, property):
        """Check if property is in a good school district"""
        description_lower = (property.description + ' ' + property.locality + ' ' + property.city).lower()
        
        school_keywords = ['school', 'educational', 'campus', 'university', 'college']
        for keyword in school_keywords:
            if keyword in description_lower:
                return "Excellent"
        
        return "Good Access"

    def check_business_district(self, property):
        """Check if property is in business district"""
        description_lower = (property.description + ' ' + property.locality + ' ' + property.city).lower()
        
        business_areas = {
            'city centre': 'Central Business District',
            'cbd': 'Central Business District',
            'nakasero': 'Prime Business Area',
            'kololo': 'Upscale Business Area',
            'industrial': 'Industrial Zone'
        }
        
        for area, district in business_areas.items():
            if area in description_lower:
                return district
        
        return "Residential Area"

    def estimate_commute_time(self, property):
        """Estimate commute time to business areas"""
        description_lower = (property.locality + ' ' + property.city).lower()
        
        if any(area in description_lower for area in ['city centre', 'cbd', 'nakasero']):
            return "Walking Distance"
        elif any(area in description_lower for area in ['kololo', 'nakawa']):
            return "5-15 minutes"
        else:
            return "15-30 minutes"

    def get_modern_amenities(self, property):
        """Get modern amenities for professionals"""
        amenities = []
        description_lower = (property.description + ' ' + property.amenities).lower()
        
        modern_features = ['aircon', 'heating', 'smart', 'automated', 'modern', 'contemporary']
        for feature in modern_features:
            if feature in description_lower:
                amenities.append(feature.title())
        
        return amenities[:4]

    def get_family_amenities(self, property):
        """Get family-friendly amenities"""
        amenities = []
        description_lower = (property.description + ' ' + property.amenities).lower()
        
        family_features = ['playground', 'garden', 'park', 'school', 'safe', 'quiet']
        for feature in family_features:
            if feature in description_lower:
                amenities.append(feature.title())
        
        return amenities[:4]

    def get_furnished_items(self, property):
        """Get list of furnished items"""
        items = []
        description_lower = (property.description + ' ' + property.amenities).lower()
        
        furniture_items = {
            'sofa': 'Sofa',
            'bed': 'Bed',
            'wardrobe': 'Wardrobe',
            'dining': 'Dining Table',
            'tv': 'TV',
            'refrigerator': 'Refrigerator',
            'washing': 'Washing Machine',
            'kitchen': 'Kitchen Appliances'
        }
        
        for item, furniture in furniture_items.items():
            if item in description_lower:
                items.append(furniture)
        
        return items if items else ['Basic Furniture']

    def calculate_furnishing_savings(self, property):
        """Estimate savings from furnished apartment"""
        # Rough estimate of furnishing costs
        base_savings = 1500  # Base savings for furnished apartment
        if property.property_type == 'house':
            base_savings = 2500
        elif property.property_type == 'apartment':
            base_savings = 1800
        
        return base_savings

    def get_pet_features(self, property):
        """Get pet-friendly features"""
        features = []
        description_lower = (property.description + ' ' + property.amenities).lower()
        
        pet_features = {
            'garden': 'Garden/Yard',
            'park': 'Nearby Park',
            'spacious': 'Spacious Layout',
            'easy clean': 'Easy-Clean Floors',
            'pet area': 'Pet Area'
        }
        
        for feature, pet_feature in pet_features.items():
            if feature in description_lower:
                features.append(pet_feature)
        
        return features if features else ['Pet Welcoming']

    def get_pet_policy(self, property):
        """Get pet policy information"""
        return "Pets Allowed with Deposit"  # This would come from property details

    def get_pet_deposit_info(self, property):
        """Get pet deposit information"""
        return "$100-200 Additional"  # This would come from property details

    def get_parking_details(self, property):
        """Get parking details"""
        description_lower = (property.description + ' ' + property.amenities).lower()
        
        if 'garage' in description_lower:
            return "Covered Garage"
        elif 'secure' in description_lower:
            return "Secure Parking"
        else:
            return "Dedicated Parking"

    def get_parking_security(self, property):
        """Get parking security information"""
        return "24/7 Security"  # This would come from property details

    def get_parking_cost(self, property):
        """Get parking cost information"""
        return "Included in Rent"  # This would come from property details

    def get_family_accommodation_advice(self, entities):
        """Get advice for family accommodation search"""
        advice = "Here are some tips for finding family accommodation:\n\n"
        advice += "💡 **Expand your search area** - Consider suburbs for better options\n"
        advice += "💰 **Adjust budget expectations** - Family housing typically costs more\n"
        advice += "🏠 **Consider shared housing** - Larger houses with multiple families\n"
        advice += "📞 **Contact property owners directly** - Some don't advertise family units\n"
        advice += "🔍 **Look for 'family-friendly' keywords** in property descriptions\n\n"
        advice += "Would you like me to search with different criteria?"
        return advice

    def get_professional_housing_advice(self, entities):
        """Get advice for professional housing search"""
        advice = "Here are tips for finding professional housing:\n\n"
        advice += "🏢 **Focus on business districts** - City centre, CBD areas\n"
        advice += "🚗 **Consider commute vs. cost** - Balance location and budget\n"
        advice += "🏠 **Look for modern amenities** - WiFi, security, parking\n"
        advice += "🤝 **Consider shared apartments** - Better value in prime locations\n"
        advice += "📅 **Check lease flexibility** - Important for career changes\n\n"
        advice += "Would you like me to adjust the search criteria?"
        return advice

# Create tenant AI service instance
tenant_ai_service = TenantAIService()
