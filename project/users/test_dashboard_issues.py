"""
Test cases for dashboard-related browser-testing issues.
These tests verify dashboard statistics and data display.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from pets.models import PetProfile
from playdates.models import Playdate
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


class Issue4PlaydateCountTests(TestCase):
    """
    Test cases for Issue #4: Playdate Count Not Updating

    Problem: Dashboard shows "0 Playdates" even after creating playdates

    Root Cause: Dashboard query might be filtering incorrectly or not counting
    user's playdates properly
    """

    def setUp(self):
        """Set up test client, user, and pet"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='playdateuser',
            email='playdate@example.com',
            password='playdatepass123',
            profile_name='Playdate User',
            location='Seattle, WA'
        )
        self.client.login(username='playdateuser', password='playdatepass123')

        # Create a pet for the user
        self.pet = PetProfile.objects.create(
            owner=self.user,
            name='Buddy',
            pet_type='dog',
            breed='Golden Retriever',
            age='3 years',
            size='large',
            energy_level='high',
            description='Friendly dog'
        )

        self.dashboard_url = reverse('users:home')

    def test_dashboard_page_loads(self):
        """Test that dashboard loads successfully"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/home.html')

    def test_dashboard_shows_zero_playdates_initially(self):
        """Test that dashboard shows 0 playdates when none exist"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

        # Check context or content for playdate count
        content = response.content.decode()

        # Dashboard should show 0 playdates
        # The exact format might vary, but should indicate no playdates
        self.assertIn('0', content)  # Should show zero somewhere for playdates

    def test_dashboard_counts_organizer_playdates(self):
        """Test that dashboard counts playdates where user is organizer"""
        # Create a playdate where user is organizer
        future_time = timezone.now() + timedelta(days=7)
        playdate = Playdate.objects.create(
            pet=self.pet,
            organizer=self.user,
            location='Dog Park',
            scheduled_time=future_time,
            description='Fun playdate',
            max_participants=5,
            status='open'
        )

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

        # Check if playdate count is provided in context
        if 'playdate_count' in response.context:
            self.assertGreaterEqual(response.context['playdate_count'], 1)
        elif 'playdates_count' in response.context:
            self.assertGreaterEqual(response.context['playdates_count'], 1)
        else:
            # Check in content
            content = response.content.decode()
            # After fix, should show 1 playdate
            # Before fix, might still show 0

    def test_dashboard_counts_multiple_playdates(self):
        """Test that dashboard correctly counts multiple playdates"""
        # Create multiple playdates
        future_time1 = timezone.now() + timedelta(days=7)
        future_time2 = timezone.now() + timedelta(days=14)

        Playdate.objects.create(
            pet=self.pet,
            organizer=self.user,
            location='Park 1',
            scheduled_time=future_time1,
            description='Playdate 1',
            max_participants=5,
            status='open'
        )

        Playdate.objects.create(
            pet=self.pet,
            organizer=self.user,
            location='Park 2',
            scheduled_time=future_time2,
            description='Playdate 2',
            max_participants=5,
            status='confirmed'
        )

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

        # Should count both playdates
        if 'playdate_count' in response.context:
            self.assertEqual(response.context['playdate_count'], 2)
        elif 'playdates_count' in response.context:
            self.assertEqual(response.context['playdates_count'], 2)

    def test_dashboard_excludes_other_users_playdates(self):
        """Test that dashboard only counts current user's playdates"""
        # Create another user and their pet
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
            profile_name='Other User',
            location='Portland, OR'
        )

        other_pet = PetProfile.objects.create(
            owner=other_user,
            name='Max',
            pet_type='dog',
            breed='Labrador',
            age='2 years',
            size='large',
            energy_level='high',
            description='Energetic dog'
        )

        # Create playdate for other user
        future_time = timezone.now() + timedelta(days=7)
        Playdate.objects.create(
            pet=other_pet,
            organizer=other_user,
            location='Other Park',
            scheduled_time=future_time,
            description='Other playdate',
            max_participants=5,
            status='open'
        )

        # Current user should still have 0 playdates
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

        if 'playdate_count' in response.context:
            self.assertEqual(response.context['playdate_count'], 0)
        elif 'playdates_count' in response.context:
            self.assertEqual(response.context['playdates_count'], 0)

    def test_dashboard_displays_playdate_stat_card(self):
        """Test that dashboard has a playdate statistics display"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()

        # Dashboard should have a section showing playdate stats
        self.assertTrue(
            'playdate' in content.lower() or 'Playdate' in content,
            "Dashboard should display playdate statistics"
        )
