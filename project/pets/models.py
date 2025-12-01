from django.db import models
from users.models import User

class PetProfile(models.Model):
    SPECIES_CHOICES = [('DOG', 'Dog'), ('CAT', 'Cat'), ('OTHER', 'Other')]
    GENDER_CHOICES = [('MALE', 'Male'), ('FEMALE', 'Female'), ('UNKNOWN', 'Unknown')]
    SIZE_CHOICES = [('SMALL', 'Small'), ('MEDIUM', 'Medium'), ('LARGE', 'Large')]
    ENERGY_CHOICES = [('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')]
    PRIVACY_CHOICES = [('PUBLIC', 'Public'), ('FRIENDS', 'Friends Only'), ('PRIVATE', 'Private')]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='UNKNOWN')
    breed = models.CharField(max_length=100, blank=True)
    age = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='pet_profiles/', null=True, blank=True)
    general_size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    energy_level = models.CharField(max_length=20, choices=ENERGY_CHOICES)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Weight in lbs")
    color_markings = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    is_playdate_available = models.BooleanField(default=False)
    is_adoptable = models.BooleanField(default=False)
    privacy_settings = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='PUBLIC')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"
    
class PetPhoto(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='pets/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.pet.name}"

class PetTrait(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='traits')
    trait = models.CharField(max_length=50)  # Friendly, Energetic, Social, etc.

    def __str__(self):
        return f"{self.trait} for {self.pet.name}"