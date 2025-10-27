from django.db import models
from users.models import User
from pets.models import PetProfile

class AdoptionPost(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name="adoption_posts")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="adoption_posts", default=1)
    requirements = models.TextField()
    additional_info = models.TextField(blank=True)
    
    # Fields admin expects
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)  # useful for ordering

    def __str__(self):
        return f"{self.pet.name} adoption by {self.owner.username}"

    class Meta:
        ordering = ['-created_at']
