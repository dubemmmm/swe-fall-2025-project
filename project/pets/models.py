from django.db import models
from users.models import User
# Create your models here.
# pets/models.py

class PetProfile(models.Model):
    SPECIES_CHOICES = [('DOG', 'Dog'), ('CAT', 'Cat'), ('OTHER', 'Other')]
    SIZE_CHOICES = [('SMALL', 'Small'), ('MEDIUM', 'Medium'), ('LARGE', 'Large')]
    ENERGY_CHOICES = [('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100, blank=True)
    age = models.CharField(max_length=50)
    general_size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    energy_level = models.CharField(max_length=20, choices=ENERGY_CHOICES)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    color_markings = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_playdate_available = models.BooleanField(default=False)
    is_adoptable = models.BooleanField(default=False)
    privacy_settings = models.CharField(max_length=20, default='PUBLIC')
    created_at = models.DateTimeField(auto_now_add=True)
    
class PetPhoto(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='pets/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class PetTrait(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='traits')
    trait = models.CharField(max_length=50)  # Friendly, Energetic, Social, etc.