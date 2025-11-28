from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

# Create your views here.


class HealthView(APIView):
    def get(self, request):
        return Response({
            "status": "healthy",
            "timestamp": timezone.now(),
            "service": "MafiaVoteout Api Service",
            "author": "Idaraobong"
        }, status=status.HTTP_200_OK)
