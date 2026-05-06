from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from properties.models import Property

from .models import Booking
from .serializers import BookingCreateSerializer


class BookingCreateSerializerTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username='owner', password='pass', role='owner')
        self.tenant = User.objects.create_user(username='tenant', password='pass')

    def create_property(self, total_rooms=2, available_rooms=2):
        return Property.objects.create(
            owner=self.owner,
            name='Test Property',
            property_type='apartment',
            target_audience='public',
            description='A clean test property',
            address_line_1='123 Test Road',
            total_rooms=total_rooms,
            available_rooms=available_rooms,
            max_occupancy=5,
            rent_per_month='1500000.00',
            is_active=True,
            is_approved=True,
        )

    def serializer_data(self, property_obj, start_date, end_date):
        return {
            'rental_property': property_obj.id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'number_of_occupants': 1,
            'base_rent': '300000.00',
            'monthly_rent': '300000.00',
            'booking_type': 'online',
        }

    def create_existing_booking(self, property_obj, start_date, end_date, reference):
        Booking.objects.bulk_create([
            Booking(
                user=self.tenant,
                rental_property=property_obj,
                booking_reference=reference,
                start_date=start_date,
                end_date=end_date,
                number_of_occupants=1,
                base_rent=Decimal('300000.00'),
                monthly_rent=Decimal('300000.00'),
            )
        ])

    def test_property_level_booking_allows_overlap_when_rooms_remain(self):
        property_obj = self.create_property(total_rooms=2, available_rooms=2)
        start_date = timezone.now().date() + timedelta(days=1)
        end_date = start_date + timedelta(days=6)
        self.create_existing_booking(property_obj, start_date, end_date, 'BKEXISTING01')

        serializer = BookingCreateSerializer(data=self.serializer_data(property_obj, start_date, end_date))

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_property_level_booking_rejects_overlap_when_capacity_is_full(self):
        property_obj = self.create_property(total_rooms=1, available_rooms=1)
        start_date = timezone.now().date() + timedelta(days=1)
        end_date = start_date + timedelta(days=6)
        self.create_existing_booking(property_obj, start_date, end_date, 'BKEXISTING02')

        serializer = BookingCreateSerializer(data=self.serializer_data(property_obj, start_date, end_date))

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            'Property is fully booked for these dates',
            [str(error) for error in serializer.errors['non_field_errors']],
        )

    def test_property_level_booking_allows_same_day_checkout_and_checkin(self):
        property_obj = self.create_property(total_rooms=1, available_rooms=1)
        start_date = timezone.now().date() + timedelta(days=1)
        end_date = start_date + timedelta(days=6)
        self.create_existing_booking(property_obj, start_date, end_date, 'BKEXISTING03')

        serializer = BookingCreateSerializer(
            data=self.serializer_data(property_obj, end_date, end_date + timedelta(days=3))
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_property_level_booking_can_be_saved_without_room(self):
        property_obj = self.create_property(total_rooms=1, available_rooms=1)
        start_date = timezone.now().date() + timedelta(days=1)
        end_date = start_date + timedelta(days=6)
        serializer = BookingCreateSerializer(data=self.serializer_data(property_obj, start_date, end_date))

        self.assertTrue(serializer.is_valid(), serializer.errors)
        booking = serializer.save(user=self.tenant)

        self.assertIsNone(booking.room)
        self.assertEqual(booking.rental_property, property_obj)
