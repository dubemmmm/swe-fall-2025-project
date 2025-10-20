from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
from .models import Post, Comment, CommunityAlert

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


class CommunityAlertModelTests(TestCase):
    """Test cases for the CommunityAlert model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='alertuser',
            email='alert@example.com',
            password='testpass123',
            profile_name='Alert User'
        )

    def test_alert_timestamp_auto_set(self):
        """
        Test that alert timestamp is automatically set on creation.
        This test should PASS because the model has auto_now_add=True.
        """
        alert = CommunityAlert.objects.create(
            user=self.user,
            alert_type='LOST',
            title='Lost Dog',
            description='Brown labrador missing',
            location='Central Park, NY',
            contact_info='555-1234'
        )
        self.assertIsNotNone(alert.created_at)


class PostModelTests(TestCase):
    """Test cases for the Post model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='postuser',
            email='post@example.com',
            password='testpass123',
            profile_name='Post User'
        )

    def test_post_timestamp_auto_set(self):
        """
        Test that post timestamp is automatically set on creation.
        This test should PASS because the model has auto_now_add=True.
        """
        post = Post.objects.create(
            user=self.user,
            caption='Test post caption'
        )
        self.assertIsNotNone(post.timestamp)


class PostAlertTests(TestCase):
    """Test cases for posting community alerts"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()

        self.user = User.objects.create_user(
            username='communityuser',
            email='community@example.com',
            password='testpass123',
            profile_name='Community User'
        )

    def test_post_alert_requires_contact_info(self):
        """
        Spec requirement: Test Scenario 3.2 - "system blocks submission and flags missing contact".
        From Use Case 2: Contact information is required for community alerts.
        This test will FAIL because either:
        1. View doesn't exist (404), or
        2. View exists but doesn't validate contact_info field
        """
        self.client.login(username='communityuser', password='testpass123')
        post_alert_url = url_or('post_alert', '/community/alerts/create/')

        # Try to post alert without contact_info
        response = self.client.post(post_alert_url, {
            'alert_type': 'LOST',
            'title': 'Lost Cat',
            'description': 'Orange tabby missing',
            'location': 'Downtown Park',
            'contact_info': ''  # Empty - should be rejected per Test Scenario 3.2
        })

        # Should stay on page with error (200) or return 400
        self.assertEqual(response.status_code, 200)
        # Should show error message about missing contact_info
        messages = list(response.context['messages'])
        self.assertTrue(any('contact' in str(m).lower() for m in messages))

    def test_post_alert_requires_location(self):
        """
        Spec requirement: Test Scenario 3.2 - "flags...location if empty".
        From Use Case 2: Geolocation data is required; "asked to set a location".
        This test will FAIL because either:
        1. View doesn't exist (404), or
        2. View exists but doesn't validate location field
        """
        self.client.login(username='communityuser', password='testpass123')
        post_alert_url = url_or('post_alert', '/community/alerts/create/')

        # Try to post alert without location
        response = self.client.post(post_alert_url, {
            'alert_type': 'FOUND',
            'title': 'Found Dog',
            'description': 'Golden retriever found',
            'location': '',  # Empty - should be rejected per Test Scenario 3.2
            'contact_info': '555-9999'
        })

        # Should stay on page with error
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('location' in str(m).lower() for m in messages))


class CommentTests(TestCase):
    """Test cases for post comments"""

    def setUp(self):
        """Set up test client, user, and post"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='testpass123',
            profile_name='Commenter'
        )
        self.post = Post.objects.create(
            user=self.user,
            caption='Test post for comments'
        )

    def test_post_comment_rejects_empty_text(self):
        """
        Spec requirement: Comments must have non-empty text (Timeline/Comments requirement).
        Similar validation pattern to Test Scenario 3.2 for alerts.
        This test will FAIL because either:
        1. View doesn't exist (404), or
        2. View doesn't validate empty/whitespace text
        """
        self.client.login(username='commenter', password='testpass123')
        # Assuming URL pattern: /community/posts/<post_id>/comment/
        comment_url = f'/community/posts/{self.post.id}/comment/'

        # Try to post empty comment
        response = self.client.post(comment_url, {
            'text': ''
        })

        # Should stay on page with error or return 400
        self.assertIn(response.status_code, [200, 400])

        # Comment should not be created
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 0)

        # Try whitespace-only comment
        response = self.client.post(comment_url, {
            'text': '   \n\t  '
        })

        # Should reject whitespace-only text
        self.assertIn(response.status_code, [200, 400])
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 0)


class CommunityFeedTests(TestCase):
    """Test cases for community feed functionality"""

    def setUp(self):
        """Set up test client and users"""
        self.client = Client()

        # Create active user
        self.active_user = User.objects.create_user(
            username='activeuser',
            email='active@example.com',
            password='testpass123',
            profile_name='Active User',
            is_active=True
        )

        # Create inactive user
        self.inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='testpass123',
            profile_name='Inactive User',
            is_active=False
        )

        # Create posts from both users
        Post.objects.create(user=self.active_user, caption='Active user post')
        Post.objects.create(user=self.inactive_user, caption='Inactive user post')

    def test_community_feed_excludes_inactive_users(self):
        """
        Spec requirement: Use Case 3 - "Only active users with visible profiles are returned".
        Feed should exclude posts from users with is_active=False.
        This test will FAIL because either:
        1. View doesn't exist (404), or
        2. View doesn't filter posts by user.is_active
        """
        feed_url = url_or('community_feed', '/community/feed/')
        response = self.client.get(feed_url)

        # View should exist
        self.assertEqual(response.status_code, 200)

        # Should only show active user's post
        posts_in_feed = response.context['posts']
        self.assertEqual(len(posts_in_feed), 1)
        self.assertEqual(posts_in_feed[0].user, self.active_user)
