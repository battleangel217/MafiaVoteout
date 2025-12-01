from django.urls import path
from .views import RoomViews

urlpatterns = [
    path('', RoomViews.as_view(), name="room"),
    path('all', RoomViews.as_view(), name="all rooms")
]