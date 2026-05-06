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
