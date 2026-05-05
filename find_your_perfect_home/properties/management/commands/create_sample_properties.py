from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from properties.models import Property, PropertyImage
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample properties for testing'

    def handle(self, *args, **options):
        # Get or create a sample user as property owner
        user, created = User.objects.get_or_create(
            email='owner@renthu.ug',
            defaults={
                'first_name': 'Property',
                'last_name': 'Owner',
                'username': 'owner@renthu.ug',
                'role': 'owner'
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created sample owner user'))

        # Sample properties data
        sample_properties = [
            {
                'name': 'Modern Studio Apartment - Kampala',
                'description': 'A beautiful modern studio apartment in the heart of Kampala with all amenities.',
                'property_type': 'studio',
                'target_audience': 'public',
                'rent_per_month': Decimal('450000'),
                'district': 'Kampala',
                'county': 'Central',
                'village': 'Kampala City Center',
                'total_rooms': 1,
                'available_rooms': 1,
                'gender_preference': 'any',
                'furnishing': 'furnished',
                'is_active': True,
                'is_approved': True,
            },
            {
                'name': 'University Hostel - Makerere',
                'description': 'Perfect hostel for Makerere University students with secure environment.',
                'property_type': 'hostel',
                'target_audience': 'university',
                'rent_per_month': Decimal('250000'),
                'district': 'Kampala',
                'county': 'Kawempe',
                'village': 'Makerere',
                'total_rooms': 20,
                'available_rooms': 5,
                'gender_preference': 'any',
                'furnishing': 'semi_furnished',
                'is_active': True,
                'is_approved': True,
            },
            {
                'name': 'Self-Contained House - Muyenga',
                'description': 'Spacious self-contained house in upscale Muyenga neighborhood.',
                'property_type': 'self_contained',
                'target_audience': 'public',
                'rent_per_month': Decimal('800000'),
                'district': 'Kampala',
                'county': 'Makindye',
                'village': 'Muyenga',
                'total_rooms': 3,
                'available_rooms': 1,
                'gender_preference': 'any',
                'furnishing': 'furnished',
                'is_active': True,
                'is_approved': True,
            },
            {
                'name': 'Single Room - Ntinda',
                'description': 'Affordable single room in quiet Ntinda neighborhood.',
                'property_type': 'single_room',
                'target_audience': 'public',
                'rent_per_month': Decimal('180000'),
                'district': 'Kampala',
                'county': 'Nakawa',
                'village': 'Ntinda',
                'total_rooms': 1,
                'available_rooms': 1,
                'gender_preference': 'male',
                'furnishing': 'unfurnished',
                'is_active': True,
                'is_approved': True,
            },
            {
                'name': 'Double Room - Kansanga',
                'description': 'Comfortable double room sharing in Kansanga near Gaba Road.',
                'property_type': 'double_room',
                'target_audience': 'university',
                'rent_per_month': Decimal('320000'),
                'district': 'Kampala',
                'county': 'Makindye',
                'village': 'Kansanga',
                'total_rooms': 2,
                'available_rooms': 1,
                'gender_preference': 'female',
                'furnishing': 'furnished',
                'is_active': True,
                'is_approved': True,
            }
        ]

        created_count = 0
        for prop_data in sample_properties:
            # Check if property already exists
            if Property.objects.filter(name=prop_data['name']).exists():
                self.stdout.write(self.style.WARNING(f"Property '{prop_data['name']}' already exists"))
                continue
            
            # Create property
            property = Property.objects.create(
                owner=user,
                **prop_data
            )
            
            # Add sample images
            sample_images = [
                'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
                'https://images.unsplash.com/photo-1502672260266-1c1de2d93688?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80',
                'https://images.unsplash.com/photo-1513694203232-719a280e022f?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80'
            ]
            
            for i, image_url in enumerate(sample_images):
                PropertyImage.objects.create(
                    rental_property=property,
                    image=image_url,
                    is_primary=(i == 0)
                )
            
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Created property: {property.name}"))

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample properties')
        )
