from django.db import models

# Create your models here.


class RoomModel(models.Model):
    username = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=7, primary_key=True)
    started = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return self.username
