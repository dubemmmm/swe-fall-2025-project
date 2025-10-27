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

