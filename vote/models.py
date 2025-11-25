from django.db import models
from Rooms.models import RoomModel
from Players.models import PlayerModel

class VoteModel(models.Model):
    """Track individual votes cast during voting phase"""
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(PlayerModel, on_delete=models.CASCADE, related_name='votes_cast')
    votee = models.ForeignKey(PlayerModel, on_delete=models.CASCADE, related_name='votes_received')
    timestamp = models.DateTimeField(auto_now_add=True)
    round_number = models.IntegerField(default=1)

    class Meta:
        unique_together = ('room', 'voter', 'round_number')  # One vote per voter per round
        indexes = [
            models.Index(fields=['room', 'round_number']),
        ]

    def __str__(self):
        return f"{self.voter.username} → {self.votee.username} (Room: {self.room.code})"
