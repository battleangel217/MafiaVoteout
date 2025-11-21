from django.db import models
from Rooms.models import *

# Create your models here.

class PlayerModel(models.Model):
    username = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=100, default='Not Mafia')
    vote = models.IntegerField(default=0)
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, related_name='room_code')
    isAdmin = models.BooleanField(default=False)

    def __str__(self):
        return self.username