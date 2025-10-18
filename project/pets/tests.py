from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
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
            description='Friendly and energetic dog.',
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
