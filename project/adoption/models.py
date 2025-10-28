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
