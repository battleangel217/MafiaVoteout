from django.shortcuts import render, get_object_or_404
from .models import PlayerModel
from Rooms.models import RoomModel
from .serializers import PlayerSerializer
from rest_framework.views import Response, APIView, status

# Create your views here.

class PlayerViews(APIView):
    def get(self, request):
        code = request.GET.get('code')
        data = PlayerModel.objects.filter(room=code)

        serializer = PlayerSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        code = request.data["room"]
        player_count = PlayerModel.objects.filter(room=code)
        try:
            room = RoomModel.objects.get(code=code)
            if room.started:
                return Response({"message":"Game has started"}, status=status.HTTP_401_UNAUTHORIZED)
        except RoomModel.DoesNotExist:
            return Response({'message': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
            
        if player_count.count() > 7:
            return Response({"message":"Room full"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)