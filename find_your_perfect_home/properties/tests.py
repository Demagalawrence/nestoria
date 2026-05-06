from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Property


class PropertyModelTests(TestCase):
    def test_string_representation_uses_existing_location_fields(self):
        User = get_user_model()
        owner = User.objects.create_user(username='owner', password='pass', role='owner')
        property_obj = Property.objects.create(
            owner=owner,
            name='Kampala Heights',
            property_type='apartment',
            target_audience='public',
            description='A clean test property',
            address_line_1='123 Test Road',
            district='Kampala',
            total_rooms=2,
            available_rooms=2,
            rent_per_month='1500000.00',
        )

        self.assertEqual(str(property_obj), 'Kampala Heights - Kampala')
