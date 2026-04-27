"""
USSD System Services for Uganda Rental Platform
"""
import json
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .models import USSDSession, USSDMenuItem, USSDRequestLog, USSDUser, USSDPropertyCache, USSDBooking
from properties.models import Property
from bookings.models import Booking
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

class USSDService:
    """Service for handling USSD interactions"""
    
    def __init__(self):
        self.session_timeout_minutes = 5  # 5 minutes timeout
        self.max_text_length = 160  # SMS character limit
    
    def process_ussd_request(self, phone_number, request_text, session_id=None):
        """Process incoming USSD request"""
        try:
            # Get or create session
            session = self.get_or_create_session(phone_number, session_id)
            
            # Log request
            start_time = timezone.now()
            
            # Process the request
            response_text, response_screen = self.process_session_request(session, request_text)
            
            # Calculate processing time
            processing_time = (timezone.now() - start_time).total_seconds() * 1000
            
            # Log the request
            USSDRequestLog.objects.create(
                session=session,
                phone_number=phone_number,
                request_text=request_text,
                response_text=response_text,
                response_screen=response_screen,
                processing_time_ms=int(processing_time),
                success=True
            )
            
            return {
                'success': True,
                'session_id': session.session_id,
                'response_text': response_text,
                'screen': response_screen,
                'continue_session': session.is_active
            }
            
        except Exception as e:
            logger.error(f"USSD request processing failed: {str(e)}")
            
            # Log error
            if 'session' in locals():
                USSDRequestLog.objects.create(
                    session=session,
                    phone_number=phone_number,
                    request_text=request_text,
                    response_text="Error processing request",
                    response_screen='error',
                    success=False,
                    error_message=str(e)
                )
            
            return {
                'success': False,
                'error': str(e),
                'response_text': "Service temporarily unavailable. Please try again later."
            }
    
    def get_or_create_session(self, phone_number, session_id=None):
        """Get existing session or create new one"""
        # Clean up expired sessions
        self.cleanup_expired_sessions()
        
        if session_id:
            try:
                session = USSDSession.objects.get(session_id=session_id, phone_number=phone_number)
                if session.is_active:
                    # Update activity
                    session.last_activity = timezone.now()
                    session.expires_at = timezone.now() + timedelta(minutes=self.session_timeout_minutes)
                    session.save()
                    return session
                else:
                    # Session expired, create new one
                    return self.create_new_session(phone_number)
            except USSDSession.DoesNotExist:
                pass
        
        # Create new session
        return self.create_new_session(phone_number)
    
    def create_new_session(self, phone_number):
        """Create new USSD session"""
        session_id = f"ussd_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Try to identify user by phone number
        user = None
        try:
            user = User.objects.get(username=phone_number)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                pass
        
        session = USSDSession.objects.create(
            session_id=session_id,
            phone_number=phone_number,
            user=user,
            is_authenticated=user is not None,
            expires_at=timezone.now() + timedelta(minutes=self.session_timeout_minutes)
        )
        
        return session
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        expired_sessions = USSDSession.objects.filter(
            expires_at__lt=timezone.now(),
            status='active'
        )
        
        for session in expired_sessions:
            session.status = 'timeout'
            session.save()
    
    def process_session_request(self, session, request_text):
        """Process request within session context"""
        try:
            # Get current screen
            current_screen = self.get_current_screen(session.current_screen)
            
            if not current_screen:
                # Default to main menu
                current_screen = self.get_current_screen('main_menu')
                session.current_screen = 'main_menu'
                session.save()
            
            # Process the request
            if current_screen.requires_input:
                return self.process_input_request(session, current_screen, request_text)
            else:
                return self.process_menu_request(session, current_screen, request_text)
                
        except Exception as e:
            logger.error(f"Session request processing failed: {str(e)}")
            return "Error processing request. Please try again.", 'main_menu'
    
    def get_current_screen(self, screen_id):
        """Get USSD screen by ID"""
        try:
            return USSDMenuItem.objects.get(screen_id=screen_id, is_active=True)
        except USSDMenuItem.DoesNotExist:
            return None
    
    def process_menu_request(self, session, screen, request_text):
        """Process menu selection request"""
        # Clean input
        request_text = request_text.strip()
        
        # Find matching option
        selected_option = None
        for option in screen.options:
            if option['id'] == request_text:
                selected_option = option
                break
        
        if not selected_option:
            return "Invalid selection. Please try again.", screen.screen_id
        
        # Handle special cases
        if selected_option['screen'] == 'exit':
            session.status = 'completed'
            session.save()
            exit_screen = self.get_current_screen('exit')
            return exit_screen.description, 'exit'
        
        # Navigate to next screen
        next_screen_id = selected_option['screen']
        next_screen = self.get_current_screen(next_screen_id)
        
        if not next_screen:
            return "Screen not available. Please try again.", screen.screen_id
        
        # Update session
        session.current_screen = next_screen_id
        session.last_activity = timezone.now()
        
        # Store any additional data
        if 'data' in selected_option:
            session.session_data.update(selected_option['data'])
        
        session.save()
        
        # Generate response
        if next_screen.action_type == 'search':
            return self.handle_search_action(session, next_screen)
        elif next_screen.action_type == 'my_bookings':
            return self.handle_my_bookings_action(session, next_screen)
        elif next_screen.action_type == 'profile':
            return self.handle_profile_action(session, next_screen)
        elif next_screen.action_type == 'help':
            return self.handle_help_action(session, next_screen)
        else:
            return self.generate_menu_response(session, next_screen)
    
    def process_input_request(self, session, screen, request_text):
        """Process input request"""
        # Validate input
        validation_result = self.validate_input(screen, request_text)
        if not validation_result['valid']:
            return validation_result['error'], screen.screen_id
        
        # Store input in session
        session.session_data[screen.screen_id] = request_text
        session.last_activity = timezone.now()
        session.save()
        
        # Process based on action type
        if screen.action_type == 'search':
            return self.handle_search_action(session, screen)
        elif screen.action_type == 'authenticate':
            return self.handle_authenticate_action(session, screen)
        else:
            # Navigate to next screen
            next_screen_id = screen.action_data.get('next_screen', 'main_menu')
            next_screen = self.get_current_screen(next_screen_id)
            
            if next_screen:
                session.current_screen = next_screen_id
                session.save()
                return self.generate_menu_response(session, next_screen)
            
            return "Processing complete. Thank you!", 'main_menu'
    
    def validate_input(self, screen, input_text):
        """Validate user input"""
        input_text = input_text.strip()
        
        # Check required fields
        if not input_text:
            return {'valid': False, 'error': 'This field is required'}
        
        # Type-specific validation
        if screen.input_type == 'number':
            try:
                value = int(input_text)
                if 'min_value' in screen.input_validation and value < screen.input_validation['min_value']:
                    return {'valid': False, 'error': f"Minimum value is {screen.input_validation['min_value']}"}
                if 'max_value' in screen.input_validation and value > screen.input_validation['max_value']:
                    return {'valid': False, 'error': f"Maximum value is {screen.input_validation['max_value']}"}
            except ValueError:
                return {'valid': False, 'error': 'Please enter a valid number'}
        
        elif screen.input_type == 'phone':
            # Validate Uganda phone number
            import re
            uganda_phone_pattern = r'^\+256[0-9]{9}$|^07[0-9]{9}$'
            if not re.match(uganda_phone_pattern, input_text):
                return {'valid': False, 'error': 'Please enter a valid Uganda phone number (+256XXXXXXXX or 07XXXXXXXX)'}
        
        elif screen.input_type == 'email':
            # Basic email validation
            if '@' not in input_text or '.' not in input_text:
                return {'valid': False, 'error': 'Please enter a valid email address'}
        
        elif screen.input_type == 'amount':
            try:
                value = int(input_text)
                if value < 0:
                    return {'valid': False, 'error': 'Amount cannot be negative'}
                if value > 10000000:  # 10 million UGX
                    return {'valid': False, 'error': 'Maximum amount is 10,000,000 UGX'}
            except ValueError:
                return {'valid': False, 'error': 'Please enter a valid amount'}
        
        # Length validation
        if 'min_length' in screen.input_validation and len(input_text) < screen.input_validation['min_length']:
            return {'valid': False, 'error': f"Minimum length is {screen.input_validation['min_length']} characters"}
        
        if 'max_length' in screen.input_validation and len(input_text) > screen.input_validation['max_length']:
            return {'valid': False, 'error': f"Maximum length is {screen.input_validation['max_length']} characters"}
        
        return {'valid': True}
    
    def handle_search_action(self, session, screen):
        """Handle search action"""
        search_type = screen.action_data.get('search_type', 'location')
        
        if search_type == 'location':
            location = session.session_data.get('search_location', '')
            if not location:
                return "Please enter a location to search.", 'search_location'
            
            # Search properties by location
            properties = self.search_properties_by_location(location)
            return self.format_search_results(session, properties)
        
        elif search_type == 'price':
            max_price = session.session_data.get('search_price', '')
            if not max_price:
                return "Please enter maximum price.", 'search_price'
            
            # Search properties by price
            properties = self.search_properties_by_price(max_price)
            return self.format_search_results(session, properties)
        
        elif search_type == 'university':
            university = session.session_data.get('university', '')
            # Search properties by university
            properties = self.search_properties_by_university(university)
            return self.format_search_results(session, properties)
        
        return "Search not available. Please try again.", 'main_menu'
    
    def search_properties_by_location(self, location):
        """Search properties by location"""
        # Search in cached properties first
        cached_properties = USSDPropertyCache.objects.filter(
            is_active=True,
            keywords__icontains=location.lower()
        )
        
        if cached_properties.exists():
            return [cached.property for cached in cached_properties]
        
        # Fallback to main property search
        properties = Property.objects.filter(
            is_approved=True,
            is_available=True
        ).filter(
            models.Q(district__icontains=location) |
            models.Q(county__icontains=location) |
            models.Q(village__icontains=location) |
            models.Q(city__icontains=location)
        )[:10]  # Limit for USSD
        
        return properties
    
    def search_properties_by_price(self, max_price):
        """Search properties by price"""
        try:
            max_price = int(max_price)
        except ValueError:
            return Property.objects.none()
        
        properties = Property.objects.filter(
            is_approved=True,
            is_available=True,
            monthly_rent__lte=max_price
        ).order_by('monthly_rent')[:10]
        
        return properties
    
    def search_properties_by_university(self, university):
        """Search properties by university"""
        # University-specific search
        university_areas = {
            'makerere': ['wandegeya', 'kikoni', 'bweyogerere'],
            'kyambogo': ['bunga', 'nakawa', 'kireka'],
            'bugema': ['bugema', 'bukoto', 'kikoni'],
            'ucu': ['mukono', 'seeta', 'kampala'],
            'must': ['mbarara', 'kashaka', 'kashozi'],
        }
        
        areas = university_areas.get(university.lower(), [])
        
        if not areas:
            return Property.objects.none()
        
        properties = Property.objects.filter(
            is_approved=True,
            is_available=True
        ).filter(
            models.Q(district__in=areas) |
            models.Q(county__in=areas) |
            models.Q(village__in=areas)
        )[:10]
        
        return properties
    
    def format_search_results(self, session, properties):
        """Format search results for USSD display"""
        if not properties:
            return "No properties found. Try different search criteria.", 'search_menu'
        
        # Store results in session
        session.session_data['search_results'] = [p.id for p in properties]
        session.save()
        
        # Format response
        response_parts = [f"Found {len(properties)} properties:"]
        
        for i, property in enumerate(properties[:5], 1):  # Limit to 5 for USSD
            # Use cached short name if available
            try:
                cached = USSDPropertyCache.objects.get(property=property, is_active=True)
                name = cached.short_name
                price = cached.price_display
                location = cached.location_display
            except USSDPropertyCache.DoesNotExist:
                name = property.name[:20]  # Truncate for USSD
                price = f"UGX {property.monthly_rent:,}"
                location = property.district[:15] if property.district else 'Unknown'
            
            response_parts.append(f"{i}. {name}")
            response_parts.append(f"   {price} - {location}")
        
        response_parts.append("")
        response_parts.append("Reply with property number to book")
        response_parts.append("0. Back to search menu")
        
        response_text = "\n".join(response_parts)
        
        # Truncate if too long
        if len(response_text) > self.max_text_length:
            response_text = response_text[:self.max_text_length-3] + "..."
        
        return response_text, 'search_results'
    
    def handle_my_bookings_action(self, session, screen):
        """Handle my bookings action"""
        if not session.user:
            return "Please login to view your bookings.", 'main_menu'
        
        # Get user's bookings
        bookings = Booking.objects.filter(user=session.user).order_by('-created_at')[:5]
        
        if not bookings:
            return "You have no bookings yet.", 'main_menu'
        
        # Format response
        response_parts = ["Your bookings:"]
        
        for i, booking in enumerate(bookings, 1):
            property_name = booking.rental_property.name[:20]
            status = booking.status.title()
            response_parts.append(f"{i}. {property_name}")
            response_parts.append(f"   Status: {status}")
            response_parts.append(f"   Ref: {booking.booking_reference}")
        
        response_parts.append("")
        response_parts.append("0. Back to main menu")
        
        response_text = "\n".join(response_parts)
        
        # Truncate if too long
        if len(response_text) > self.max_text_length:
            response_text = response_text[:self.max_text_length-3] + "..."
        
        return response_text, 'my_bookings'
    
    def handle_profile_action(self, session, screen):
        """Handle profile action"""
        if not session.user:
            return "Please login to view your profile.", 'main_menu'
        
        # Get user profile
        user = session.user
        
        response_parts = [f"Profile: {user.get_full_name() or user.username}"]
        response_parts.append(f"Phone: {user.phone_number or 'Not set'}")
        response_parts.append(f"Email: {user.email}")
        response_parts.append(f"Role: {user.role.title()}")
        response_parts.append("")
        response_parts.append("0. Back to main menu")
        
        response_text = "\n".join(response_parts)
        
        return response_text, 'profile_menu'
    
    def handle_help_action(self, session, screen):
        """Handle help action"""
        response_parts = ["RentHu Uganda Help"]
        response_parts.append("")
        response_parts.append("For help:")
        response_parts.append("Call: +256 123 456 789")
        response_parts.append("Email: support@renthu.ug")
        response_parts.append("Visit: www.renthu.ug")
        response_parts.append("")
        response_parts.append("Available 8AM-8PM daily")
        response_parts.append("")
        response_parts.append("0. Back to main menu")
        
        response_text = "\n".join(response_parts)
        
        return response_text, 'help_menu'
    
    def generate_menu_response(self, session, screen):
        """Generate menu response"""
        response_parts = [screen.title]
        
        if screen.description:
            response_parts.append(screen.description)
        
        response_parts.append("")
        
        for option in screen.options:
            response_parts.append(f"{option['id']}. {option['text']}")
        
        response_text = "\n".join(response_parts)
        
        # Truncate if too long
        if len(response_text) > self.max_text_length:
            response_text = response_text[:self.max_text_length-3] + "..."
        
        return response_text, screen.screen_id
    
    def handle_property_selection(self, session, property_index):
        """Handle property selection from search results"""
        try:
            property_index = int(property_index)
            search_results = session.session_data.get('search_results', [])
            
            if not search_results or property_index < 1 or property_index > len(search_results):
                return "Invalid property selection. Please try again.", 'search_results'
            
            property_id = search_results[property_index - 1]
            property = Property.objects.get(id=property_id)
            
            # Get property details
            try:
                cached = USSDPropertyCache.objects.get(property=property, is_active=True)
                details = [
                    f"{cached.short_name}",
                    f"Price: {cached.price_display}",
                    f"Location: {cached.location_display}",
                    f"Contact: {cached.contact_display}",
                ]
            except USSDPropertyCache.DoesNotExist:
                details = [
                    property.name[:30],
                    f"Price: UGX {property.monthly_rent:,}",
                    f"Location: {property.district or 'Unknown'}",
                    f"Contact: {property.owner.phone_number or 'Call support'}",
                ]
            
            details.extend([
                "",
                "1. Book this property",
                "2. More details",
                "0. Back to search"
            ])
            
            # Store selected property
            session.session_data['selected_property'] = property_id
            session.save()
            
            return "\n".join(details), 'property_details'
            
        except (ValueError, Property.DoesNotExist):
            return "Property not found. Please try again.", 'search_results'

# Create service instance
ussd_service = USSDService()
