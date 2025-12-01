from django.db import models

# Create your models here.

CHOICES = [
    ('private', 'private'),
    ('public', 'public')
]

class RoomModel(models.Model):
    username = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=15, choices=CHOICES)
    code = models.CharField(max_length=7, primary_key=True)
    started = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return self.username

    def get_messages(self):
        return list(self.room.values_list("message", flat=True))