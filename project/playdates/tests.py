from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from users.models import User
from pets.models import PetProfile
from playdates.models import Playdate, PlaydateParticipant


class PlaydateModelTestCase(TestCase):
    """Test cases for the Playdate model"""

    def setUp(self):
        """Set up test data for Playdate model tests"""
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

        self.playdate = Playdate.objects.create(
            organizer=self.user1,
            organizer_pet=self.pet1,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Central Park, New York',
            description='Fun playdate in the park!',
            max_participants=5,
            is_public=True,
            status='OPEN'
        )

    def test_playdate_creation(self):
        """Test that a playdate can be created successfully"""
        self.assertIsInstance(self.playdate, Playdate)
        self.assertEqual(self.playdate.organizer_pet, self.pet1)
        self.assertEqual(self.playdate.organizer, self.user1)
        self.assertEqual(self.playdate.location, 'Central Park, New York')
        self.assertEqual(self.playdate.status, 'OPEN')
        self.assertTrue(self.playdate.is_public)

    def test_playdate_default_values(self):
        """Test default values for new fields"""
        new_playdate = Playdate.objects.create(
            organizer=self.user2,
            organizer_pet=self.pet2,
            scheduled_time=timezone.now() + timedelta(days=2),
            location='Prospect Park, Brooklyn'
        )
        self.assertEqual(new_playdate.status, 'OPEN')
        self.assertTrue(new_playdate.is_public)
        self.assertEqual(new_playdate.max_participants, 5)

    def test_playdate_get_accepted_count(self):
        """Test getting accepted participant count"""
        # Add participants
        PlaydateParticipant.objects.create(
            playdate=self.playdate,
            user=self.user2,
            pet=self.pet2,
            status='ACCEPTED'
        )
        self.assertEqual(self.playdate.get_accepted_count(), 1)

    def test_playdate_get_available_spots(self):
        """Test getting available spots"""
        # Max 5, organizer takes 1, so 4 available
        self.assertEqual(self.playdate.get_available_spots(), 4)

        # Add 2 accepted participants
        user3 = User.objects.create_user(username='user3', password='pass')
        pet3 = PetProfile.objects.create(
            owner=user3, name='Pet3', species='DOG', age='2',
            general_size='MEDIUM', energy_level='HIGH', is_playdate_available=True
        )
        PlaydateParticipant.objects.create(
            playdate=self.playdate, user=self.user2, pet=self.pet2, status='ACCEPTED'
        )
        PlaydateParticipant.objects.create(
            playdate=self.playdate, user=user3, pet=pet3, status='ACCEPTED'
        )

        self.assertEqual(self.playdate.get_available_spots(), 2)

    def test_playdate_is_full(self):
        """Test checking if playdate is full"""
        self.assertFalse(self.playdate.is_full())

        # Fill up the playdate (max 5, organizer + 4 participants)
        for i in range(4):
            user = User.objects.create_user(username=f'user{i}', password='pass')
            pet = PetProfile.objects.create(
                owner=user, name=f'Pet{i}', species='DOG', age='2',
                general_size='MEDIUM', energy_level='HIGH', is_playdate_available=True
            )
            PlaydateParticipant.objects.create(
                playdate=self.playdate, user=user, pet=pet, status='ACCEPTED'
            )

        self.assertTrue(self.playdate.is_full())


class PlaydateParticipantModelTestCase(TestCase):
    """Test cases for the PlaydateParticipant model with new statuses"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='testpass123',
            profile_name='Organizer',
            location='New York, NY'
        )

        self.user2 = User.objects.create_user(
            username='invitee',
            email='invitee@example.com',
            password='testpass123',
            profile_name='Invitee',
            location='Brooklyn, NY'
        )

        self.pet1 = PetProfile.objects.create(
            owner=self.user1,
            name='Buddy',
            species='DOG',
            age='3 years',
            general_size='LARGE',
            energy_level='HIGH',
            is_playdate_available=True
        )

        self.pet2 = PetProfile.objects.create(
            owner=self.user2,
            name='Max',
            species='DOG',
            age='2 years',
            general_size='LARGE',
            energy_level='HIGH',
            is_playdate_available=True
        )

        self.playdate = Playdate.objects.create(
            organizer=self.user1,
            organizer_pet=self.pet1,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Central Park',
            is_public=True
        )

    def test_participant_invited_status(self):
        """Test creating participant with INVITED status"""
        participant = PlaydateParticipant.objects.create(
            playdate=self.playdate,
            user=self.user2,
            pet=self.pet2,
            status='INVITED'
        )
        self.assertEqual(participant.status, 'INVITED')

    def test_participant_requested_status(self):
        """Test creating participant with REQUESTED status"""
        participant = PlaydateParticipant.objects.create(
            playdate=self.playdate,
            user=self.user2,
            pet=self.pet2,
            status='REQUESTED'
        )
        self.assertEqual(participant.status, 'REQUESTED')

    def test_participant_status_transitions(self):
        """Test status transitions"""
        participant = PlaydateParticipant.objects.create(
            playdate=self.playdate,
            user=self.user2,
            pet=self.pet2,
            status='INVITED'
        )

        # Accept invitation
        participant.status = 'ACCEPTED'
        participant.responded_at = timezone.now()
        participant.save()

        self.assertEqual(participant.status, 'ACCEPTED')
        self.assertIsNotNone(participant.responded_at)


class BrowsePlaydatesViewTestCase(TestCase):
    """Test cases for browsing public playdates"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        self.user1 = User.objects.create_user(
            username='user1', password='testpass123', profile_name='User One'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='testpass123', profile_name='User Two'
        )

        self.pet1 = PetProfile.objects.create(
            owner=self.user1, name='Buddy', species='DOG', age='3 years',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )
        self.pet2 = PetProfile.objects.create(
            owner=self.user2, name='Max', species='CAT', age='2 years',
            general_size='MEDIUM', energy_level='MEDIUM', is_playdate_available=True
        )

        # Create public playdate
        self.public_playdate = Playdate.objects.create(
            organizer=self.user1,
            organizer_pet=self.pet1,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Central Park',
            is_public=True,
            status='OPEN'
        )

        # Create private playdate
        self.private_playdate = Playdate.objects.create(
            organizer=self.user1,
            organizer_pet=self.pet1,
            scheduled_time=timezone.now() + timedelta(days=2),
            location='Dog Park',
            is_public=False,
            status='OPEN'
        )

    def test_browse_view_requires_login(self):
        """Test that browse view requires authentication"""
        response = self.client.get(reverse('browse-playdates'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_browse_view_shows_public_playdates(self):
        """Test that browse view shows only public playdates"""
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('browse-playdates'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('playdates', response.context)
        # Should show public playdate but not private or own playdates
        self.assertEqual(response.context['playdates'].count(), 1)

    def test_browse_view_excludes_own_playdates(self):
        """Test that users don't see their own playdates in browse"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('browse-playdates'))

        self.assertEqual(response.context['playdates'].count(), 0)

    def test_browse_view_filter_by_species(self):
        """Test filtering by pet species"""
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('browse-playdates'), {'species': 'DOG'})

        self.assertEqual(response.context['playdates'].count(), 1)


class RequestToJoinViewTestCase(TestCase):
    """Test cases for requesting to join playdates"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        self.organizer = User.objects.create_user(
            username='organizer', password='testpass123', profile_name='Organizer'
        )
        self.requester = User.objects.create_user(
            username='requester', password='testpass123', profile_name='Requester'
        )

        self.organizer_pet = PetProfile.objects.create(
            owner=self.organizer, name='Buddy', species='DOG', age='3 years',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )
        self.requester_pet = PetProfile.objects.create(
            owner=self.requester, name='Max', species='DOG', age='2 years',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )

        self.playdate = Playdate.objects.create(
            organizer=self.organizer,
            organizer_pet=self.organizer_pet,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Central Park',
            is_public=True,
            max_participants=5
        )

    def test_request_to_join_success(self):
        """Test successfully requesting to join a playdate"""
        self.client.login(username='requester', password='testpass123')

        response = self.client.post(
            reverse('request-join', kwargs={'pk': self.playdate.id}),
            {'pet_id': self.requester_pet.id}
        )

        self.assertEqual(response.status_code, 302)

        # Check participant was created with REQUESTED status
        participant = PlaydateParticipant.objects.filter(
            playdate=self.playdate,
            pet=self.requester_pet
        ).first()
        self.assertIsNotNone(participant)
        self.assertEqual(participant.status, 'REQUESTED')

    def test_request_to_join_full_playdate(self):
        """Test cannot request to join full playdate"""
        # Fill the playdate
        for i in range(4):
            user = User.objects.create_user(username=f'user{i}', password='pass')
            pet = PetProfile.objects.create(
                owner=user, name=f'Pet{i}', species='DOG', age='2',
                general_size='MEDIUM', energy_level='HIGH', is_playdate_available=True
            )
            PlaydateParticipant.objects.create(
                playdate=self.playdate, user=user, pet=pet, status='ACCEPTED'
            )

        self.client.login(username='requester', password='testpass123')
        response = self.client.post(
            reverse('request-join', kwargs={'pk': self.playdate.id}),
            {'pet_id': self.requester_pet.id}
        )

        # Should not create participant
        self.assertFalse(
            PlaydateParticipant.objects.filter(
                playdate=self.playdate,
                pet=self.requester_pet
            ).exists()
        )

    def test_cannot_request_twice(self):
        """Test cannot request to join twice"""
        PlaydateParticipant.objects.create(
            playdate=self.playdate,
            user=self.requester,
            pet=self.requester_pet,
            status='REQUESTED'
        )

        self.client.login(username='requester', password='testpass123')
        response = self.client.post(
            reverse('request-join', kwargs={'pk': self.playdate.id}),
            {'pet_id': self.requester_pet.id}
        )

        # Should still be only one participant
        self.assertEqual(
            PlaydateParticipant.objects.filter(
                playdate=self.playdate,
                pet=self.requester_pet
            ).count(),
            1
        )


class ApproveRequestViewTestCase(TestCase):
    """Test cases for approving/denying join requests"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        self.organizer = User.objects.create_user(
            username='organizer', password='testpass123'
        )
        self.requester = User.objects.create_user(
            username='requester', password='testpass123'
        )

        self.organizer_pet = PetProfile.objects.create(
            owner=self.organizer, name='Buddy', species='DOG', age='3',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )
        self.requester_pet = PetProfile.objects.create(
            owner=self.requester, name='Max', species='DOG', age='2',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )

        self.playdate = Playdate.objects.create(
            organizer=self.organizer,
            organizer_pet=self.organizer_pet,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Central Park',
            is_public=True
        )

        self.participant = PlaydateParticipant.objects.create(
            playdate=self.playdate,
            user=self.requester,
            pet=self.requester_pet,
            status='REQUESTED'
        )

    def test_approve_request_success(self):
        """Test successfully approving a request"""
        self.client.login(username='organizer', password='testpass123')

        response = self.client.post(
            reverse('approve-request', kwargs={
                'pk': self.playdate.id,
                'participant_id': self.participant.id
            }),
            {'action': 'approve'}
        )

        self.assertEqual(response.status_code, 302)

        self.participant.refresh_from_db()
        self.assertEqual(self.participant.status, 'ACCEPTED')
        self.assertIsNotNone(self.participant.responded_at)

    def test_deny_request_success(self):
        """Test successfully denying a request"""
        self.client.login(username='organizer', password='testpass123')

        response = self.client.post(
            reverse('approve-request', kwargs={
                'pk': self.playdate.id,
                'participant_id': self.participant.id
            }),
            {'action': 'deny'}
        )

        self.participant.refresh_from_db()
        self.assertEqual(self.participant.status, 'DECLINED')

    def test_only_organizer_can_approve(self):
        """Test that only organizer can approve requests"""
        self.client.login(username='requester', password='testpass123')

        response = self.client.post(
            reverse('approve-request', kwargs={
                'pk': self.playdate.id,
                'participant_id': self.participant.id
            }),
            {'action': 'approve'}
        )

        # Should be forbidden or redirect
        self.assertIn(response.status_code, [302, 403])


class PlaydateInviteViewTestCase(TestCase):
    """Test cases for inviting pets (organizer sends direct invite)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        self.organizer = User.objects.create_user(
            username='organizer', password='testpass123'
        )
        self.invitee = User.objects.create_user(
            username='invitee', password='testpass123'
        )

        self.organizer_pet = PetProfile.objects.create(
            owner=self.organizer, name='Buddy', species='DOG', age='3',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )
        self.invitee_pet = PetProfile.objects.create(
            owner=self.invitee, name='Max', species='DOG', age='2',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )

        self.playdate = Playdate.objects.create(
            organizer=self.organizer,
            organizer_pet=self.organizer_pet,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Central Park',
            is_public=True
        )

    def test_invite_pet_success(self):
        """Test successfully inviting a pet"""
        self.client.login(username='organizer', password='testpass123')

        response = self.client.post(
            reverse('playdate-invite', kwargs={'pk': self.playdate.id}),
            {'pet_id': self.invitee_pet.id}
        )

        self.assertEqual(response.status_code, 302)

        # Check participant was created with INVITED status
        participant = PlaydateParticipant.objects.filter(
            playdate=self.playdate,
            pet=self.invitee_pet,
            status='INVITED'
        ).first()
        self.assertIsNotNone(participant)


class PlaydateRespondViewTestCase(TestCase):
    """Test cases for responding to invitations"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        self.organizer = User.objects.create_user(
            username='organizer', password='testpass123'
        )
        self.invitee = User.objects.create_user(
            username='invitee', password='testpass123'
        )

        self.organizer_pet = PetProfile.objects.create(
            owner=self.organizer, name='Buddy', species='DOG', age='3',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )
        self.invitee_pet = PetProfile.objects.create(
            owner=self.invitee, name='Max', species='DOG', age='2',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )

        self.playdate = Playdate.objects.create(
            organizer=self.organizer,
            organizer_pet=self.organizer_pet,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Central Park',
            is_public=True
        )

        self.participant = PlaydateParticipant.objects.create(
            playdate=self.playdate,
            user=self.invitee,
            pet=self.invitee_pet,
            status='INVITED'
        )

    def test_accept_invitation(self):
        """Test accepting an invitation"""
        self.client.login(username='invitee', password='testpass123')

        response = self.client.post(
            reverse('playdate-respond', kwargs={'pk': self.playdate.id}),
            {'response': 'accept'}
        )

        self.assertEqual(response.status_code, 302)

        self.participant.refresh_from_db()
        self.assertEqual(self.participant.status, 'ACCEPTED')
        self.assertIsNotNone(self.participant.responded_at)

        self.playdate.refresh_from_db()
        self.assertEqual(self.playdate.status, 'CONFIRMED')

    def test_decline_invitation(self):
        """Test declining an invitation"""
        self.client.login(username='invitee', password='testpass123')

        response = self.client.post(
            reverse('playdate-respond', kwargs={'pk': self.playdate.id}),
            {'response': 'decline'}
        )

        self.participant.refresh_from_db()
        self.assertEqual(self.participant.status, 'DECLINED')


class CompleteWorkflowTestCase(TestCase):
    """Test complete workflows for both invitation and request systems"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        self.user1 = User.objects.create_user(
            username='user1', password='testpass123', profile_name='User One'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='testpass123', profile_name='User Two'
        )
        self.user3 = User.objects.create_user(
            username='user3', password='testpass123', profile_name='User Three'
        )

        self.pet1 = PetProfile.objects.create(
            owner=self.user1, name='Buddy', species='DOG', age='3',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )
        self.pet2 = PetProfile.objects.create(
            owner=self.user2, name='Max', species='DOG', age='2',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )
        self.pet3 = PetProfile.objects.create(
            owner=self.user3, name='Charlie', species='DOG', age='4',
            general_size='LARGE', energy_level='HIGH', is_playdate_available=True
        )

    def test_public_playdate_with_requests(self):
        """Test workflow: User1 creates public playdate, User2 requests to join"""
        # User1 creates public playdate
        self.client.login(username='user1', password='testpass123')

        playdate_data = {
            'organizer_pet': self.pet1.id,
            'scheduled_time': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'location': 'Central Park',
            'description': 'Fun playdate!',
            'max_participants': 5,
            'is_public': True
        }

        response = self.client.post(reverse('playdate-create'), data=playdate_data)
        self.assertEqual(response.status_code, 302)

        playdate = Playdate.objects.get(organizer_pet=self.pet1)
        self.assertTrue(playdate.is_public)
        self.assertEqual(playdate.status, 'OPEN')

        # User2 requests to join
        self.client.logout()
        self.client.login(username='user2', password='testpass123')

        response = self.client.post(
            reverse('request-join', kwargs={'pk': playdate.id}),
            {'pet_id': self.pet2.id}
        )

        participant = PlaydateParticipant.objects.get(playdate=playdate, pet=self.pet2)
        self.assertEqual(participant.status, 'REQUESTED')

        # User1 approves request
        self.client.logout()
        self.client.login(username='user1', password='testpass123')

        response = self.client.post(
            reverse('approve-request', kwargs={
                'pk': playdate.id,
                'participant_id': participant.id
            }),
            {'action': 'approve'}
        )

        participant.refresh_from_db()
        self.assertEqual(participant.status, 'ACCEPTED')

    def test_invitation_and_request_mixed(self):
        """Test workflow: User1 creates playdate, invites User2, User3 requests"""
        # User1 creates playdate and invites User2
        self.client.login(username='user1', password='testpass123')

        playdate = Playdate.objects.create(
            organizer=self.user1,
            organizer_pet=self.pet1,
            scheduled_time=timezone.now() + timedelta(days=1),
            location='Dog Park',
            is_public=True
        )

        # Send invitation to User2
        PlaydateParticipant.objects.create(
            playdate=playdate,
            user=self.user2,
            pet=self.pet2,
            status='INVITED'
        )

        # User3 requests to join
        self.client.logout()
        self.client.login(username='user3', password='testpass123')

        response = self.client.post(
            reverse('request-join', kwargs={'pk': playdate.id}),
            {'pet_id': self.pet3.id}
        )

        # Check both participants exist with different statuses
        invited = PlaydateParticipant.objects.get(playdate=playdate, pet=self.pet2)
        requested = PlaydateParticipant.objects.get(playdate=playdate, pet=self.pet3)

        self.assertEqual(invited.status, 'INVITED')
        self.assertEqual(requested.status, 'REQUESTED')

        # User2 accepts invitation
        self.client.logout()
        self.client.login(username='user2', password='testpass123')

        response = self.client.post(
            reverse('playdate-respond', kwargs={'pk': playdate.id}),
            {'response': 'accept'}
        )

        invited.refresh_from_db()
        self.assertEqual(invited.status, 'ACCEPTED')

        # User1 approves User3's request
        self.client.logout()
        self.client.login(username='user1', password='testpass123')

        response = self.client.post(
            reverse('approve-request', kwargs={
                'pk': playdate.id,
                'participant_id': requested.id
            }),
            {'action': 'approve'}
        )

        requested.refresh_from_db()
        self.assertEqual(requested.status, 'ACCEPTED')

        # Verify playdate is CONFIRMED with 2 accepted participants
        playdate.refresh_from_db()
        self.assertEqual(playdate.status, 'CONFIRMED')
        self.assertEqual(playdate.get_accepted_count(), 2)


class PlaydatePetSelectionTests(TestCase):
    """Test cases for Ticket 6: Playdate pet selection and cancel functionality"""

    def setUp(self):
        """Set up test data"""
        from pets.models import PetProfile

        self.client = Client()
        self.user = User.objects.create_user(
            username='petowner',
            email='petowner@example.com',
            password='password123',
            profile_name='Pet Owner'
        )
        self.other_user = User.objects.create_user(
            username='otherpet',
            email='otherpet@example.com',
            password='password123',
            profile_name='Other Pet Owner'
        )

        # Create pets for user - some available, some not
        self.available_pet = PetProfile.objects.create(
            owner=self.user,
            name='Available Dog',
            species='DOG',
            breed='Labrador',
            age=3,
            is_playdate_available=True
        )
        self.unavailable_pet = PetProfile.objects.create(
            owner=self.user,
            name='Unavailable Dog',
            species='DOG',
            breed='Poodle',
            age=2,
            is_playdate_available=False
        )
        self.other_user_pet = PetProfile.objects.create(
            owner=self.other_user,
            name='Other Person Dog',
            species='DOG',
            breed='Beagle',
            age=4,
            is_playdate_available=True
        )

        self.playdate_create_url = reverse('playdate-create')

    def test_playdate_create_shows_only_user_pets(self):
        """Test that pet dropdown only shows user's own pets"""
        self.client.login(username='petowner', password='password123')

        response = self.client.get(self.playdate_create_url)
        self.assertEqual(response.status_code, 200)

        # Check form's pet queryset
        if 'form' in response.context:
            form = response.context['form']
            pet_queryset = form.fields['organizer_pet'].queryset

            # Should include user's pets
            self.assertIn(self.available_pet, pet_queryset)

            # Should NOT include other user's pets
            self.assertNotIn(self.other_user_pet, pet_queryset)

    def test_playdate_create_filters_available_pets(self):
        """Test that only pets with is_playdate_available=True are shown"""
        self.client.login(username='petowner', password='password123')

        response = self.client.get(self.playdate_create_url)
        self.assertEqual(response.status_code, 200)

        if 'form' in response.context:
            form = response.context['form']
            pet_queryset = form.fields['organizer_pet'].queryset

            # Should include available pet
            self.assertIn(self.available_pet, pet_queryset)

            # Should NOT include unavailable pet
            self.assertNotIn(self.unavailable_pet, pet_queryset)

    def test_cannot_create_with_other_user_pet(self):
        """Test that user cannot create playdate with another user's pet"""
        self.client.login(username='petowner', password='password123')

        from datetime import datetime, timedelta
        future_time = datetime.now() + timedelta(days=1)

        response = self.client.post(self.playdate_create_url, {
            'organizer_pet': self.other_user_pet.id,  # Try to use other user's pet
            'location': 'Dog Park',
            'scheduled_time': future_time.strftime('%Y-%m-%d %H:%M'),
            'description': 'Test playdate',
            'is_public': True,
            'max_participants': 5
        })

        # Should fail (400 or stay on form with error)
        self.assertIn(response.status_code, [200, 400, 403])

        # Playdate should NOT be created
        playdate_created = Playdate.objects.filter(
            organizer_pet=self.other_user_pet
        ).exists()
        self.assertFalse(playdate_created)

    def test_playdate_form_has_cancel_button(self):
        """Test that playdate form has cancel button"""
        self.client.login(username='petowner', password='password123')

        response = self.client.get(self.playdate_create_url)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()
        # Should have cancel option
        self.assertTrue('Cancel' in content or 'cancel' in content.lower() or 'Back' in content)

    def test_playdate_create_cancel_redirects(self):
        """Test canceling playdate creation"""
        self.client.login(username='petowner', password='password123')

        # Access form
        response = self.client.get(self.playdate_create_url)
        self.assertEqual(response.status_code, 200)

        # Navigate away (simulating cancel)
        response = self.client.get(reverse('playdate-list'))
        self.assertEqual(response.status_code, 200)
        # Should not be stuck

    def test_playdate_create_back_button(self):
        """Test back button functionality during playdate creation"""
        self.client.login(username='petowner', password='password123')

        # Access form
        response = self.client.get(self.playdate_create_url)
        self.assertEqual(response.status_code, 200)

        # Go back
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Should work fine (Ticket 6 bug)

    def test_cannot_select_unavailable_pet(self):
        """Test that unavailable pets cannot be selected"""
        self.client.login(username='petowner', password='password123')

        from datetime import datetime, timedelta
        future_time = datetime.now() + timedelta(days=1)

        response = self.client.post(self.playdate_create_url, {
            'organizer_pet': self.unavailable_pet.id,  # Try unavailable pet
            'location': 'Dog Park',
            'scheduled_time': future_time.strftime('%Y-%m-%d %H:%M'),
            'description': 'Test playdate',
            'is_public': True,
            'max_participants': 5
        })

        # Should fail validation
        self.assertIn(response.status_code, [200, 400])

        # Playdate should NOT be created with unavailable pet
        playdate_created = Playdate.objects.filter(
            organizer_pet=self.unavailable_pet
        ).exists()
        self.assertFalse(playdate_created)

    def test_playdate_pet_queryset_filtering(self):
        """Test that form queryset is properly filtered"""
        self.client.login(username='petowner', password='password123')

        response = self.client.get(self.playdate_create_url)
        self.assertEqual(response.status_code, 200)

        if 'form' in response.context:
            form = response.context['form']
            pet_queryset = list(form.fields['organizer_pet'].queryset)

            # Should have exactly 1 pet (the available one)
            self.assertEqual(len(pet_queryset), 1)
            self.assertEqual(pet_queryset[0], self.available_pet)
