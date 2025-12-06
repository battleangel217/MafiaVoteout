from django.db import models
from Rooms.models import *

# Create your models here.

class PlayerModel(models.Model):
    username = models.CharField(max_length=100, unique=True)
    is_mafia = models.BooleanField(default=False)
    vote = models.IntegerField(default=0)
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, related_name='room_code')
    is_admin = models.BooleanField(default=False)
    online = models.BooleanField(default=False)

    def as_dict(self):
        return {
            "username": self.username,
            "isAdmin": self.is_admin,
            "online": self.online,
            "isMafia": self.is_mafia,
            "vote": self.vote
        }

    class Meta:
        # composite index to speed up queries that filter by room and online status
        indexes = [
            models.Index(fields=["room", "online"]),
        ]