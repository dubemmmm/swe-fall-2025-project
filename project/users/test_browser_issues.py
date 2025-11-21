"""
Test cases for browser-testing issues found during Playwright MCP testing.
These tests verify fixes for critical issues discovered during manual browser testing.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Issue1RegistrationRedirectTests(TestCase):
    """
    Test cases for Issue #1: Registration Redirect Error

    Problem: After successful registration, the app throws:
    "Reverse for 'home' not found. 'home' is not a valid view function or pattern name."

    Root Cause: Registration view redirects to 'home' but the URL is namespaced as 'users:home'
    """

    def setUp(self):
        """Set up test client and URLs"""
        self.client = Client()
        self.register_url = reverse('users:register')

    def test_registration_redirects_correctly(self):
        """Test that successful registration redirects to the correct home URL"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'profile_name': 'New User',
            'location': 'San Francisco, CA',
        }, follow=False)  # Don't follow redirects

        # Should return 302 (redirect status)
        self.assertEqual(response.status_code, 302)

        # Should NOT raise NoReverseMatch error
        # If this test passes, it means redirect is working

        # Verify the redirect target is valid
        self.assertIn('/users/home', response.url)

    def test_registration_creates_user_and_redirects(self):
        """Test that registration creates user AND successfully redirects"""
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'profile_name': 'Test User',
            'location': 'New York, NY',
        }, follow=True)  # Follow redirects

        # Should successfully redirect to home page
        self.assertEqual(response.status_code, 200)

        # User should be created
        self.assertTrue(User.objects.filter(username='testuser').exists())

        # User should be logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Should show success message
        messages = list(response.context['messages'])
        self.assertTrue(any('Welcome' in str(m) for m in messages))

    def test_registration_error_does_not_create_user(self):
        """Test that registration errors don't create users"""
        # Try registering with missing fields
        response = self.client.post(self.register_url, {
            'username': 'incomplete',
            'email': 'incomplete@example.com',
            # Missing required fields
        })

        # Should stay on registration page
        self.assertEqual(response.status_code, 200)

        # User should NOT be created
        self.assertFalse(User.objects.filter(username='incomplete').exists())
