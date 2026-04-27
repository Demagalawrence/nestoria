from django.contrib import admin
from .models import Property, PropertyImage, PropertyVideo, PropertyReview, Room

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_type', 'target_audience', 'owner', 'district', 'is_approved', 'is_active', 'created_at')
    list_filter = ('property_type', 'target_audience', 'gender_preference', 'furnishing', 'is_approved', 'is_active', 'verification_status', 'district')
    search_fields = ('name', 'owner__username', 'district', 'county', 'village')
    
    fieldsets = (
        ('Basic Info', {'fields': ('owner', 'name', 'property_type', 'target_audience', 'gender_preference', 'description', 'detailed_description')}),
        ('Location', {'fields': ('address_line_1', 'address_line_2', 'district', 'county', 'sub_county', 'parish', 'village', 'postal_code', 'country', 'latitude', 'longitude', 'nearby_landmarks', 'nearby_transportation')}),
        ('Property Details', {'fields': ('total_floors', 'property_on_floor', 'year_built', 'year_renovated', 'property_age', 'built_up_area', 'carpet_area')}),
        ('Room Details', {'fields': ('total_rooms', 'available_rooms', 'min_occupancy', 'max_occupancy')}),
        ('Pricing', {'fields': ('rent_per_month', 'security_deposit', 'maintenance_charge', 'electricity_charge', 'water_charge', 'other_charges')}),
        ('Features', {'fields': ('furnishing', 'amenities', 'safety_features', 'rules', 'restrictions')}),
        ('Availability', {'fields': ('available_from', 'notice_period', 'minimum_stay_months', 'maximum_stay_months')}),
        ('Status', {'fields': ('is_approved', 'is_active', 'is_featured', 'verification_status')}),
        ('Contact', {'fields': ('contact_person', 'contact_number', 'alternate_contact_number', 'whatsapp_number', 'email', 'website')}),
        ('Social Media', {'fields': ('facebook_link', 'instagram_link', 'youtube_link')}),
        ('Policies', {'fields': ('pet_friendly', 'smoking_allowed', 'non_veg_allowed', 'visitors_allowed', 'late_night_entry_allowed')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('rental_property', 'image_type', 'is_primary', 'caption', 'created_at')
    list_filter = ('image_type', 'is_primary')
    search_fields = ('rental_property__name', 'caption')
    readonly_fields = ('created_at',)

@admin.register(PropertyVideo)
class PropertyVideoAdmin(admin.ModelAdmin):
    list_display = ('rental_property', 'title', 'is_primary', 'created_at')
    list_filter = ('is_primary',)
    search_fields = ('rental_property__name', 'title', 'description')
    readonly_fields = ('created_at',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('rental_property', 'room_number', 'room_type', 'capacity', 'current_occupancy', 'price_per_month', 'status')
    list_filter = ('room_type', 'status', 'has_bathroom', 'has_ac', 'has_balcony')
    search_fields = ('rental_property__name', 'room_number', 'floor_number')
    
    fieldsets = (
        ('Basic Info', {'fields': ('rental_property', 'room_number', 'floor_number', 'room_type', 'capacity', 'current_occupancy')}),
        ('Pricing', {'fields': ('price_per_month', 'price_per_bed')}),
        ('Status', {'fields': ('status',)}),
        ('Dimensions', {'fields': ('area_sqft', 'length_ft', 'breadth_ft')}),
        ('Features', {'fields': ('has_bathroom', 'has_balcony', 'has_ac', 'has_heating', 'has_fridge', 'has_tv', 'has_wardrobe', 'has_study_table', 'has_bed')}),
        ('Bathroom', {'fields': ('bathroom_type', 'western_toilet', 'indian_toilet', 'geyser')}),
        ('Details', {'fields': ('furnishing_details', 'room_description', 'facing_direction')}),
        ('Availability', {'fields': ('available_from', 'available_till')}),
        ('Pricing Details', {'fields': ('electricity_included', 'water_included', 'maintenance_included', 'wifi_included')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ('rental_property', 'user', 'rating', 'is_verified', 'helpful_count', 'created_at')
    list_filter = ('rating', 'is_verified')
    search_fields = ('rental_property__name', 'user__username', 'title', 'review')
    readonly_fields = ('created_at', 'updated_at')
