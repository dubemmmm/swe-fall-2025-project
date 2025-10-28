from django.db import models
from pets.models import PetProfile
from users.models import User

# Create your models here.
class Playdate(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),  # Open for anyone to request to join
        ('CONFIRMED', 'Confirmed'),  # At least one participant confirmed
        ('CANCELLED', 'Cancelled'),  # Cancelled by organizer
        ('COMPLETED', 'Completed'),  # Playdate finished
    ]

    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_playdates')
    organizer_pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='organized_playdates')
    scheduled_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="Add details about the playdate")
    max_participants = models.IntegerField(default=5, help_text="Maximum number of pets (including organizer's pet)")
    is_public = models.BooleanField(default=True, help_text="If True, appears in browse page for anyone to request")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Playdate: {self.organizer_pet.name} at {self.location} on {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"

    def get_accepted_count(self):
        """Return count of accepted participants (excluding organizer)"""
        return self.participants.filter(status='ACCEPTED').count()

    def get_available_spots(self):
        """Return number of available spots"""
        return self.max_participants - 1 - self.get_accepted_count()  # -1 for organizer's pet

    def is_full(self):
        """Check if playdate is full"""
        return self.get_available_spots() <= 0

    class Meta:
        ordering = ['-scheduled_time']


class PlaydateParticipant(models.Model):
    PARTICIPANT_STATUS_CHOICES = [
        ('INVITED', 'Invited'),  # Directly invited by organizer, waiting for user response
        ('REQUESTED', 'Requested'),  # User requested to join, waiting for organizer approval
        ('ACCEPTED', 'Accepted'),  # Confirmed participation (either accepted invitation or approved request)
        ('DECLINED', 'Declined'),  # Declined by user (for invitations) or organizer (for requests)
    ]

    playdate = models.ForeignKey(Playdate, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playdate_participations')
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='playdate_participations')
    status = models.CharField(max_length=20, choices=PARTICIPANT_STATUS_CHOICES, default='INVITED')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.pet.name} - {self.status} for playdate on {self.playdate.scheduled_time.strftime('%Y-%m-%d')}"

    def is_invitation(self):
        """Check if this is an invitation (vs a request)"""
        return self.status in ['INVITED', 'ACCEPTED', 'DECLINED'] and hasattr(self, '_is_invite')

    class Meta:
        unique_together = ['playdate', 'pet']
        ordering = ['-created_at']