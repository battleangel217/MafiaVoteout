from django.db import models
from Rooms.models import RoomModel


class MessageModel(models.Model):
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, related_name="room")
    message = models.TextField()