from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Pet, AdoptionListing, AdoptionRequest


class AdoptionFlowTestCase(TestCase):
    def setUp(self):
        # Create two users
        self.owner = User.objects.create_user(username="owner", password="test123")
        self.adopter = User.objects.create_user(username="adopter", password="test123")

        # Log in as owner initially
        self.client.login(username="owner", password="test123")

        # Create a pet
        self.pet = Pet.objects.create(
            owner=self.owner,
            name="Luna",
            age=3,
            breed="Beagle",
            description="Friendly and trained",
            is_adoptable=True
        )

    # ---------------------------------------------------------
    # ✅ SUCCESS SCENARIOS
    # ---------------------------------------------------------

    def test_user_successfully_lists_pet_for_adoption(self):
        """
        ✅ Test if a user can successfully list a pet for adoption.
        """
        url = reverse("post_for_adoption", args=[self.pet.id])
        response = self.client.post(url, {
            "requirements": "Loving family required",
            "additional_info": "Vaccinated and active",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(AdoptionListing.objects.filter(pet=self.pet).exists())

    def test_user_can_view_pets_for_adoption(self):
        """
        ✅ Test if user can view list of pets up for adoption.
        """
        AdoptionListing.objects.create(
            pet=self.pet,
            posted_by=self.owner,
            requirements="Calm family",
            additional_info="Trained and friendly"
        )
        url = reverse("view_adoption_listings")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Luna")

    def test_user_successfully_adopts_pet(self):
        """
        ✅ Test if a user can successfully send adoption request.
        """
        listing = AdoptionListing.objects.create(
            pet=self.pet,
            posted_by=self.owner,
            requirements="Responsible home",
            additional_info="Healthy"
        )

        self.client.logout()
        self.client.login(username="adopter", password="test123")

        url = reverse("send_adoption_request", args=[listing.id])
        response = self.client.post(url, {"message": "I would love to adopt Luna!"})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(AdoptionRequest.objects.filter(listing=listing, requester=self.adopter).exists())

    def test_owner_can_view_received_requests(self):
        """
        ✅ Test if the owner can view requests received for their pets.
        """
        listing = AdoptionListing.objects.create(
            pet=self.pet,
            posted_by=self.owner,
            requirements="Good home",
            additional_info="Playful"
        )

        AdoptionRequest.objects.create(
            listing=listing,
            requester=self.adopter,
            message="Can provide a great home!"
        )

        url = reverse("view_received_requests")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Can provide a great home!")
        self.assertContains(response, "Luna")

    # ---------------------------------------------------------
    # ❌ FAILURE SCENARIOS
    # ---------------------------------------------------------

    def test_listing_pet_for_adoption_fails_missing_fields(self):
        """
        ❌ Test listing a pet for adoption fails when required fields are missing.
        """
        url = reverse("post_for_adoption", args=[self.pet.id])
        response = self.client.post(url, {"requirements": ""})  # Missing additional_info

        self.assertEqual(response.status_code, 200)  # Form re-renders
        self.assertFalse(AdoptionListing.objects.filter(pet=self.pet).exists())

    def test_user_fails_to_adopt_pet_when_not_logged_in(self):
        """
        ❌ Test if unauthenticated user fails to send an adoption request.
        """
        listing = AdoptionListing.objects.create(
            pet=self.pet,
            posted_by=self.owner,
            requirements="Loving home",
            additional_info="Friendly dog"
        )

        self.client.logout()
        url = reverse("send_adoption_request", args=[listing.id])
        response = self.client.post(url, {"message": "I want to adopt Luna"})

        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn("/login/", response.url)
        self.assertFalse(AdoptionRequest.objects.filter(listing=listing).exists())

    def test_user_fails_to_list_other_users_pet_for_adoption(self):
        """
        ❌ Test if a user tries to list another user's pet for adoption.
        """
        self.client.logout()
        self.client.login(username="adopter", password="test123")  # Adopter tries to list owner’s pet

        url = reverse("post_for_adoption", args=[self.pet.id])
        response = self.client.post(url, {
            "requirements": "Calm family",
            "additional_info": "Cute dog",
        })

        # Should be blocked or redirected (depending on view logic)
        self.assertIn(response.status_code, [302, 403])
        self.assertFalse(AdoptionListing.objects.filter(pet=self.pet, posted_by=self.adopter).exists())


# Create your tests here.
