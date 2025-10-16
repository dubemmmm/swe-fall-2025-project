from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import User
from .location_utils import get_client_ip, reverse_geocode, geocode
from unittest.mock import patch, MagicMock


class UserModelTests(TestCase):
    """Test cases for the User model"""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'profile_name': 'Test User',
            'location': 'New York, NY',
            'latitude': Decimal('40.712776'),
            'longitude': Decimal('-74.005974'),
            'phone_number': '555-123-4567',
            'bio': 'Test bio for testing purposes'
        }

    def test_create_user_with_location(self):
        """Test creating a user with location data"""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            profile_name=self.user_data['profile_name'],
            location=self.user_data['location'],
            latitude=self.user_data['latitude'],
            longitude=self.user_data['longitude']
        )

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.profile_name, 'Test User')
        self.assertEqual(user.location, 'New York, NY')
        self.assertEqual(user.latitude, Decimal('40.712776'))
        self.assertEqual(user.longitude, Decimal('-74.005974'))
        self.assertTrue(user.check_password('testpass123'))

    def test_create_user_without_location(self):
        """Test creating a user without location data"""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            profile_name='Test User 2',
            location='Unknown',
            latitude=None,
            longitude=None
        )

        self.assertEqual(user.username, 'testuser2')
        self.assertIsNone(user.latitude)
        self.assertIsNone(user.longitude)

    def test_user_string_representation(self):
        """Test the __str__ method of User model"""
        user = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123',
            profile_name='Test User 3'
        )

        self.assertEqual(str(user), 'testuser3')


class UserRegistrationTests(TestCase):
    """Test cases for user registration functionality"""

    def setUp(self):
        """Set up test client and URLs"""
        self.client = Client()
        self.register_url = reverse('register')

    def test_registration_page_loads(self):
        """Test that registration page loads successfully"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_successful_registration_with_location(self):
        """Test successful user registration with location data"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'profile_name': 'New User',
            'location': 'Los Angeles, CA',
            'latitude': '34.052235',
            'longitude': '-118.243683',
            'phone_number': '555-987-6543',
            'bio': 'I love pets!'
        })

        # Should redirect to home after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.profile_name, 'New User')
        self.assertEqual(user.location, 'Los Angeles, CA')
        self.assertEqual(user.latitude, Decimal('34.052235'))

    def test_registration_with_duplicate_username(self):
        """Test registration fails with duplicate username"""
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123',
            profile_name='Existing User'
        )

        # Try to register with same username
        response = self.client.post(self.register_url, {
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'password': 'newpass123',
            'profile_name': 'New User',
            'location': 'Boston, MA'
        })

        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        # Should show error message
        messages = list(response.context['messages'])
        self.assertTrue(any('already taken' in str(m) for m in messages))

    def test_registration_with_duplicate_email(self):
        """Test registration fails with duplicate email"""
        # Create existing user
        User.objects.create_user(
            username='user1',
            email='duplicate@example.com',
            password='pass123',
            profile_name='User One'
        )

        # Try to register with same email
        response = self.client.post(self.register_url, {
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'newpass123',
            'profile_name': 'User Two',
            'location': 'Chicago, IL'
        })

        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        # Should show error message
        messages = list(response.context['messages'])
        self.assertTrue(any('already registered' in str(m) for m in messages))

    def test_registration_missing_required_fields(self):
        """Test registration fails when required fields are missing"""
        response = self.client.post(self.register_url, {
            'username': 'incomplete',
            'email': 'incomplete@example.com',
            # Missing password, profile_name, location
        })

        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('required fields' in str(m) for m in messages))


class UserLoginTests(TestCase):
    """Test cases for user login functionality"""

    def setUp(self):
        """Set up test client, user, and URLs"""
        self.client = Client()
        self.login_url = reverse('login')

        # Create test user
        self.user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='loginpass123',
            profile_name='Login User',
            location='Seattle, WA'
        )

    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_successful_login(self):
        """Test successful user login"""
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'loginpass123'
        })

        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        # User should be logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_wrong_password(self):
        """Test login fails with incorrect password"""
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'wrongpassword'
        })

        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        # User should not be logged in
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        # Should show error message
        messages = list(response.context['messages'])
        self.assertTrue(any('Invalid' in str(m) for m in messages))

    def test_login_with_nonexistent_user(self):
        """Test login fails with non-existent username"""
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'somepassword'
        })

        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        # User should not be logged in
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class UserLogoutTests(TestCase):
    """Test cases for user logout functionality"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.logout_url = reverse('logout')

        # Create and login test user
        self.user = User.objects.create_user(
            username='logoutuser',
            email='logout@example.com',
            password='logoutpass123',
            profile_name='Logout User'
        )
        self.client.login(username='logoutuser', password='logoutpass123')

    def test_successful_logout(self):
        """Test successful user logout"""
        # User should be logged in initially
        self.assertTrue(self.user.is_authenticated)

        # Logout
        response = self.client.get(self.logout_url)

        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))


class UserProfileTests(TestCase):
    """Test cases for user profile functionality"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.profile_url = reverse('profile')

        # Create test user
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='profilepass123',
            profile_name='Profile User',
            location='Portland, OR',
            bio='I love dogs and cats!'
        )

    def test_profile_page_requires_login(self):
        """Test that profile page requires authentication"""
        response = self.client.get(self.profile_url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_view_profile(self):
        """Test that logged-in user can view their profile"""
        self.client.login(username='profileuser', password='profilepass123')
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertEqual(response.context['user'].username, 'profileuser')


class LocationUtilityTests(TestCase):
    """Test cases for location utility functions"""

    def test_get_client_ip_without_proxy(self):
        """Test extracting IP address from request without proxy"""
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '192.168.1.1'}

        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_with_proxy(self):
        """Test extracting IP address from request with proxy"""
        request = MagicMock()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '203.0.113.195, 70.41.3.18',
            'REMOTE_ADDR': '192.168.1.1'
        }

        ip = get_client_ip(request)
        self.assertEqual(ip, '203.0.113.195')

    def test_geocode_success(self):
        """Test successful geocoding of an address"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'lat': '40.7127281',
                'lon': '-74.0060152',
                'display_name': 'New York, NY, United States'
            }
        ]

        with patch('users.location_utils.requests.get', return_value=mock_response):
            result = geocode('New York, NY')

            self.assertIsNotNone(result)
            self.assertEqual(result['latitude'], Decimal('40.7127281'))
            self.assertEqual(result['longitude'], Decimal('-74.0060152'))
            self.assertEqual(result['display_name'], 'New York, NY, United States')

    def test_geocode_no_results(self):
        """Test geocoding with no results found"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch('users.location_utils.requests.get', return_value=mock_response):
            result = geocode('InvalidAddressXYZ123')

            self.assertIsNone(result)


class UserProfileEditTests(TestCase):
    """Test cases for user profile editing functionality"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.edit_profile_url = reverse('edit_profile')

        # Create test user
        self.user = User.objects.create_user(
            username='edituser',
            email='edit@example.com',
            password='editpass123',
            profile_name='Edit User',
            location='Boston, MA',
            latitude=Decimal('42.360081'),
            longitude=Decimal('-71.058884')
        )

    def test_edit_profile_page_requires_login(self):
        """Test that edit profile page requires authentication"""
        response = self.client.get(self.edit_profile_url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_edit_profile_page_loads(self):
        """Test that edit profile page loads successfully for logged-in user"""
        self.client.login(username='edituser', password='editpass123')
        response = self.client.get(self.edit_profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/edit_profile.html')
        self.assertEqual(response.context['user'].username, 'edituser')

    def test_successful_profile_update_with_manual_address(self):
        """Test successful profile update using manual address entry with geocoding"""
        self.client.login(username='edituser', password='editpass123')

        # Mock geocoding API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'lat': '34.052235',
                'lon': '-118.243683',
                'display_name': 'Los Angeles, CA, United States'
            }
        ]

        with patch('users.location_utils.requests.get', return_value=mock_response):
            response = self.client.post(self.edit_profile_url, {
                'profile_name': 'Updated Name',
                'phone_number': '555-999-8888',
                'bio': 'Updated bio text',
                'location': '123 Main St, Los Angeles, CA',
                'use_manual_address': 'true'
            })

        # Should redirect to profile page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

        # Check user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile_name, 'Updated Name')
        self.assertEqual(self.user.phone_number, '555-999-8888')
        self.assertEqual(self.user.bio, 'Updated bio text')
        self.assertEqual(self.user.location, 'Los Angeles, CA, United States')
        self.assertEqual(self.user.latitude, Decimal('34.052235'))
        self.assertEqual(self.user.longitude, Decimal('-118.243683'))

    def test_successful_profile_update_with_browser_geolocation(self):
        """Test successful profile update using browser geolocation"""
        self.client.login(username='edituser', password='editpass123')

        response = self.client.post(self.edit_profile_url, {
            'profile_name': 'Geo User',
            'phone_number': '555-777-6666',
            'bio': 'I love pets',
            'latitude': '37.774929',
            'longitude': '-122.419418',
            'location': 'San Francisco, CA',
            'use_manual_address': 'false'
        })

        # Should redirect to profile page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

        # Check user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile_name, 'Geo User')
        self.assertEqual(self.user.location, 'San Francisco, CA')
        self.assertEqual(self.user.latitude, Decimal('37.774929'))
        self.assertEqual(self.user.longitude, Decimal('-122.419418'))

    def test_profile_update_with_failed_geocoding(self):
        """Test profile update when geocoding fails"""
        self.client.login(username='edituser', password='editpass123')

        # Mock geocoding API to return no results
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch('users.location_utils.requests.get', return_value=mock_response):
            response = self.client.post(self.edit_profile_url, {
                'profile_name': 'Updated Name',
                'location': 'InvalidAddressXYZ123',
                'use_manual_address': 'true'
            })

        # Should stay on edit page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/edit_profile.html')

        # Should show error message
        messages = list(response.context['messages'])
        self.assertTrue(any('Could not find that address' in str(m) for m in messages))

        # User should not be updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile_name, 'Edit User')  # Original name unchanged

    def test_profile_update_missing_required_fields(self):
        """Test profile update fails when required fields are missing"""
        self.client.login(username='edituser', password='editpass123')

        response = self.client.post(self.edit_profile_url, {
            # Missing profile_name
            'phone_number': '555-999-8888',
            'bio': 'Updated bio'
        })

        # Should stay on edit page
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('required' in str(m).lower() for m in messages))

    def test_profile_update_without_location_change(self):
        """Test updating profile without changing location"""
        self.client.login(username='edituser', password='editpass123')

        response = self.client.post(self.edit_profile_url, {
            'profile_name': 'Just Name Change',
            'phone_number': self.user.phone_number,
            'bio': self.user.bio,
            'location': self.user.location,
            'use_manual_address': 'true'
        })

        # Should redirect to profile page
        self.assertEqual(response.status_code, 302)

        # Check only profile name was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile_name, 'Just Name Change')
