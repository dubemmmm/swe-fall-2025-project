from django.db import models
from users.models import User
from pets.models import PetProfile

class AdoptionPost(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    requirements = models.TextField()
    additional_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # NEW FIELD

    def __str__(self):
        return f"{self.pet.name} adoption by {self.owner.username}"


class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    adoption_post = models.ForeignKey(AdoptionPost, on_delete=models.CASCADE, related_name='requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_requests')

    # Requester Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    # Housing Information
    housing_type = models.CharField(max_length=100, help_text="e.g., House, Apartment, Condo")
    owns_or_rents = models.CharField(max_length=20, choices=[('own', 'Own'), ('rent', 'Rent')])
    has_yard = models.BooleanField(default=False)
    landlord_approval = models.BooleanField(default=False, help_text="If renting, do you have landlord approval?")

    # Pet Experience
    has_pets_currently = models.BooleanField(default=False)
    current_pets_description = models.TextField(blank=True, help_text="Describe your current pets")
    previous_pet_experience = models.TextField(help_text="Describe your previous experience with pets")

    # Adoption Motivation
    why_adopt = models.TextField(help_text="Why do you want to adopt this pet?")
    daily_care_plan = models.TextField(help_text="How will you care for this pet daily?")

    # Additional Information
    veterinarian_info = models.TextField(blank=True, help_text="Your veterinarian's contact information (optional)")
    references = models.TextField(blank=True, help_text="Personal references (optional)")
    additional_notes = models.TextField(blank=True)

    # Status and Timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['adoption_post', 'requester']  # One request per user per post
        ordering = ['-created_at']

    def __str__(self):
        return f"Adoption request for {self.adoption_post.pet.name} by {self.requester.username}"
