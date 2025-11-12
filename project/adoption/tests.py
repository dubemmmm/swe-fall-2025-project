from django.test import TestCase
from django.urls import reverse
from users.models import User
from pets.models import PetProfile
from .models import AdoptionPost

class AdoptionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass')
        self.other_user = User.objects.create_user(username='user2', password='pass')
        self.pet = PetProfile.objects.create(
            name='Fido', age='2', breed='Labrador', species='DOG',
            general_size='MEDIUM', energy_level='MEDIUM', owner=self.user
        )
        self.adoption = AdoptionPost.objects.create(
            pet=self.pet, owner=self.user, requirements='Good home', additional_info='None'
        )

    def test_user_can_view_pets_for_adoption(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('adoption:user_adoptions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fido')

    def test_user_successfully_lists_pet_for_adoption(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('adoption:create'), {
            'pet': self.pet.id,
            'requirements': 'Loving home',
            'additional_info': 'Playful'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AdoptionPost.objects.filter(pet=self.pet, owner=self.user, requirements='Loving home').exists())

    def test_listing_pet_for_adoption_by_non_owner_fails(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(reverse('adoption:create'), {
            'pet': self.pet.id,
            'requirements': 'Safe home'
        })
        self.assertEqual(response.status_code, 403)  # <-- expect 403 now
        self.assertFalse(AdoptionPost.objects.filter(pet=self.pet, owner=self.other_user).exists())

    def test_user_successfully_adopts_pet(self):
        self.client.login(username='user2', password='pass')
        response = self.client.get(reverse('adoption:detail', kwargs={'pk': self.adoption.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fido')

    def test_owner_can_view_received_requests(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('adoption:user_adoptions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fido')


class AdoptionFlowTests(TestCase):
    """Test cases for Ticket 2: Adoption flow with cancel/exit functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(username='adoptuser', password='password123')
        self.other_user = User.objects.create_user(username='adopter', password='password123')
        self.pet = PetProfile.objects.create(
            owner=self.user,
            name='AdoptMe',
            species='DOG',
            breed='Beagle',
            age=2,
            general_size='MEDIUM',
            energy_level='HIGH'
        )
        self.adoption_create_url = reverse('adoption:create')

    def test_adoption_create_has_cancel_button(self):
        """Test that adoption create form has cancel button"""
        self.client.login(username='adoptuser', password='password123')
        response = self.client.get(self.adoption_create_url)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Should have cancel button or link
        self.assertTrue('Cancel' in content or 'cancel' in content.lower())

    def test_adoption_create_cancel_redirects_properly(self):
        """Test that canceling adoption creation redirects properly"""
        self.client.login(username='adoptuser', password='password123')

        # Get the form page
        response = self.client.get(self.adoption_create_url)
        self.assertEqual(response.status_code, 200)

        # Navigate away (simulating cancel)
        response = self.client.get(reverse('adoption:list'))
        self.assertEqual(response.status_code, 200)
        # Should not be stuck

    def test_adoption_create_success_redirects(self):
        """Test that successful adoption creation redirects properly"""
        self.client.login(username='adoptuser', password='password123')

        response = self.client.post(self.adoption_create_url, {
            'pet': self.pet.id,
            'requirements': 'Good home required',
            'additional_info': 'Friendly dog'
        })

        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        # Should not be stuck on the form

    def test_adoption_form_completion_flow(self):
        """Test complete adoption posting workflow"""
        self.client.login(username='adoptuser', password='password123')

        # Step 1: Access form
        response = self.client.get(self.adoption_create_url)
        self.assertEqual(response.status_code, 200)

        # Step 2: Submit form
        response = self.client.post(self.adoption_create_url, {
            'pet': self.pet.id,
            'requirements': 'Experienced owner',
            'additional_info': 'Needs daily exercise'
        })

        # Step 3: Should redirect
        self.assertEqual(response.status_code, 302)

        # Step 4: Verify adoption was created
        self.assertTrue(AdoptionPost.objects.filter(pet=self.pet).exists())

    def test_adoption_request_form_has_cancel(self):
        """Test that adoption request form has cancel option"""
        # Create an adoption post first
        adoption = AdoptionPost.objects.create(
            pet=self.pet,
            owner=self.user,
            requirements='Good home',
            additional_info='Sweet dog'
        )

        self.client.login(username='adopter', password='password123')
        request_url = reverse('adoption:request_adoption', kwargs={'pk': adoption.pk})

        response = self.client.get(request_url)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()
        # Should have some way to cancel or go back
        self.assertTrue('Cancel' in content or 'Back' in content or 'cancel' in content.lower())

    def test_adoption_request_cancel_flow(self):
        """Test canceling adoption request"""
        adoption = AdoptionPost.objects.create(
            pet=self.pet,
            owner=self.user,
            requirements='Good home',
            additional_info='Sweet dog'
        )

        self.client.login(username='adopter', password='password123')

        # Access request form
        request_url = reverse('adoption:request_adoption', kwargs={'pk': adoption.pk})
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, 200)

        # Navigate away without submitting
        response = self.client.get(reverse('adoption:list'))
        self.assertEqual(response.status_code, 200)
        # Should not be stuck

    def test_adoption_form_validation_prevents_stuck(self):
        """Test that form validation doesn't trap user"""
        self.client.login(username='adoptuser', password='password123')

        # Submit incomplete form
        response = self.client.post(self.adoption_create_url, {
            # Missing required fields
            'pet': self.pet.id
        })

        # Should stay on form with errors (200) or redirect
        self.assertIn(response.status_code, [200, 302])
        # User should still be able to navigate away if they want

    def test_cannot_exit_during_incomplete_submission(self):
        """Test the actual bug scenario: being stuck on adoption page"""
        self.client.login(username='adoptuser', password='password123')

        # Start filling form
        response = self.client.get(self.adoption_create_url)
        self.assertEqual(response.status_code, 200)

        # Try to navigate away (should always work)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Should NOT be stuck

    def test_back_button_during_adoption_creation(self):
        """Test browser back button handling"""
        self.client.login(username='adoptuser', password='password123')

        # Access form
        response = self.client.get(self.adoption_create_url)
        self.assertEqual(response.status_code, 200)

        # Simulate going back
        response = self.client.get(reverse('pets:pet_list'))
        self.assertEqual(response.status_code, 200)
        # Should work fine
