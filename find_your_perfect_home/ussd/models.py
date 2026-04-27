"""
USSD System Models for Uganda Rental Platform
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid
import json

class USSDSession(models.Model):
    """USSD session tracking"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('timeout', 'Timeout'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ]
    
    session_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    
    # Session state
    current_screen = models.CharField(max_length=50, default='main_menu')
    session_data = models.JSONField(default=dict)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=timezone.now)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # User identification
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ussd_sessions'
    )
    is_authenticated = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.phone_number} - {self.session_id[:8]}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_active(self):
        return self.status == 'active' and not self.is_expired

class USSDMenuItem(models.Model):
    """USSD menu items and navigation"""
    
    screen_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Navigation
    parent_screen = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    back_screen = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='back_from')
    
    # Menu options
    options = models.JSONField(default=list)
    
    # Input handling
    requires_input = models.BooleanField(default=False)
    input_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('number', 'Number'),
        ('phone', 'Phone Number'),
        ('email', 'Email'),
        ('amount', 'Amount'),
    ], blank=True)
    
    input_placeholder = models.CharField(max_length=100, blank=True)
    input_validation = models.JSONField(default=dict)
    
    # Actions
    action_type = models.CharField(max_length=50, choices=[
        ('menu', 'Show Menu'),
        ('search', 'Search Properties'),
        ('book', 'Book Property'),
        ('my_bookings', 'My Bookings'),
        ('profile', 'User Profile'),
        ('help', 'Help/Support'),
        ('exit', 'Exit'),
        ('authenticate', 'Authenticate'),
        ('input', 'Process Input'),
    ], default='menu')
    
    action_data = models.JSONField(default=dict)
    
    # Display settings
    max_text_length = models.PositiveIntegerField(default=160)  # SMS limit
    paginate = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.screen_id} - {self.title}"

class USSDRequestLog(models.Model):
    """Log all USSD requests"""
    
    session = models.ForeignKey(USSDSession, on_delete=models.CASCADE, related_name='requests')
    
    # Request details
    phone_number = models.CharField(max_length=20)
    request_text = models.CharField(max_length=500)
    
    # Response details
    response_text = models.TextField()
    response_screen = models.CharField(max_length=50)
    
    # Timing
    request_time = models.DateTimeField(auto_now_add=True)
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # User agent (if available)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.phone_number} - {self.request_time}"

class USSDUser(models.Model):
    """USSD-specific user data"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='ussd_profile'
    )
    
    # Phone verification
    phone_number = models.CharField(max_length=20, unique=True)
    phone_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=10, blank=True)
    
    # USSD preferences
    preferred_language = models.CharField(max_length=10, choices=[
        ('en', 'English'),
        ('lg', 'Luganda'),
        ('sw', 'Swahili'),
    ], default='en')
    
    # Usage tracking
    total_sessions = models.PositiveIntegerField(default=0)
    last_session = models.DateTimeField(null=True, blank=True)
    favorite_properties = models.JSONField(default=list)
    
    # Quick actions
    quick_search_location = models.CharField(max_length=100, blank=True)
    quick_search_price_range = models.CharField(max_length=50, blank=True)
    
    # Notification preferences
    sms_notifications = models.BooleanField(default=True)
    booking_confirmations = models.BooleanField(default=True)
    payment_reminders = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"

class USSDPropertyCache(models.Model):
    """Cache frequently accessed properties for USSD"""
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    
    # USSD-friendly data
    short_name = models.CharField(max_length=50)
    short_description = models.CharField(max_length=100)
    price_display = models.CharField(max_length=30)
    location_display = models.CharField(max_length=50)
    contact_display = models.CharField(max_length=30)
    
    # Search optimization
    keywords = models.JSONField(default=list)  # Search keywords
    tags = models.JSONField(default=list)      # Tags for quick filtering
    
    # Popularity tracking
    view_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)
    
    # Cache management
    last_updated = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.short_name} - {self.price_display}"

class USSDBooking(models.Model):
    """USSD-specific booking tracking"""
    
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='ussd_booking')
    
    # USSD session info
    session = models.ForeignKey(USSDSession, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking process tracking
    search_query = models.CharField(max_length=200, blank=True)
    property_selected = models.ForeignKey('properties.Property', on_delete=models.SET_NULL, null=True, related_name='ussd_bookings')
    
    # Confirmation via USSD
    confirmed_via_ussd = models.BooleanField(default=False)
    confirmation_code = models.CharField(max_length=10, blank=True)
    
    # Payment via USSD
    payment_method = models.CharField(max_length=20, choices=[
        ('mobile_money', 'Mobile Money'),
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('pending', 'Pending'),
    ], default='pending')
    
    # Status updates via USSD
    last_status_update = models.DateTimeField(auto_now=True)
    status_updates = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"USSD Booking - {self.booking.booking_reference}"

# Create default USSD menu structure
def create_default_ussd_menu():
    """Create default USSD menu structure"""
    
    # Main menu
    main_menu, created = USSDMenuItem.objects.get_or_create(
        screen_id='main_menu',
        defaults={
            'title': 'RentHu Uganda - Main Menu',
            'description': 'Find your perfect accommodation',
            'options': [
                {'id': '1', 'text': 'Search Hostels', 'screen': 'search_menu'},
                {'id': '2', 'text': 'Book Room', 'screen': 'quick_book'},
                {'id': '3', 'text': 'My Bookings', 'screen': 'my_bookings'},
                {'id': '4', 'text': 'My Profile', 'screen': 'profile_menu'},
                {'id': '5', 'text': 'Help & Support', 'screen': 'help_menu'},
                {'id': '0', 'text': 'Exit', 'screen': 'exit'},
            ],
            'action_type': 'menu'
        }
    )
    
    # Search menu
    search_menu, created = USSDMenuItem.objects.get_or_create(
        screen_id='search_menu',
        defaults={
            'title': 'Search Hostels',
            'description': 'Find accommodation by location',
            'options': [
                {'id': '1', 'text': 'By Location', 'screen': 'search_location'},
                {'id': '2', 'text': 'By Price', 'screen': 'search_price'},
                {'id': '3', 'text': 'By University', 'screen': 'search_university'},
                {'id': '4', 'text': 'Popular Areas', 'screen': 'popular_areas'},
                {'id': '0', 'text': 'Back', 'screen': 'main_menu'},
            ],
            'action_type': 'menu'
        }
    )
    
    # Search by location
    search_location, created = USSDMenuItem.objects.get_or_create(
        screen_id='search_location',
        defaults={
            'title': 'Enter Location',
            'description': 'Type location (e.g., Kampala, Makerere)',
            'requires_input': True,
            'input_type': 'text',
            'input_placeholder': 'Enter location',
            'input_validation': {'min_length': 2, 'max_length': 50},
            'action_type': 'search',
            'action_data': {'search_type': 'location'}
        }
    )
    
    # Search by price
    search_price, created = USSDMenuItem.objects.get_or_create(
        screen_id='search_price',
        defaults={
            'title': 'Enter Price Range',
            'description': 'Enter max price (e.g., 150000)',
            'requires_input': True,
            'input_type': 'amount',
            'input_placeholder': 'Enter max price in UGX',
            'input_validation': {'min_value': 0, 'max_value': 5000000},
            'action_type': 'search',
            'action_data': {'search_type': 'price'}
        }
    )
    
    # Search by university
    search_university, created = USSDMenuItem.objects.get_or_create(
        screen_id='search_university',
        defaults={
            'title': 'Select University',
            'description': 'Choose your university',
            'options': [
                {'id': '1', 'text': 'Makerere University', 'screen': 'search_results', 'data': {'university': 'makerere'}},
                {'id': '2', 'text': 'Kyambogo University', 'screen': 'search_results', 'data': {'university': 'kyambogo'}},
                {'id': '3', 'text': 'Bugema University', 'screen': 'search_results', 'data': {'university': 'bugema'}},
                {'id': '4', 'text': 'UCU', 'screen': 'search_results', 'data': {'university': 'ucu'}},
                {'id': '5', 'text': 'MUST', 'screen': 'search_results', 'data': {'university': 'must'}},
                {'id': '0', 'text': 'Back', 'screen': 'search_menu'},
            ],
            'action_type': 'menu'
        }
    )
    
    # Search results
    search_results, created = USSDMenuItem.objects.get_or_create(
        screen_id='search_results',
        defaults={
            'title': 'Search Results',
            'description': 'Available properties',
            'action_type': 'search',
            'paginate': True,
            'max_text_length': 140
        }
    )
    
    # My bookings
    my_bookings, created = USSDMenuItem.objects.get_or_create(
        screen_id='my_bookings',
        defaults={
            'title': 'My Bookings',
            'description': 'View your booking status',
            'action_type': 'my_bookings',
            'paginate': True
        }
    )
    
    # Profile menu
    profile_menu, created = USSDMenuItem.objects.get_or_create(
        screen_id='profile_menu',
        defaults={
            'title': 'My Profile',
            'description': 'Manage your account',
            'options': [
                {'id': '1', 'text': 'My Details', 'screen': 'profile_details'},
                {'id': '2', 'text': 'Language', 'screen': 'language_settings'},
                {'id': '3', 'text': 'Notifications', 'screen': 'notification_settings'},
                {'id': '0', 'text': 'Back', 'screen': 'main_menu'},
            ],
            'action_type': 'menu'
        }
    )
    
    # Help menu
    help_menu, created = USSDMenuItem.objects.get_or_create(
        screen_id='help_menu',
        defaults={
            'title': 'Help & Support',
            'description': 'Get help with your booking',
            'options': [
                {'id': '1', 'text': 'FAQ', 'screen': 'faq'},
                {'id': '2', 'text': 'Contact Support', 'screen': 'contact_support'},
                {'id': '3', 'text': 'Report Issue', 'screen': 'report_issue'},
                {'id': '0', 'text': 'Back', 'screen': 'main_menu'},
            ],
            'action_type': 'menu'
        }
    )
    
    # Exit screen
    exit_screen, created = USSDMenuItem.objects.get_or_create(
        screen_id='exit',
        defaults={
            'title': 'Thank You!',
            'description': 'Visit us at www.renthu.ug or call +256 123 456 789',
            'action_type': 'exit'
        }
    )
    
    # Set back navigation
    search_menu.back_screen = main_menu
    search_location.back_screen = search_menu
    search_price.back_screen = search_menu
    search_university.back_screen = search_menu
    profile_menu.back_screen = main_menu
    help_menu.back_screen = main_menu
    
    # Save all
    main_menu.save()
    search_menu.save()
    search_location.save()
    search_price.save()
    search_university.save()
    search_results.save()
    my_bookings.save()
    profile_menu.save()
    help_menu.save()
    exit_screen.save()
