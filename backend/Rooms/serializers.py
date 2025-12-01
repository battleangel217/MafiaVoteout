from rest_framework import serializers
from .models import *


class RoomSerializer(serializers.ModelSerializer):
    player_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = RoomModel
        fields = '__all__'