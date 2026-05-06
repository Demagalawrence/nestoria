from rest_framework import serializers
from django.db.models import Avg
from .models import Property, PropertyImage, PropertyVideo, Room, PropertyReview

class PropertyImageSerializer(serializers.ModelSerializer):
    image_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url', 'image_display', 'caption', 'is_primary', 'image_type', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_display(self, obj):
        if obj.image_url:
            return obj.image_url
        elif obj.image:
            return obj.image.url
        return None

class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = ['id', 'video', 'title', 'description', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']

class PropertySerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'name', 'property_type', 'target_audience', 'gender_preference',
                 'description', 'address_line_1', 'address_line_2', 'district', 'county', 
                 'sub_county', 'parish', 'village', 'postal_code', 'country',
                 'rent_per_month', 'security_deposit', 'furnishing', 'amenities',
                 'total_rooms', 'available_rooms', 'min_occupancy', 'max_occupancy',
                 'is_featured', 'owner_name', 'primary_image', 'average_rating',
                 'total_reviews', 'created_at']
        read_only_fields = ['id', 'owner_name', 'primary_image', 'average_rating',
                           'total_reviews', 'created_at']
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return PropertyImageSerializer(primary_image).data
        first_image = obj.images.first()
        if first_image:
            return PropertyImageSerializer(first_image).data
        return None
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.aggregate(avg_rating=Avg('rating'))
        return round(reviews['avg_rating'], 1) if reviews['avg_rating'] else None
    
    def get_total_reviews(self, obj):
        return obj.reviews.count()

class PropertyDetailSerializer(PropertySerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    videos = PropertyVideoSerializer(many=True, read_only=True)
    rooms = serializers.SerializerMethodField()
    full_address = serializers.ReadOnlyField()
    occupancy_rate = serializers.ReadOnlyField()
    
    class Meta(PropertySerializer.Meta):
        fields = PropertySerializer.Meta.fields + ['detailed_description', 'address_line_2',
                 'country', 'latitude', 'longitude', 'nearby_landmarks', 'nearby_transportation',
                 'total_floors', 'property_on_floor', 'year_built', 'built_up_area', 'carpet_area',
                 'maintenance_charge', 'electricity_charge', 'water_charge', 'other_charges',
                 'safety_features', 'rules', 'restrictions', 'available_from', 'notice_period',
                 'minimum_stay_months', 'maximum_stay_months', 'contact_person', 'contact_number',
                 'whatsapp_number', 'email', 'pet_friendly', 'smoking_allowed', 'non_veg_allowed',
                 'visitors_allowed', 'late_night_entry_allowed', 'images', 'videos', 'rooms', 'full_address',
                 'occupancy_rate']
    
    def get_rooms(self, obj):
        rooms = obj.rooms.filter(status='vacant')[:10]  # Limit to 10 vacant rooms
        return RoomSerializer(rooms, many=True).data

class PropertyCreateSerializer(serializers.ModelSerializer):
    image_urls = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="List of image URLs for the property"
    )
    
    class Meta:
        model = Property
        fields = ['name', 'property_type', 'target_audience', 'gender_preference',
                 'description', 'address_line_1', 'address_line_2', 'district', 'county',
                 'sub_county', 'parish', 'village', 'postal_code', 'country',
                 'total_rooms', 'available_rooms', 'min_occupancy', 'max_occupancy',
                 'rent_per_month', 'security_deposit', 'built_up_area', 'carpet_area',
                 'contact_person', 'contact_number', 'whatsapp_number', 'furnishing', 
                 'amenities', 'is_active', 'is_featured', 'nearby_landmarks', 
                 'nearby_transportation', 'total_floors', 'property_on_floor',
                 'year_built', 'year_renovated', 'maintenance_charge', 'electricity_charge', 
                 'water_charge', 'other_charges', 'safety_features', 'rules',
                 'restrictions', 'available_from', 'notice_period', 'minimum_stay_months',
                 'maximum_stay_months', 'email', 'website', 'facebook_link', 'instagram_link',
                 'youtube_link', 'pet_friendly', 'smoking_allowed', 'non_veg_allowed',
                 'visitors_allowed', 'late_night_entry_allowed', 'image_urls']
    
    def create(self, validated_data):
        image_urls = validated_data.pop('image_urls', [])
        property_obj = Property.objects.create(**validated_data)
        
        # Create property images from URLs if any
        if image_urls:
            for index, image_url in enumerate(image_urls):
                is_primary = index == 0  # First image is primary by default
                PropertyImage.objects.create(
                    rental_property=property_obj,
                    image_url=image_url,  # Store URL in image_url field
                    is_primary=is_primary,
                    image_type='exterior'
                )
        
        return property_obj

class RoomSerializer(serializers.ModelSerializer):
    rental_property_name = serializers.CharField(source='rental_property.name', read_only=True)
    is_available = serializers.ReadOnlyField()
    available_beds = serializers.ReadOnlyField()
    
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'floor_number', 'room_type', 'capacity', 'current_occupancy',
                 'price_per_month', 'price_per_bed', 'status', 'area_sqft', 'length_ft', 'breadth_ft',
                 'has_bathroom', 'has_balcony', 'has_ac', 'has_heating', 'has_fridge', 'has_tv',
                 'has_wardrobe', 'has_study_table', 'has_bed', 'bathroom_type', 'western_toilet',
                 'indian_toilet', 'geyser', 'furnishing_details', 'room_description', 'facing_direction',
                 'available_from', 'available_till', 'electricity_included', 'water_included',
                 'maintenance_included', 'wifi_included', 'rental_property_name', 'is_available',
                 'available_beds', 'created_at']
        read_only_fields = ['id', 'rental_property_name', 'is_available', 'available_beds', 'created_at']

class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['room_number', 'floor_number', 'room_type', 'capacity', 'price_per_month',
                 'price_per_bed', 'area_sqft', 'length_ft', 'breadth_ft', 'has_bathroom',
                 'has_balcony', 'has_ac', 'has_heating', 'has_fridge', 'has_tv', 'has_wardrobe',
                 'has_study_table', 'has_bed', 'bathroom_type', 'western_toilet', 'indian_toilet',
                 'geyser', 'furnishing_details', 'room_description', 'facing_direction',
                 'available_from', 'available_till', 'electricity_included', 'water_included',
                 'maintenance_included', 'wifi_included']

class PropertyReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = PropertyReview
        fields = ['id', 'rating', 'title', 'review', 'user_name', 'is_verified',
                 'helpful_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_name', 'is_verified', 'helpful_count', 'created_at', 'updated_at']
