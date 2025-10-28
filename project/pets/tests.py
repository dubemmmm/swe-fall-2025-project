from django.test import TestCase
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from users.models import User
from .models import PetProfile, PetPhoto, PetTrait

class PetProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.pet_profile = PetProfile.objects.create(
            owner=self.user,
            name='Buddy',
            species='DOG',
            breed='Golden Retriever',
            age='2 years',
            general_size='MEDIUM',
            energy_level='HIGH',
            weight=30.50,
            is_playdate_available=True,
            is_adoptable=False,
            privacy_settings='PUBLIC'
        )

    def test_pet_profile_creation(self):
        self.assertEqual(self.pet_profile.name, 'Buddy')
        self.assertEqual(self.pet_profile.owner, self.user)
        self.assertTrue(self.pet_profile.is_playdate_available)
        self.assertFalse(self.pet_profile.is_adoptable)

    def test_pet_profile_str(self):
        self.assertEqual(str(self.pet_profile), 'Buddy (Dog)')

class PetPhotoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser2', email='test2@example.com', password='password123')
        self.pet_profile = PetProfile.objects.create(
            owner=self.user,
            name='Whiskers',
            species='CAT',
            age='1 year',
            general_size='SMALL',
            energy_level='LOW'
        )
        # Create a dummy image file
        image_content = b"GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        self.photo_file = SimpleUploadedFile("cat.gif", image_content, content_type="image/gif")
        self.pet_photo = PetPhoto.objects.create(
            pet=self.pet_profile,
            photo=self.photo_file,
            is_primary=True
        )

    def test_pet_photo_creation(self):
        self.assertEqual(self.pet_photo.pet, self.pet_profile)
        self.assertTrue(self.pet_photo.is_primary)
        self.assertIn('pets/', self.pet_photo.photo.name)

class PetTraitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser3', email='test3@example.com', password='password123')
        self.pet_profile = PetProfile.objects.create(
            owner=self.user,
            name='Max',
            species='DOG',
            age='3 years',
            general_size='LARGE',
            energy_level='MEDIUM'
        )
        self.pet_trait = PetTrait.objects.create(
            pet=self.pet_profile,
            trait='Friendly'
        )

    def test_pet_trait_creation(self):
        self.assertEqual(self.pet_trait.pet, self.pet_profile)
        self.assertEqual(self.pet_trait.trait, 'Friendly')

    def test_pet_trait_str(self):
        self.assertEqual(str(self.pet_trait), 'Friendly for Max')


class PetProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password123')

        self.pet1 = PetProfile.objects.create(
            owner=self.user1,
            name='Fido',
            species='DOG',
            age='3 years',
            general_size='MEDIUM',
            bio='A friendly dog.', # Added bio
            privacy_settings='PUBLIC' # Added privacy_settings
        )

    def test_pet_list_view_authenticated(self):
        """Test that an authenticated user can see their own pets but not others'."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('pet_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fido')
        self.assertIn(self.pet1, response.context['object_list'])

        # Create a pet for user2
        PetProfile.objects.create(owner=self.user2, name='Whiskers', species='CAT', age='1 year')
        
        # user1 should still only see their own pet
        response = self.client.get(reverse('pet_list'))
        self.assertNotContains(response, 'Whiskers')
        self.assertEqual(len(response.context['object_list']), 1)

    def test_pet_list_view_unauthenticated(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(reverse('pet_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/users/login/?next=/pets/')

    def test_pet_detail_view(self):
        """Test that a logged-in user can view a pet's detail page."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('pet_detail', kwargs={'pk': self.pet1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fido')
        self.assertEqual(response.context['pet'], self.pet1)

    def test_pet_create_view_get(self):
        """Test that an authenticated user can access the create pet page."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('pet_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pets/petprofile_form.html')

    def test_pet_create_view_post(self):
        """Test that an authenticated user can create a pet."""
        self.client.login(username='user1', password='password123')
        pet_data = {
            'name': 'Rex',
            'species': 'DOG',
            'breed': 'German Shepherd',
            'age': '4 years',
            'general_size': 'LARGE',
            'energy_level': 'HIGH',
            'weight': 85.0,
            'bio': 'A loyal companion.',
            'is_playdate_available': True,
            'privacy_settings': 'PUBLIC'
        }
        response = self.client.post(reverse('pet_create'), data=pet_data)
        
        self.assertEqual(PetProfile.objects.count(), 2)
        new_pet = PetProfile.objects.get(name='Rex')
        self.assertEqual(new_pet.owner, self.user1)
        self.assertRedirects(response, reverse('pet_detail', kwargs={'pk': new_pet.pk}))

    def test_pet_update_view_owner(self):
        """Test that the owner can update their pet's profile."""
        self.client.login(username='user1', password='password123')
        updated_data = {
            'name': 'Fido Updated',
            'species': self.pet1.species,
            'age': self.pet1.age,
            'breed': self.pet1.breed,
            'general_size': self.pet1.general_size,
            'energy_level': self.pet1.energy_level or 'MEDIUM',
            'bio': self.pet1.bio,
            'privacy_settings': self.pet1.privacy_settings,
            'is_playdate_available': self.pet1.is_playdate_available,
            'weight': self.pet1.weight or '',
        }
        response = self.client.post(reverse('pet_update', kwargs={'pk': self.pet1.pk}), data=updated_data)
        
        self.assertRedirects(response, reverse('pet_detail', kwargs={'pk': self.pet1.pk}))
        self.pet1.refresh_from_db()
        self.assertEqual(self.pet1.name, 'Fido Updated')

    def test_pet_update_view_not_owner(self):
        """Test that a non-owner receives a 403 Forbidden error when trying to update."""
        self.client.login(username='user2', password='password123')
        updated_data = {'name': 'Hacked Fido', 'species': self.pet1.species, 'age': self.pet1.age, 'general_size': self.pet1.general_size}
        
        # Test GET request
        response_get = self.client.get(reverse('pet_update', kwargs={'pk': self.pet1.pk}))
        self.assertEqual(response_get.status_code, 403)

        # Test POST request
        response_post = self.client.post(reverse('pet_update', kwargs={'pk': self.pet1.pk}), data=updated_data)
        self.assertEqual(response_post.status_code, 403)

        self.pet1.refresh_from_db()
        self.assertNotEqual(self.pet1.name, 'Hacked Fido')

    def test_pet_delete_view_owner(self):
        """Test that the owner can delete their pet's profile."""
        self.client.login(username='user1', password='password123')
        
        # Test GET request to confirmation page
        response_get = self.client.get(reverse('pet_delete', kwargs={'pk': self.pet1.pk}))
        self.assertEqual(response_get.status_code, 200)
        self.assertContains(response_get, 'Are you sure you want to delete')

        # Test POST request to delete
        response_post = self.client.post(reverse('pet_delete', kwargs={'pk': self.pet1.pk}))
        self.assertRedirects(response_post, reverse('pet_list'))
        
        with self.assertRaises(PetProfile.DoesNotExist):
            PetProfile.objects.get(pk=self.pet1.pk)
        
        self.assertEqual(PetProfile.objects.count(), 0)

    def test_pet_delete_view_not_owner(self):
        """Test that a non-owner receives a 403 Forbidden error when trying to delete."""
        self.client.login(username='user2', password='password123')

        # Test GET request
        response_get = self.client.get(reverse('pet_delete', kwargs={'pk': self.pet1.pk}))
        self.assertEqual(response_get.status_code, 403)

        # Test POST request
        response_post = self.client.post(reverse('pet_delete', kwargs={'pk': self.pet1.pk}))
        self.assertEqual(response_post.status_code, 403)

        self.assertEqual(PetProfile.objects.count(), 1)
