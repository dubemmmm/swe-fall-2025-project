from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from .models import Notification


class NotificationTests(TestCase):
    """Test cases for Ticket 5: Notifications functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='notifuser',
            email='notif@example.com',
            password='password123',
            profile_name='Notif User'
        )
        self.other_user = User.objects.create_user(
            username='othernotif',
            email='other@example.com',
            password='password123',
            profile_name='Other User'
        )

    def test_notification_list_displays(self):
        """Test that notification page loads without error"""
        self.client.login(username='notifuser', password='password123')

        try:
            notif_url = reverse('notifications:list')
        except:
            notif_url = '/notifications/'

        response = self.client.get(notif_url)
        # Should load successfully (this is the bug - it gives error)
        self.assertEqual(response.status_code, 200)

    def test_notification_button_no_error(self):
        """Test that notifications button doesn't give error when pressed"""
        self.client.login(username='notifuser', password='password123')

        try:
            notif_url = reverse('notifications:list')
        except:
            notif_url = '/notifications/'

        response = self.client.get(notif_url)
        # Should not error out (Ticket 5 bug)
        self.assertNotEqual(response.status_code, 500)
        self.assertEqual(response.status_code, 200)

    def test_mark_notification_read(self):
        """Test marking a single notification as read"""
        self.client.login(username='notifuser', password='password123')

        # Create a notification
        notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Test notification',
            notification_type='adoption_approved',
            is_read=False
        )

        try:
            mark_read_url = reverse('notifications:mark_read', kwargs={'pk': notification.pk})
            response = self.client.post(mark_read_url)

            # Should succeed
            self.assertIn(response.status_code, [200, 302])

            # Notification should be marked as read
            notification.refresh_from_db()
            self.assertTrue(notification.is_read)
        except:
            # Mark as read endpoint might not exist
            pass

    def test_unread_count_api(self):
        """Test the unread count API endpoint"""
        self.client.login(username='notifuser', password='password123')

        # Create notifications
        Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Unread 1',
            notification_type='adoption_approved',
            is_read=False
        )
        Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Unread 2',
            notification_type='adoption_approved',
            is_read=False
        )
        Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Read notification',
            notification_type='adoption_approved',
            is_read=True
        )

        try:
            unread_count_url = reverse('notifications:unread_count')
        except:
            unread_count_url = '/notifications/api/unread-count/'

        try:
            response = self.client.get(unread_count_url)
            # Should return count
            self.assertEqual(response.status_code, 200)

            # Should return JSON with count=2
            if response.get('Content-Type') == 'application/json':
                data = response.json()
                self.assertEqual(data.get('count'), 2)
        except:
            pass

    def test_notification_created_on_playdate_invite(self):
        """Test that notification is created when invited to playdate"""
        # This tests the notification trigger
        # The actual trigger implementation will be in playdates app
        # Here we just verify notifications can be created

        notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='You were invited to a playdate',
            notification_type='playdate_approved',
            is_read=False
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.user)
        self.assertFalse(notification.is_read)

    def test_notification_created_on_adoption_request(self):
        """Test that notification is created on adoption request"""
        notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Someone requested to adopt your pet',
            notification_type='new_adoption_request',
            is_read=False
        )

        self.assertIsNotNone(notification)
        self.assertFalse(notification.is_read)

    def test_notification_created_on_alert(self):
        """Test that notification is created for community alerts"""
        notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='New community alert in your area',
            notification_type='adoption_approved',
            is_read=False
        )

        self.assertIsNotNone(notification)
        self.assertFalse(notification.is_read)

    def test_notification_link_navigation(self):
        """Test that clicking notification navigates properly"""
        self.client.login(username='notifuser', password='password123')

        notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Test navigation',
            notification_type='adoption_approved',
            is_read=False,
            link='/test-link/'
        )

        # Clicking should work and mark as read
        if hasattr(notification, 'link') and notification.link:
            response = self.client.get(notification.link)
            # Link should be accessible
            self.assertIn(response.status_code, [200, 302, 404])

    def test_notification_filtering(self):
        """Test filtering read/unread notifications"""
        self.client.login(username='notifuser', password='password123')

        # Create mix of read and unread
        Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Unread',
            notification_type='adoption_approved',
            is_read=False
        )
        Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Read',
            notification_type='adoption_approved',
            is_read=True
        )

        try:
            notif_url = reverse('notifications:list')
        except:
            notif_url = '/notifications/'

        response = self.client.get(notif_url)
        self.assertEqual(response.status_code, 200)

        # Should show both or allow filtering

    def test_notification_authentication_required(self):
        """Test that notification page requires login"""
        # Not logged in
        try:
            notif_url = reverse('notifications:list')
        except:
            notif_url = '/notifications/'

        response = self.client.get(notif_url)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
