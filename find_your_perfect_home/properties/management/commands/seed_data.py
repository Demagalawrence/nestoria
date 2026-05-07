from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from properties.models import Property, Room
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial properties and users.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seed...')
        
        # 1. Create a dummy owner user if it doesn't exist
        owner, created = User.objects.get_or_create(
            username='default_owner',
            defaults={
                'email': 'owner@nestoria.com',
                'first_name': 'Nestoria',
                'last_name': 'Owner',
                'role': 'owner',
                'is_active': True
            }
        )
        if created:
            owner.set_password('nestoria2026')
            owner.save()
            self.stdout.write(self.style.SUCCESS('Created default owner account.'))
        else:
            self.stdout.write('Default owner already exists.')

        # 2. Define sample properties
        sample_properties = [
            {
                'name': 'Modern Studio Apartment - Kampala',
                'description': 'A beautiful modern studio apartment in the heart of Kampala with all amenities.',
                'property_type': 'studio',
                'target_audience': 'public',
                'rent_per_month': Decimal('450000.00'),
                'district': 'Kampala',
                'village': 'Kampala City Center',
                'total_rooms': 1,
                'available_rooms': 1,
                'gender_preference': 'any',
                'furnishing': 'fully_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'University Hostel - Makerere',
                'description': 'Perfect hostel for Makerere University students with secure environment.',
                'property_type': 'hostel',
                'target_audience': 'university_students',
                'rent_per_month': Decimal('250000.00'),
                'district': 'Kampala',
                'village': 'Makerere',
                'total_rooms': 20,
                'available_rooms': 5,
                'gender_preference': 'any',
                'furnishing': 'semi_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Self-Contained House - Muyenga',
                'description': 'Spacious self-contained house in upscale Muyenga neighborhood.',
                'property_type': 'self_contained',
                'target_audience': 'mixed',
                'rent_per_month': Decimal('800000.00'),
                'district': 'Kampala',
                'village': 'Muyenga',
                'total_rooms': 3,
                'available_rooms': 1,
                'gender_preference': 'any',
                'furnishing': 'fully_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Single Room - Ntinda',
                'description': 'Affordable single room in quiet Ntinda neighborhood.',
                'property_type': 'single_room',
                'target_audience': 'mixed',
                'rent_per_month': Decimal('180000.00'),
                'district': 'Kampala',
                'village': 'Ntinda',
                'total_rooms': 1,
                'available_rooms': 1,
                'gender_preference': 'male',
                'furnishing': 'unfurnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Luxury Apartment - Kololo',
                'description': 'Premium 2-bedroom apartment with swimming pool and gym.',
                'property_type': 'apartment',
                'target_audience': 'public',
                'rent_per_month': Decimal('2500000.00'),
                'district': 'Kampala',
                'village': 'Kololo',
                'total_rooms': 10,
                'available_rooms': 2,
                'gender_preference': 'any',
                'furnishing': 'fully_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Student Campus Heights',
                'description': 'Affordable student accommodation just 5 mins from campus.',
                'property_type': 'hostel',
                'target_audience': 'university_students',
                'rent_per_month': Decimal('300000.00'),
                'district': 'Kampala',
                'village': 'Kikoni',
                'total_rooms': 50,
                'available_rooms': 15,
                'gender_preference': 'any',
                'furnishing': 'semi_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Family Villa - Naalya',
                'description': 'Spacious 4-bedroom villa suitable for large families.',
                'property_type': 'villa',
                'target_audience': 'public',
                'rent_per_month': Decimal('1500000.00'),
                'district': 'Wakiso',
                'village': 'Naalya',
                'total_rooms': 4,
                'available_rooms': 1,
                'gender_preference': 'any',
                'furnishing': 'unfurnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Girls Only Hostel - Wandegeya',
                'description': 'Secure female-only hostel near the main gate.',
                'property_type': 'hostel',
                'target_audience': 'university_students',
                'rent_per_month': Decimal('400000.00'),
                'district': 'Kampala',
                'village': 'Wandegeya',
                'total_rooms': 30,
                'available_rooms': 5,
                'gender_preference': 'female',
                'furnishing': 'fully_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Entebbe Lake View Apartments',
                'description': 'Beautiful apartments with a view of Lake Victoria.',
                'property_type': 'apartment',
                'target_audience': 'public',
                'rent_per_month': Decimal('900000.00'),
                'district': 'Entebbe',
                'village': 'Kitoro',
                'total_rooms': 8,
                'available_rooms': 3,
                'gender_preference': 'any',
                'furnishing': 'semi_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Banda Student Rentals',
                'description': 'Cheap and affordable single rooms for KYU students.',
                'property_type': 'single_room',
                'target_audience': 'university_students',
                'rent_per_month': Decimal('150000.00'),
                'district': 'Kampala',
                'village': 'Banda',
                'total_rooms': 25,
                'available_rooms': 8,
                'gender_preference': 'any',
                'furnishing': 'unfurnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Bugema Self-Contained Rooms',
                'description': 'Self-contained rooms with private bath and kitchen access.',
                'property_type': 'self_contained',
                'target_audience': 'mixed',
                'rent_per_month': Decimal('300000.00'),
                'district': 'Kampala',
                'village': 'Bugema',
                'total_rooms': 15,
                'available_rooms': 8,
                'gender_preference': 'any',
                'furnishing': 'fully_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Jinja Executive Hostels',
                'description': 'Modern executive hostels with study areas and facilities.',
                'property_type': 'hostel',
                'target_audience': 'university_students',
                'rent_per_month': Decimal('350000.00'),
                'district': 'Jinja',
                'village': 'Jinja Town',
                'total_rooms': 40,
                'available_rooms': 12,
                'gender_preference': 'any',
                'furnishing': 'fully_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Entebbe Airport Guest House',
                'description': '24/7 guest house with airport transfer services.',
                'property_type': 'guest_house',
                'target_audience': 'public',
                'rent_per_month': Decimal('450000.00'),
                'district': 'Entebbe',
                'village': 'Kitoro',
                'total_rooms': 10,
                'available_rooms': 4,
                'gender_preference': 'any',
                'furnishing': 'fully_furnished',
                'is_approved': True,
                'is_active': True,
            },
            {
                'name': 'Wakiso Student Hostels',
                'description': 'Budget-friendly hostels near university with modern amenities.',
                'property_type': 'hostel',
                'target_audience': 'university_students',
                'rent_per_month': Decimal('200000.00'),
                'district': 'Wakiso',
                'village': 'Wakiso Town',
                'total_rooms': 60,
                'available_rooms': 20,
                'gender_preference': 'any',
                'furnishing': 'semi_furnished',
                'is_approved': True,
                'is_active': True,
            }
        ]

        # 3. Insert sample properties
        for prop_data in sample_properties:
            prop, prop_created = Property.objects.get_or_create(
                name=prop_data['name'],
                owner=owner,
                defaults=prop_data
            )
            if prop_created:
                self.stdout.write(self.style.SUCCESS(f"Created property: {prop.name}"))
            else:
                self.stdout.write(f"Property already exists: {prop.name}")

        # 4. Add sample images to properties
        sample_images = [
            {
                'property_name': 'Entebbe Lake View Apartments',
                'image_url': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
                'caption': 'Beautiful view of Lake Victoria from apartments',
                'is_primary': True,
                'image_type': 'exterior'
            },
            {
                'property_name': 'Kampala Luxury Apartments',
                'image_url': 'https://images.unsplash.com/photo-1502672260266-1c1de2d93688?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
                'caption': 'Modern luxury apartments in Kampala',
                'is_primary': True,
                'image_type': 'exterior'
            },
            {
                'property_name': 'Makerere Student Hostel',
                'image_url': 'https://images.unsplash.com/photo-1513694203232-719a280e022f?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
                'caption': 'Student hostel near Makerere University',
                'is_primary': True,
                'image_type': 'exterior'
            },
            {
                'property_name': 'Banda Student Rentals',
                'image_url': 'https://images.unsplash.com/photo-1493809842364-78817add7ffb?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
                'caption': 'Affordable student rooms in Banda',
                'is_primary': True,
                'image_type': 'interior'
            },
            {
                'property_name': 'Jinja Executive Hostels',
                'image_url': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
                'caption': 'Executive hostels in Jinja',
                'is_primary': True,
                'image_type': 'exterior'
            },
            {
                'property_name': 'Entebbe Airport Guest House',
                'image_url': 'https://images.unsplash.com/photo-1484154218962-a197022b5858?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
                'caption': 'Guest house near Entebbe Airport',
                'is_primary': True,
                'image_type': 'exterior'
            }
        ]

        for img_data in sample_images:
            try:
                property_obj = Property.objects.get(name=img_data['property_name'])
                PropertyImage.objects.get_or_create(
                    rental_property=property_obj,
                    defaults={
                        'image_url': img_data['image_url'],
                        'caption': img_data['caption'],
                        'is_primary': img_data['is_primary'],
                        'image_type': img_data['image_type']
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"Added image for: {img_data['property_name']}"))
            except Property.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Property not found: {img_data['property_name']}"))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
