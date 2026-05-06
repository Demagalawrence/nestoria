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

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
