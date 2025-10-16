from django.db import models
from pets.models import PetProfile
# Create your models here.
class AdoptionPost(models.Model):
    pet = models.OneToOneField(PetProfile, on_delete=models.CASCADE)
    additional_info = models.TextField()
    adoption_requirements = models.TextField(blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)