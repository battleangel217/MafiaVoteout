from django.shortcuts import render
from .models import PlayerModel
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
        if player_count.count() > 7:
            return Response({"message":"Room full"}, status=401)
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)