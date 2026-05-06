from django.db import models
from django.conf import settings

class Property(models.Model):
    PROPERTY_TYPES = [
        ('hostel', 'Hostel'),
        ('pg', 'Paying Guest'),
        ('apartment', 'Apartment'),
        ('house', 'Independent House'),
        ('villa', 'Villa'),
        ('studio', 'Studio Apartment'),
        ('flat', 'Flat'),
        ('shared_room', 'Shared Room'),
        ('commercial', 'Commercial Space'),
        ('office', 'Office Space'),
        ('bedsitter', 'Bedsitter'),
        ('single_room', 'Single Room'),
        ('double_room', 'Double Room'),
        ('self_contained', 'Self Contained'),
        ('boys_quarters', "Boys' Quarters"),
        ('servants_quarters', "Servants' Quarters"),
    ]
    
    TARGET_AUDIENCE = [
        ('students', 'Students'),
        ('professionals', 'Working Professionals'),
        ('families', 'Families'),
        ('mixed', 'Mixed Audience'),
        ('business', 'Business Travelers'),
        ('expats', 'Expatriates'),
        ('senior_citizens', 'Senior Citizens'),
        ('university_students', 'University Students'),
        ('college_students', 'College Students'),
        ('interns', 'Interns'),
        ('nurses', 'Nurses & Medical Staff'),
        ('teachers', 'Teachers'),
        ('ngo_workers', 'NGO Workers'),
    ]
    
    GENDER_PREFERENCE = [
        ('any', 'Any'),
        ('male', 'Male Only'),
        ('female', 'Female Only'),
        ('family', 'Family Only'),
    ]
    
    FURNISHING_CHOICES = [
        ('unfurnished', 'Unfurnished'),
        ('semi_furnished', 'Semi Furnished'),
        ('fully_furnished', 'Fully Furnished'),
    ]
    
    AMENITY_CHOICES = [
        ('wifi', 'WiFi'),
        ('parking', 'Parking'),
        ('laundry', 'Laundry'),
        ('gym', 'Gym'),
        ('kitchen', 'Kitchen'),
        ('security', 'Security'),
        ('study_room', 'Study Room'),
        ('canteen', 'Canteen'),
        ('power_backup', 'Power Backup'),
        ('water_supply', '24/7 Water Supply'),
        ('housekeeping', 'Housekeeping'),
        ('ac', 'Air Conditioning'),
        ('heating', 'Heating'),
        ('balcony', 'Balcony'),
        ('garden', 'Garden'),
        ('swimming_pool', 'Swimming Pool'),
        ('clubhouse', 'Clubhouse'),
        ('lift', 'Lift/Elevator'),
        ('fire_safety', 'Fire Safety'),
        ('cctv', 'CCTV Surveillance'),
        ('play_area', 'Children Play Area'),
        ('generator', 'Generator'),
        ('solar_power', 'Solar Power'),
        ('water_tank', 'Water Tank'),
        ('fence', 'Compound Fence'),
        ('gate', 'Security Gate'),
        ('warden', 'Warden/Manager'),
        ('cleaning_services', 'Cleaning Services'),
        ('meals', 'Meals Included'),
        ('internet_cafe', 'Internet Cafe'),
        ('common_room', 'Common Room'),
        ('tv_room', 'TV Room'),
        ('prayer_room', 'Prayer Room'),
        ('borehole', 'Borehole Water'),
        ('rainwater_harvesting', 'Rainwater Harvesting'),
    ]
    
    SAFETY_FEATURES = [
        ('cctv', 'CCTV Cameras'),
        ('security_guard', 'Security Guard'),
        ('fire_extinguisher', 'Fire Extinguishers'),
        ('smoke_detector', 'Smoke Detectors'),
        ('emergency_exit', 'Emergency Exit'),
        ('first_aid_kit', 'First Aid Kit'),
        ('intercom', 'Intercom Facility'),
        ('visitor_management', 'Visitor Management'),
    ]
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE, default='mixed')
    gender_preference = models.CharField(max_length=20, choices=GENDER_PREFERENCE, default='any')
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    
    # Location Details
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=100, default='Kampala', help_text='Uganda district')
    county = models.CharField(max_length=100, blank=True, help_text='Uganda county')
    sub_county = models.CharField(max_length=100, blank=True, help_text='Uganda sub-county')
    parish = models.CharField(max_length=100, blank=True, help_text='Uganda parish')
    village = models.CharField(max_length=100, blank=True, help_text='Uganda village')
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='Uganda')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    nearby_landmarks = models.TextField(blank=True)
    nearby_transportation = models.TextField(blank=True)
    
    # Property Details
    total_floors = models.PositiveIntegerField(blank=True, null=True)
    property_on_floor = models.PositiveIntegerField(blank=True, null=True)
    year_built = models.PositiveIntegerField(blank=True, null=True)
    year_renovated = models.PositiveIntegerField(blank=True, null=True)
    property_age = models.PositiveIntegerField(blank=True, null=True)
    built_up_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carpet_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Room Details
    total_rooms = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField()
    min_occupancy = models.PositiveIntegerField(default=1)
    max_occupancy = models.PositiveIntegerField(default=1)
    
    # Pricing
    rent_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    maintenance_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    electricity_charge = models.CharField(max_length=100, blank=True)
    water_charge = models.CharField(max_length=100, blank=True)
    other_charges = models.TextField(blank=True)
    
    # Features
    furnishing = models.CharField(max_length=20, choices=FURNISHING_CHOICES, default='unfurnished')
    amenities = models.JSONField(default=list)
    safety_features = models.JSONField(default=list)
    rules = models.TextField(blank=True)
    restrictions = models.TextField(blank=True)
    
    # Availability
    available_from = models.DateField(blank=True, null=True)
    notice_period = models.PositiveIntegerField(default=30)  # in days
    minimum_stay_months = models.PositiveIntegerField(default=1)
    maximum_stay_months = models.PositiveIntegerField(blank=True, null=True)
    
    # Status
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    
    # Contact
    contact_person = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    alternate_contact_number = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Social Media
    facebook_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)
    youtube_link = models.URLField(blank=True)
    
    # Additional Information
    pet_friendly = models.BooleanField(default=False)
    smoking_allowed = models.BooleanField(default=False)
    non_veg_allowed = models.BooleanField(default=True)
    visitors_allowed = models.BooleanField(default=True)
    late_night_entry_allowed = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.locality}, {self.city}"
    
    @property
    def occupancy_rate(self):
        if self.total_rooms > 0:
            return ((self.total_rooms - self.available_rooms) / self.total_rooms) * 100
        return 0
    
    @property
    def full_address(self):
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.village,
            self.parish,
            self.sub_county,
            self.county,
            self.district,
            self.country
        ]
        return ', '.join(filter(None, address_parts))

class PropertyImage(models.Model):
    rental_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="External image URL")
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    image_type = models.CharField(
        max_length=20,
        choices=[
            ('exterior', 'Exterior'),
            ('interior', 'Interior'),
            ('room', 'Room'),
            ('bathroom', 'Bathroom'),
            ('kitchen', 'Kitchen'),
            ('amenity', 'Amenity'),
            ('other', 'Other'),
        ],
        default='other'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.rental_property.name} - {self.image_type}"

class PropertyVideo(models.Model):
    rental_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='property_videos/')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.rental_property.name} - Video"

class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('triple', 'Triple Sharing'),
        ('dormitory', 'Dormitory'),
        ('suite', 'Suite'),
        ('studio', 'Studio'),
        ('1bhk', '1 BHK'),
        ('2bhk', '2 BHK'),
        ('3bhk', '3 BHK'),
        ('4bhk', '4 BHK'),
    ]
    
    STATUS_CHOICES = [
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    ]
    
    rental_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor_number = models.CharField(max_length=10, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    capacity = models.PositiveIntegerField(default=1)
    current_occupancy = models.PositiveIntegerField(default=0)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_bed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='vacant')
    
    # Room Dimensions
    area_sqft = models.DecimalField(max_digits=8, decimal_places=2)
    length_ft = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    breadth_ft = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    # Features
    has_bathroom = models.BooleanField(default=True)
    has_balcony = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    has_heating = models.BooleanField(default=False)
    has_fridge = models.BooleanField(default=False)
    has_tv = models.BooleanField(default=False)
    has_wardrobe = models.BooleanField(default=False)
    has_study_table = models.BooleanField(default=False)
    has_bed = models.BooleanField(default=True)
    
    # Bathroom Details
    bathroom_type = models.CharField(
        max_length=20,
        choices=[
            ('attached', 'Attached'),
            ('common', 'Common'),
            ('none', 'None'),
        ],
        default='attached'
    )
    western_toilet = models.BooleanField(default=True)
    indian_toilet = models.BooleanField(default=False)
    geyser = models.BooleanField(default=False)
    
    # Additional Details
    furnishing_details = models.TextField(blank=True)
    room_description = models.TextField(blank=True)
    facing_direction = models.CharField(
        max_length=10,
        choices=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
            ('north_east', 'North East'),
            ('north_west', 'North West'),
            ('south_east', 'South East'),
            ('south_west', 'South West'),
        ],
        blank=True
    )
    
    # Availability
    available_from = models.DateField(blank=True, null=True)
    available_till = models.DateField(blank=True, null=True)
    
    # Pricing Details
    electricity_included = models.BooleanField(default=False)
    water_included = models.BooleanField(default=True)
    maintenance_included = models.BooleanField(default=False)
    wifi_included = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.rental_property.name} - Room {self.room_number} ({self.room_type})"
    
    @property
    def is_available(self):
        return self.status == 'vacant' and self.current_occupancy < self.capacity
    
    @property
    def available_beds(self):
        return self.capacity - self.current_occupancy

class PropertyReview(models.Model):
    rental_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    review = models.TextField()
    is_verified = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['rental_property', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.rental_property.name} ({self.rating}★)"
