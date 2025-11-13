"""
Test cases for Issue #5: Profile Edit URL Name Error

Problem: Profile edit view redirects to 'profile' instead of 'users:profile'
causing NoReverseMatch error after successful profile update.

This test file verifies the fix for the URL namespacing issue.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Issue5ProfileEditRedirectTests(TestCase):
    """
    Test cases for Issue #5: Profile Edit Redirect Error

    Problem: After successful profile edit, view redirects to 'profile'
    but URL is namespaced as 'users:profile', causing:
    "Reverse for 'profile' not found. 'profile' is not a valid view function or pattern name."

    Expected: Should redirect to 'users:profile'
    """

    def setUp(self):
        """Set up test client and create test user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            profile_name='Test User',
            location='Los Angeles, CA',
            latitude=Decimal('34.0522'),
            longitude=Decimal('-118.2437')
        )
        self.edit_profile_url = reverse('users:edit_profile')
        self.profile_url = reverse('users:profile')

    def test_profile_edit_redirects_to_correct_url(self):
        """Test that profile edit redirects to the correct namespaced URL"""
        # Login
        self.client.login(username='testuser', password='testpass123')

        # Submit profile edit
        response = self.client.post(self.edit_profile_url, {
            'profile_name': 'Updated Test User',
            'phone_number': '555-1234',
            'bio': 'Test bio',
            'location': 'Los Angeles, CA',
            'latitude': '34.0522',
            'longitude': '-118.2437',
        }, follow=False)  # Don't follow redirects

        # Should return 302 (redirect status)
        self.assertEqual(response.status_code, 302)

        # Should NOT raise NoReverseMatch error
        # If this test passes, it means redirect is working

        # Verify the redirect target is valid
        self.assertIn('/users/profile', response.url)

    def test_profile_edit_updates_and_redirects_successfully(self):
        """Test that profile edit saves changes AND redirects without error"""
        # Login
        self.client.login(username='testuser', password='testpass123')

        # Submit profile edit
        response = self.client.post(self.edit_profile_url, {
            'profile_name': 'Updated Name',
            'phone_number': '555-9999',
            'bio': 'New bio text',
            'location': 'Los Angeles, CA',
            'latitude': '34.0522',
            'longitude': '-118.2437',
        }, follow=True)  # Follow redirects

        # Should successfully redirect to profile page
        self.assertEqual(response.status_code, 200)

        # Verify we're on the profile page
        self.assertTemplateUsed(response, 'users/profile.html')

        # Verify user data was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile_name, 'Updated Name')
        self.assertEqual(self.user.phone_number, '555-9999')
        self.assertEqual(self.user.bio, 'New bio text')

        # Verify success message appears
        messages = list(response.context['messages'])
        self.assertTrue(any('Profile updated successfully' in str(m) for m in messages))

    def test_profile_edit_with_manual_address(self):
        """Test profile edit with manual address entry (tests geocoding path)"""
        # Login
        self.client.login(username='testuser', password='testpass123')

        # Submit profile edit with manual address
        response = self.client.post(self.edit_profile_url, {
            'profile_name': 'Test User',
            'phone_number': '555-0000',
            'bio': 'Test bio',
            'location': 'San Francisco, CA',
            'use_manual_address': 'true',
        }, follow=True)

        # Should redirect successfully (even if geocoding fails)
        self.assertEqual(response.status_code, 200)

        # Should be on profile or edit page (depends on geocoding success)
        # The important thing is no NoReverseMatch error

    def test_profile_edit_without_changes(self):
        """Test that editing profile without changes still redirects correctly"""
        # Login
        self.client.login(username='testuser', password='testpass123')

        # Submit profile edit with same data
        response = self.client.post(self.edit_profile_url, {
            'profile_name': 'Test User',  # Same as original
            'location': 'Los Angeles, CA',
            'latitude': '34.0522',
            'longitude': '-118.2437',
        }, follow=False)

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Should redirect to profile page
        self.assertIn('/users/profile', response.url)

    def test_profile_edit_requires_authentication(self):
        """Test that profile edit requires login (sanity check)"""
        # Don't login
        response = self.client.post(self.edit_profile_url, {
            'profile_name': 'Hacker',
        })

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login', response.url)

    def test_profile_edit_missing_required_fields(self):
        """Test that profile edit validates required fields"""
        # Login
        self.client.login(username='testuser', password='testpass123')

        # Submit profile edit without profile_name (required)
        response = self.client.post(self.edit_profile_url, {
            'phone_number': '555-1111',
            # Missing profile_name
        })

        # Should stay on edit page (not redirect)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/edit_profile.html')

        # Should show error message
        messages = list(response.context['messages'])
        self.assertTrue(any('required' in str(m).lower() for m in messages))
