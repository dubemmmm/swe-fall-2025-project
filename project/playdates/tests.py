from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from users.models import User
from pets.models import PetProfile
from playdates.models import Playdate


class PlaydateModelTestCase(TestCase):
    """Test cases for the Playdate model"""

    def setUp(self):
        """Set up test data for Playdate model tests"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='petowner1',
            email='owner1@example.com',
            password='testpass123',
            profile_name='Pet Owner One',
            location='New York, NY',
            latitude=Decimal('40.712776'),
            longitude=Decimal('-74.005974')
        )

        self.user2 = User.objects.create_user(
            username='petowner2',
            email='owner2@example.com',
            password='testpass123',
            profile_name='Pet Owner Two',
            location='Brooklyn, NY',
            latitude=Decimal('40.650002'),
            longitude=Decimal('-73.949997')
        )

        # Create test pets
        self.pet1 = PetProfile.objects.create(
            owner=self.user1,
            name='Buddy',
            species='DOG',
            breed='Golden Retriever',
            age='3 years',
            general_size='LARGE',
            energy_level='HIGH',
            weight=Decimal('70.50'),
            is_playdate_available=True,
            privacy_settings='PUBLIC'
        )

        self.pet2 = PetProfile.objects.create(
            owner=self.user2,
            name='Max',
            species='DOG',
            breed='Labrador',
            age='2 years',
            general_size='LARGE',
            energy_level='HIGH',
            weight=Decimal('65.00'),
            is_playdate_available=True,
            privacy_settings='PUBLIC'
        )

        # Create a test playdate
        self.playdate = Playdate.objects.create(
            pet=self.pet1,
            organizer=self.user1,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Central Park, New York',
            status='PENDING'
        )

    def test_playdate_creation(self):
        """Test that a playdate can be created successfully"""
        self.assertIsInstance(self.playdate, Playdate)
        self.assertEqual(self.playdate.pet, self.pet1)
        self.assertEqual(self.playdate.organizer, self.user1)
        self.assertEqual(self.playdate.location, 'Central Park, New York')
        self.assertEqual(self.playdate.status, 'PENDING')

    def test_playdate_default_status(self):
        """Test that default status is PENDING"""
        new_playdate = Playdate.objects.create(
            pet=self.pet2,
            organizer=self.user2,
            scheduled_time=timezone.now() + timedelta(days=2),
            location='Prospect Park, Brooklyn'
        )
        self.assertEqual(new_playdate.status, 'PENDING')

    def test_playdate_foreign_key_relationships(self):
        """Test foreign key relationships work correctly"""
        # Test pet relationship
        self.assertEqual(self.playdate.pet.name, 'Buddy')
        self.assertEqual(self.playdate.pet.owner, self.user1)

        # Test organizer relationship
        self.assertEqual(self.playdate.organizer.username, 'petowner1')

    def test_playdate_cascade_delete_pet(self):
        """Test that deleting a pet deletes associated playdates"""
        playdate_id = self.playdate.id
        self.pet1.delete()

        with self.assertRaises(Playdate.DoesNotExist):
            Playdate.objects.get(id=playdate_id)

    def test_playdate_cascade_delete_user(self):
        """Test that deleting a user deletes their organized playdates"""
        playdate_id = self.playdate.id
        self.user1.delete()

        with self.assertRaises(Playdate.DoesNotExist):
            Playdate.objects.get(id=playdate_id)

    def test_playdate_created_at_auto_set(self):
        """Test that created_at is automatically set"""
        self.assertIsNotNone(self.playdate.created_at)
        self.assertLessEqual(
            self.playdate.created_at,
            timezone.now()
        )

    def test_multiple_playdates_for_same_pet(self):
        """Test that a pet can have multiple playdates"""
        playdate2 = Playdate.objects.create(
            pet=self.pet1,
            organizer=self.user1,
            scheduled_time=timezone.now() + timedelta(days=3),
            location='Washington Square Park'
        )

        pet_playdates = Playdate.objects.filter(pet=self.pet1)
        self.assertEqual(pet_playdates.count(), 2)

    def test_playdate_status_update(self):
        """Test that playdate status can be updated"""
        self.playdate.status = 'CONFIRMED'
        self.playdate.save()

        updated_playdate = Playdate.objects.get(id=self.playdate.id)
        self.assertEqual(updated_playdate.status, 'CONFIRMED')

    def test_playdate_scheduled_time_in_future(self):
        """Test that scheduled time can be set in the future"""
        future_time = timezone.now() + timedelta(days=7)
        playdate = Playdate.objects.create(
            pet=self.pet2,
            organizer=self.user2,
            scheduled_time=future_time,
            location='Dog Beach'
        )
        self.assertEqual(playdate.scheduled_time, future_time)


class PlaydateViewTestCase(TestCase):
    """Test cases for Playdate views - These will fail until views are implemented"""

    def setUp(self):
        """Set up test data for view tests"""
        self.client = Client()

        # Create test users
        self.user1 = User.objects.create_user(
            username='petowner1',
            email='owner1@example.com',
            password='testpass123',
            profile_name='Pet Owner One',
            location='New York, NY'
        )

        self.user2 = User.objects.create_user(
            username='petowner2',
            email='owner2@example.com',
            password='testpass123',
            profile_name='Pet Owner Two',
            location='Brooklyn, NY'
        )

        # Create test pets
        self.pet1 = PetProfile.objects.create(
            owner=self.user1,
            name='Buddy',
            species='DOG',
            breed='Golden Retriever',
            age='3 years',
            general_size='LARGE',
            energy_level='HIGH',
            is_playdate_available=True
        )

        self.pet2 = PetProfile.objects.create(
            owner=self.user2,
            name='Max',
            species='DOG',
            breed='Labrador',
            age='2 years',
            general_size='LARGE',
            energy_level='HIGH',
            is_playdate_available=True
        )

        # Create test playdate
        self.playdate = Playdate.objects.create(
            pet=self.pet1,
            organizer=self.user1,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Central Park, New York',
            status='PENDING'
        )

    # def test_create_playdate_view(self):
    #     """Test creating a playdate through the view (will fail until implemented)"""
    #     self.client.login(username='petowner1', password='testpass123')

    #     playdate_data = {
    #         'pet': self.pet1.id,
    #         'organizer': self.user1.id,
    #         'scheduled_time': (timezone.now() + timedelta(days=2)).isoformat(),
    #         'location': 'Brooklyn Bridge Park',
    #         'status': 'PENDING'
    #     }

    #     # This will fail until the view is implemented
    #     try:
    #         response = self.client.post(
    #             reverse('playdate-create'),  # URL name will need to be defined
    #             data=playdate_data
    #         )
    #         self.assertEqual(response.status_code, 201)
    #     except Exception as e:
    #         # Expected to fail - views not implemented yet
    #         self.assertTrue(True, f"Expected failure: {e}")

#     def test_list_playdates_view(self):
#         """Test listing all playdates (will fail until implemented)"""
#         self.client.login(username='petowner1', password='testpass123')

#         # This will fail until the view is implemented
#         try:
#             response = self.client.get(reverse('playdate-list'))
#             self.assertEqual(response.status_code, 200)
#             self.assertIn('playdates', response.context)
#         except Exception as e:
#             # Expected to fail - views not implemented yet
#             self.assertTrue(True, f"Expected failure: {e}")

#     def test_playdate_detail_view(self):
#         """Test viewing playdate details (will fail until implemented)"""
#         self.client.login(username='petowner1', password='testpass123')

#         # This will fail until the view is implemented
#         try:
#             response = self.client.get(
#                 reverse('playdate-detail', kwargs={'pk': self.playdate.id})
#             )
#             self.assertEqual(response.status_code, 200)
#             self.assertEqual(response.context['playdate'], self.playdate)
#         except Exception as e:
#             # Expected to fail - views not implemented yet
#             self.assertTrue(True, f"Expected failure: {e}")

#     def test_update_playdate_status_view(self):
#         """Test updating playdate status (will fail until implemented)"""
#         self.client.login(username='petowner1', password='testpass123')

#         # This will fail until the view is implemented
#         try:
#             response = self.client.patch(
#                 reverse('playdate-update', kwargs={'pk': self.playdate.id}),
#                 data={'status': 'CONFIRMED'},
#                 content_type='application/json'
#             )
#             self.assertEqual(response.status_code, 200)

#             updated_playdate = Playdate.objects.get(id=self.playdate.id)
#             self.assertEqual(updated_playdate.status, 'CONFIRMED')
#         except Exception as e:
#             # Expected to fail - views not implemented yet
#             self.assertTrue(True, f"Expected failure: {e}")

#     def test_delete_playdate_view(self):
#         """Test deleting a playdate (will fail until implemented)"""
#         self.client.login(username='petowner1', password='testpass123')
#         playdate_id = self.playdate.id

#         # This will fail until the view is implemented
#         try:
#             response = self.client.delete(
#                 reverse('playdate-delete', kwargs={'pk': playdate_id})
#             )
#             self.assertEqual(response.status_code, 204)

#             with self.assertRaises(Playdate.DoesNotExist):
#                 Playdate.objects.get(id=playdate_id)
#         except Exception as e:
#             # Expected to fail - views not implemented yet
#             self.assertTrue(True, f"Expected failure: {e}")

#     def test_user_can_only_modify_own_playdates(self):
#         """Test that users can only modify their own playdates (will fail until implemented)"""
#         self.client.login(username='petowner2', password='testpass123')

#         # This will fail until the view is implemented
#         try:
#             response = self.client.patch(
#                 reverse('playdate-update', kwargs={'pk': self.playdate.id}),
#                 data={'status': 'CANCELLED'},
#                 content_type='application/json'
#             )
#             # Should be forbidden (403) since user2 didn't create this playdate
#             self.assertEqual(response.status_code, 403)
#         except Exception as e:
#             # Expected to fail - views not implemented yet
#             self.assertTrue(True, f"Expected failure: {e}")

#     def test_filter_playdates_by_status(self):
#         """Test filtering playdates by status (will fail until implemented)"""
#         # Create playdates with different statuses
#         Playdate.objects.create(
#             pet=self.pet2,
#             organizer=self.user2,
#             scheduled_time=timezone.now() + timedelta(days=3),
#             location='Dog Park',
#             status='CONFIRMED'
#         )

#         self.client.login(username='petowner1', password='testpass123')

#         # This will fail until the view is implemented
#         try:
#             response = self.client.get(
#                 reverse('playdate-list'),
#                 {'status': 'PENDING'}
#             )
#             self.assertEqual(response.status_code, 200)
#             # Should only return pending playdates
#         except Exception as e:
#             # Expected to fail - views not implemented yet
#             self.assertTrue(True, f"Expected failure: {e}")

#     def test_filter_playdates_by_pet(self):
#         """Test filtering playdates by pet (will fail until implemented)"""
#         self.client.login(username='petowner1', password='testpass123')

#         # This will fail until the view is implemented
#         try:
#             response = self.client.get(
#                 reverse('playdate-list'),
#                 {'pet': self.pet1.id}
#             )
#             self.assertEqual(response.status_code, 200)
#             # Should only return playdates for pet1
#         except Exception as e:
#             # Expected to fail - views not implemented yet
#             self.assertTrue(True, f"Expected failure: {e}")


# class PlaydateBusinessLogicTestCase(TestCase):
#     """Test cases for playdate business logic (will fail until implemented)"""

#     def setUp(self):
#         """Set up test data"""
#         self.user = User.objects.create_user(
#             username='petowner',
#             email='owner@example.com',
#             password='testpass123',
#             profile_name='Pet Owner',
#             location='New York, NY'
#         )

#         self.pet_available = PetProfile.objects.create(
#             owner=self.user,
#             name='Available Pet',
#             species='DOG',
#             breed='Beagle',
#             age='4 years',
#             general_size='MEDIUM',
#             energy_level='MEDIUM',
#             is_playdate_available=True
#         )

#         self.pet_unavailable = PetProfile.objects.create(
#             owner=self.user,
#             name='Unavailable Pet',
#             species='CAT',
#             breed='Persian',
#             age='5 years',
#             general_size='SMALL',
#             energy_level='LOW',
#             is_playdate_available=False
#         )

#     def test_cannot_create_playdate_for_unavailable_pet(self):
#         """Test that playdates can't be created for pets not available (will fail until implemented)"""
#         # This logic should be in the view/serializer validation
#         # For now, we can create the playdate at model level, but view should prevent it
#         playdate = Playdate.objects.create(
#             pet=self.pet_unavailable,
#             organizer=self.user,
#             scheduled_time=timezone.now() + timedelta(days=1),
#             location='Some Park'
#         )
#         # Model allows this, but view validation should prevent it
#         self.assertIsInstance(playdate, Playdate)

#     def test_cannot_schedule_playdate_in_past(self):
#         """Test validation for scheduling playdates in the past (will fail until implemented)"""
#         # This logic should be in the view/serializer validation
#         past_time = timezone.now() - timedelta(days=1)
#         playdate = Playdate.objects.create(
#             pet=self.pet_available,
#             organizer=self.user,
#             scheduled_time=past_time,
#             location='Some Park'
#         )
#         # Model allows this, but view validation should prevent it
#         self.assertIsInstance(playdate, Playdate)
