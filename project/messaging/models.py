from django.db import models
from users.models import User
from playdates.models import Playdate
# Create your models here.
class MessageThread(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads_as_user2')
    playdate = models.ForeignKey(Playdate, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user1', 'user2']

class Message(models.Model):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    photo = models.ImageField(upload_to='messages/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)