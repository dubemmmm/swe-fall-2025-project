from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
from django.apps import apps
from django.db import IntegrityError
from .models import MessageThread, Message

User = get_user_model()


def url_or(name, fallback):
    """
    Try reverse(), fallback to hardcoded URL if route doesn't exist.
    Prevents NoReverseMatch errors when views aren't implemented yet.
    """
    try:
        return reverse(name)
    except NoReverseMatch:
        return fallback


class MessageModelTests(TestCase):
    """Test cases for the Message model"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            profile_name='User One'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            profile_name='User Two'
        )
        self.thread = MessageThread.objects.create(
            user1=self.user1,
            user2=self.user2
        )

    def test_message_timestamp_auto_set(self):
        """
        Test that message timestamp is automatically set on creation.
        From Test Scenario 5.2: "message time-stamped".
        This test should PASS because the model has auto_now_add=True.
        """
        message = Message.objects.create(
            thread=self.thread,
            sender=self.user1,
            text='Test message'
        )
        self.assertIsNotNone(message.timestamp)


class MessageThreadModelTests(TestCase):
    """Test cases for the MessageThread model"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='testpass123',
            profile_name='Alice'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='testpass123',
            profile_name='Bob'
        )

    def test_thread_unique_participants(self):
        """
        Test that duplicate threads between same users are prevented.
        This test should PASS because the model has unique_together=['user1', 'user2'].
        """
        # Create first thread
        MessageThread.objects.create(user1=self.user1, user2=self.user2)

        # Attempt to create duplicate should raise IntegrityError
        with self.assertRaises(IntegrityError):
            MessageThread.objects.create(user1=self.user1, user2=self.user2)


class SendMessageTests(TestCase):
    """Test cases for sending messages"""

    def setUp(self):
        """Set up test client and users"""
        self.client = Client()

        self.user1 = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123',
            profile_name='Sender'
        )
        self.user2 = User.objects.create_user(
            username='recipient',
            email='recipient@example.com',
            password='testpass123',
            profile_name='Recipient'
        )
        self.user3 = User.objects.create_user(
            username='outsider',
            email='outsider@example.com',
            password='testpass123',
            profile_name='Outsider'
        )

        self.thread = MessageThread.objects.create(
            user1=self.user1,
            user2=self.user2
        )

    def test_send_message_requires_login(self):
        """
        Spec requirement: User must be authenticated to send messages.
        This test will FAIL because the view doesn't exist yet (404).
        """
        # Assuming URL pattern: /messaging/threads/<thread_id>/send/
        send_message_url = f'/messaging/threads/{self.thread.id}/send/'

        response = self.client.post(send_message_url, {
            'text': 'Unauthenticated message'
        })

        # Should redirect to login or return 403 - but will get 404
        self.assertIn(response.status_code, [302, 403])

    def test_send_message_requires_text_or_photo(self):
        """
        Spec requirement: Message must have text or photo (at least one).
        From Test Scenario 5.2: Shows attachment icon and photo capability.
        This test will FAIL because either:
        1. View doesn't exist (404), or
        2. View doesn't validate text/photo requirement
        """
        self.client.login(username='sender', password='testpass123')
        send_message_url = f'/messaging/threads/{self.thread.id}/send/'

        # Try to send message with empty text and no photo
        response = self.client.post(send_message_url, {
            'text': '',
            # No photo uploaded
        })

        # Should stay on page with error or return 400
        self.assertIn(response.status_code, [200, 400])

        # Message should not be created
        self.assertEqual(Message.objects.filter(thread=self.thread).count(), 0)

    def test_send_message_requires_thread_participation(self):
        """
        Spec requirement: User can only send message within thread they participate in.
        Security requirement to prevent unauthorized messaging.
        This test will FAIL because either:
        1. View doesn't exist (404), or
        2. View doesn't check if sender is thread participant (user1 or user2)
        """
        # Login as user3 who is NOT part of this thread
        self.client.login(username='outsider', password='testpass123')
        send_message_url = f'/messaging/threads/{self.thread.id}/send/'

        response = self.client.post(send_message_url, {
            'text': 'Unauthorized message from outsider'
        })

        # Should return 403 Forbidden - but will get 404 or accept message
        self.assertEqual(response.status_code, 403)

        # Message should not be created
        self.assertEqual(Message.objects.filter(thread=self.thread).count(), 0)

    def test_send_message_creates_notification(self):
        """
        Spec requirement: Creating a message generates notification for recipient.
        From Use Case 2: "timely real-time notifications".
        This test will FAIL because:
        1. Notification model doesn't exist yet (LookupError), or
        2. View doesn't create notification, or
        3. View doesn't exist (404)
        """
        self.client.login(username='sender', password='testpass123')
        send_message_url = f'/messaging/threads/{self.thread.id}/send/'

        # Try to get Notification model - will fail if model doesn't exist
        try:
            Notification = apps.get_model('notifications', 'Notification')
        except LookupError:
            self.fail("Spec requirement: Notification model should exist in notifications app for real-time notifications")

        # Send a message
        response = self.client.post(send_message_url, {
            'text': 'Hello recipient!'
        })

        # Should create message successfully
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Check that message was created
        message = Message.objects.filter(thread=self.thread).first()
        self.assertIsNotNone(message)

        # Check that notification was created for recipient
        notification = Notification.objects.filter(
            user=self.user2,  # Recipient should get notification
        ).first()
        self.assertIsNotNone(notification, "Notification should be created for message recipient")


class MessageThreadListTests(TestCase):
    """Test cases for listing message threads"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_thread_list_requires_login(self):
        """
        Spec requirement: User must be authenticated to view their message threads.
        This test will FAIL because the view doesn't exist yet (404).
        """
        thread_list_url = url_or('thread_list', '/messaging/threads/')
        response = self.client.get(thread_list_url)

        # Should redirect to login - but will get 404
        self.assertEqual(response.status_code, 302)
        if response.status_code == 302:
            self.assertIn('/login/', response.url)
