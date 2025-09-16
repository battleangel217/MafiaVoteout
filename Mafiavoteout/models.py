from django.db import models

# Create your models here.

class Room(models.Model):
    username = models.CharField(max_length=100, unique=True)
    code = models.IntegerField(primary_key=True)
    started = models.BooleanField(default=True)

    def __str__(self):
        return self.username

class Player(models.Model):
    username = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=100, default='Not Mafia')
    vote = models.IntegerField(default=0)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_code')

    def __str__(self):
        return self.username