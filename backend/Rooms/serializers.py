from rest_framework import serializers
from .models import *


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomModel
        fields = '__all__'