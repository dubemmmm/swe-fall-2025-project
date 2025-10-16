from django.db import models
from users.models import User
# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.TextField()
    photo = models.ImageField(upload_to='posts/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class CommunityAlert(models.Model):
    ALERT_TYPES = [('LOST', 'Lost Pet'), ('FOUND', 'Found Pet'), ('EMERGENCY', 'Emergency')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    pet_type = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20, blank=True)
    color_markings = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    contact_info = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='alerts/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)