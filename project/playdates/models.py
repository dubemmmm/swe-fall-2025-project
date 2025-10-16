from django.db import models
from pets.models import PetProfile
from users.models import User

# Create your models here.
class Playdate(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)