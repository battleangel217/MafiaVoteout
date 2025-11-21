from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView, Response, status
from Players.models import *
from .serializers import RoomSerializer
import uuid


# Create your views here.


class RoomViews(APIView):
    def get(self, request):
        code = request.GET.get('code')
        data = get_object_or_404(RoomModel, code=code)

        serializer = RoomSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        data = request.data
        data["code"] = uuid.uuid4().hex[:6].upper()
        print(data)

        serializer = RoomSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            try:
                player = PlayerModel.objects.create(username=serializer.data["username"], room_id=serializer.data["code"], isAdmin=True)
                player.save()
            except:
                RoomModel.objects.get(code=data["code"]).delete()
                return Response({"message":"Bomboclat"}, status=status.HTTP_400_BAD_REQUEST)
            
            res = {
                "username":serializer.data["username"],
                "code": serializer.data["code"],
                "isAdmin": True
            }
            return Response(res, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        data = request.data
        roomdata = get_object_or_404(RoomModel, code=data["code"])
        playernumber = PlayerModel.objects.filter(room=roomdata).count()

        if playernumber < 3:
            return Response({"message":"Must be up to 3 players"})
        serializer = RoomSerializer(RoomModel, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Room started"}, status=status.HTTP_200_OK)


    def delete(self, request):
        data = request.data
        roomdata = get_object_or_404(RoomModel, code=data["code"])
        roomdata.delete()
        return Response({"message":"Room closed"}, status=status.HTTP_200_OK)
