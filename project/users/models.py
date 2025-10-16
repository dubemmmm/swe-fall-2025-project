from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    profile_name = models.CharField(max_length=100)

    # Location fields
    location = models.CharField(max_length=255, help_text="Human-readable address (e.g., 'New York, NY')")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitude coordinate")

    profile_photo = models.ImageField(upload_to='profiles/', blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username