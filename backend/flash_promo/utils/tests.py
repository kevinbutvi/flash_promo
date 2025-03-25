from decimal import Decimal
from unittest import TestCase
from unittest.mock import MagicMock
from .utils import (
    filter_promos_by_distance,
    filter_users_by_distance,
    get_eligible_users_for_promo,
)
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock
from users.models import ClientProfile, UserSegment

from django.contrib.auth.models import User
from unittest.mock import Mock


class TestFilterPromosByDistance(TestCase):
    def setUp(self):
        # Mock user profile with latitude and longitude
        self.user_profile = MagicMock()
        self.user_profile.latitude = 40.7128
        self.user_profile.longitude = -74.0060

        # Mock promo objects
        self.promo1 = MagicMock()
        self.promo1.product.store.latitude = 40.730610
        self.promo1.product.store.longitude = -73.935242
        self.promo1.max_distance_km = Decimal("10.0")

        self.promo2 = MagicMock()
        self.promo2.product.store.latitude = 41.7128
        self.promo2.product.store.longitude = -75.0060
        self.promo2.max_distance_km = Decimal("5.0")

        self.promo3 = MagicMock()
        self.promo3.product.store.latitude = 40.7128
        self.promo3.product.store.longitude = -74.0060
        self.promo3.max_distance_km = Decimal("0.5")

        self.promos = [self.promo1, self.promo2, self.promo3]

    def test_filter_promos_by_distance_with_valid_user_location(self):
        eligible_promos = filter_promos_by_distance(self.promos, self.user_profile)
        self.assertIn(self.promo1, eligible_promos)
        self.assertNotIn(self.promo2, eligible_promos)
        self.assertIn(self.promo3, eligible_promos)

    def test_filter_promos_by_distance_with_no_user_location(self):
        self.user_profile.latitude = None
        self.user_profile.longitude = None
        eligible_promos = filter_promos_by_distance(self.promos, self.user_profile)
        self.assertEqual(eligible_promos, [])

    def test_filter_promos_by_distance_with_empty_promos(self):
        eligible_promos = filter_promos_by_distance([], self.user_profile)
        self.assertEqual(eligible_promos, [])


class TestFilterUsersByDistance(TestCase):
    def setUp(self):
        # Mock user profiles
        self.user1 = MagicMock(latitude=40.7128, longitude=-74.0060)  # New York
        self.user2 = MagicMock(latitude=34.0522, longitude=-118.2437)  # Los Angeles
        self.user3 = MagicMock(latitude=41.8781, longitude=-87.6298)  # Chicago

        self.users = [self.user1, self.user2, self.user3]

        # Store location
        self.store_location = (40.730610, -73.935242)  # Near New York

    def test_filter_users_within_distance(self):
        max_distance = 50  # 50 km
        nearby_users = filter_users_by_distance(
            self.users, self.store_location, max_distance
        )

        # Only user1 (New York) should be within 50 km
        self.assertIn(self.user1, nearby_users)
        self.assertNotIn(self.user2, nearby_users)
        self.assertNotIn(self.user3, nearby_users)

    def test_filter_users_outside_distance(self):
        max_distance = 5  # 5 km
        nearby_users = filter_users_by_distance(
            self.users, self.store_location, max_distance
        )

        # No users should be within 5 km
        self.assertNotIn(self.user1, nearby_users)
        self.assertNotIn(self.user2, nearby_users)
        self.assertNotIn(self.user3, nearby_users)

    def test_empty_user_list(self):
        max_distance = 50  # 50 km
        nearby_users = filter_users_by_distance([], self.store_location, max_distance)

        # No users to filter, result should be empty
        self.assertEqual(nearby_users, [])


class ClientProfileModelTests(TestCase):
    def setUp(self):
        # Create UserSegments
        self.segment1 = UserSegment.objects.create(
            name="Segment 1", description="Test Segment 1"
        )
        self.segment2 = UserSegment.objects.create(
            name="Segment 2", description="Test Segment 2"
        )

        # Create Users and ClientProfiles
        self.user1 = User.objects.create(username="user1")
        self.profile1 = ClientProfile.objects.create(
            user=self.user1,
            latitude=10.0,
            longitude=20.0,
            last_notification_date=None,
        )
        self.profile1.segments.add(self.segment1)

        self.user2 = User.objects.create(username="user2")
        self.profile2 = ClientProfile.objects.create(
            user=self.user2,
            latitude=99.0,
            longitude=25.0,
            last_notification_date=timezone.now() - timedelta(days=2),
        )
        self.profile2.segments.add(self.segment1)

        self.user3 = User.objects.create(username="user3")
        self.profile3 = ClientProfile.objects.create(
            user=self.user3,
            latitude=15.00,
            longitude=25.00,
            last_notification_date=None,
        )
        self.profile3.segments.add(self.segment2)

        # Mock promo object
        self.promo = Mock()
        self.promo.segments = UserSegment.objects.filter(id__in=[self.segment1.id])

    def test_get_eligible_users_for_promo(self):
        eligible_users = get_eligible_users_for_promo(self.promo)

        # Assert user1 and user2 are eligible
        self.assertIn(self.profile1, eligible_users)
        self.assertIn(self.profile2, eligible_users)

        # Assert user3 is not eligible, another segment
        self.assertNotIn(self.profile3, eligible_users)

        # Assert distinct users are returned
        self.assertEqual(eligible_users.count(), 2)
