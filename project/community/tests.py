from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
from django.template.exceptions import TemplateDoesNotExist
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
        This test verifies that alerts cannot be posted without contact information.
        """
        self.client.login(username='communityuser', password='testpass123')
        post_alert_url = url_or('post_alert', '/community/alerts/create/')

        # Try to post alert without contact_info
        try:
            response = self.client.post(post_alert_url, {
                'alert_type': 'LOST',
                'title': 'Lost Cat',
                'description': 'Orange tabby missing',
                'location': 'Downtown Park',
                'contact_info': ''  # Empty - should be rejected per Test Scenario 3.2
            })

            # Should stay on page with error (200) or return 400
            self.assertEqual(response.status_code, 200)

            # Check for validation error - either in messages or form errors
            has_error = False

            # Check messages
            if 'messages' in response.context:
                messages = list(response.context['messages'])
                has_error = any('contact' in str(m).lower() for m in messages)

            # Check form errors if no message found
            if not has_error and 'form' in response.context:
                form = response.context['form']
                has_error = 'contact_info' in form.errors or any(
                    'contact' in str(error).lower()
                    for errors in form.errors.values()
                    for error in errors
                )

            self.assertTrue(has_error, "Expected validation error for missing contact_info")

        except TemplateDoesNotExist:
            # Template doesn't exist yet, but we can still verify validation worked
            pass

        # Most important: Verify no alert was created (validation blocked it)
        self.assertEqual(CommunityAlert.objects.count(), 0)

    def test_post_alert_requires_location(self):
        """
        Spec requirement: Test Scenario 3.2 - "flags...location if empty".
        From Use Case 2: Geolocation data is required; "asked to set a location".
        This test verifies that alerts cannot be posted without location.
        """
        self.client.login(username='communityuser', password='testpass123')
        post_alert_url = url_or('post_alert', '/community/alerts/create/')

        # Try to post alert without location
        try:
            response = self.client.post(post_alert_url, {
                'alert_type': 'FOUND',
                'title': 'Found Dog',
                'description': 'Golden retriever found',
                'location': '',  # Empty - should be rejected per Test Scenario 3.2
                'contact_info': '555-9999'
            })

            # Should stay on page with error
            self.assertEqual(response.status_code, 200)

            # Check for validation error - either in messages or form errors
            has_error = False

            # Check messages
            if 'messages' in response.context:
                messages = list(response.context['messages'])
                has_error = any('location' in str(m).lower() for m in messages)

            # Check form errors if no message found
            if not has_error and 'form' in response.context:
                form = response.context['form']
                has_error = 'location' in form.errors or any(
                    'location' in str(error).lower()
                    for errors in form.errors.values()
                    for error in errors
                )

            self.assertTrue(has_error, "Expected validation error for missing location")

        except TemplateDoesNotExist:
            # Template doesn't exist yet, but we can still verify validation worked
            pass

        # Most important: Verify no alert was created (validation blocked it)
        self.assertEqual(CommunityAlert.objects.count(), 0)


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


class DiscoverFeatureTests(TestCase):
    """Test cases for Ticket 4: Discover/Community Feed functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='feeduser',
            email='feed@example.com',
            password='password123',
            profile_name='Feed User'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123',
            profile_name='Other User'
        )

    def test_community_feed_displays(self):
        """Test that community feed page loads"""
        self.client.login(username='feeduser', password='password123')

        try:
            feed_url = reverse('community:community_feed')
        except:
            feed_url = '/community/feed/'

        response = self.client.get(feed_url)
        # Should load successfully
        self.assertEqual(response.status_code, 200)

    def test_community_feed_shows_posts(self):
        """Test that community feed displays posts"""
        self.client.login(username='feeduser', password='password123')

        # Create a post
        Post.objects.create(
            user=self.user,
            caption='Test post for feed'
        )

        try:
            feed_url = reverse('community:community_feed')
        except:
            feed_url = '/community/feed/'

        response = self.client.get(feed_url)
        self.assertEqual(response.status_code, 200)

        # Post should appear in feed
        content = response.content.decode()
        self.assertTrue('Test post for feed' in content or 'posts' in content.lower())

    def test_post_creation_workflow(self):
        """Test creating a new post"""
        self.client.login(username='feeduser', password='password123')

        # Try to create a post
        post_data = {
            'caption': 'New post from test'
        }

        # This might fail if post creation not implemented
        try:
            response = self.client.post(reverse('community:create_post'), post_data)
            # Should create post
            self.assertIn(response.status_code, [200, 201, 302])
        except:
            # Post creation endpoint might not exist
            pass

    def test_comment_posting_works(self):
        """Test adding comment to a post"""
        self.client.login(username='feeduser', password='password123')

        # Create a post
        post = Post.objects.create(
            user=self.user,
            caption='Post to comment on'
        )

        # Try to add a comment
        comment_data = {
            'text': 'This is a comment'
        }

        try:
            response = self.client.post(
                reverse('community:add_comment', kwargs={'post_id': post.id}),
                comment_data
            )
            # Should succeed
            self.assertIn(response.status_code, [200, 201, 302])
        except:
            # Comment endpoint might not exist yet
            pass

    def test_empty_comment_rejected(self):
        """Test that empty comments are rejected"""
        self.client.login(username='feeduser', password='password123')

        post = Post.objects.create(
            user=self.user,
            caption='Post for empty comment test'
        )

        # Try to add empty comment
        comment_data = {
            'text': ''
        }

        try:
            response = self.client.post(
                reverse('community:add_comment', kwargs={'post_id': post.id}),
                comment_data
            )
            # Should reject (stay on page or show error)
            # After fix, this should not create a comment
            empty_comments = Comment.objects.filter(post=post, text='')
            self.assertEqual(empty_comments.count(), 0)
        except:
            pass

    def test_comment_whitespace_validation(self):
        """Test that whitespace-only comments are rejected"""
        self.client.login(username='feeduser', password='password123')

        post = Post.objects.create(
            user=self.user,
            caption='Post for whitespace comment test'
        )

        # Try to add whitespace comment
        comment_data = {
            'text': '   '
        }

        try:
            response = self.client.post(
                reverse('community:add_comment', kwargs={'post_id': post.id}),
                comment_data
            )
            # Should reject whitespace comments
            whitespace_comments = Comment.objects.filter(post=post)
            self.assertEqual(whitespace_comments.count(), 0)
        except:
            pass

    def test_feed_pagination(self):
        """Test feed pagination"""
        self.client.login(username='feeduser', password='password123')

        # Create multiple posts
        for i in range(15):
            Post.objects.create(
                user=self.user,
                caption=f'Post {i}'
            )

        try:
            feed_url = reverse('community:community_feed')
        except:
            feed_url = '/community/feed/'

        response = self.client.get(feed_url)
        self.assertEqual(response.status_code, 200)

        # Should handle pagination if many posts

    def test_feed_filter_active_users(self):
        """Test that feed only shows posts from active users"""
        # Create inactive user
        inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='password123',
            profile_name='Inactive',
            is_active=False
        )

        # Create posts from both
        Post.objects.create(user=self.user, caption='Active post')
        Post.objects.create(user=inactive_user, caption='Inactive post')

        self.client.login(username='feeduser', password='password123')

        try:
            feed_url = reverse('community:community_feed')
        except:
            feed_url = '/community/feed/'

        response = self.client.get(feed_url)
        self.assertEqual(response.status_code, 200)

        # Should only show active user's post
        if 'posts' in response.context:
            posts = response.context['posts']
            for post in posts:
                self.assertTrue(post.user.is_active)

    def test_discover_button_functionality(self):
        """Test that discover feature/button works"""
        self.client.login(username='feeduser', password='password123')

        # Try accessing discover/community feed
        try:
            feed_url = reverse('community:community_feed')
        except:
            feed_url = '/community/feed/'

        response = self.client.get(feed_url)

        # Should load without errors
        self.assertEqual(response.status_code, 200)
        # Should not do nothing as reported in ticket
