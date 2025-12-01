from django.urls import path
from .views import RoomViews, AllRooms

urlpatterns = [
    path('', RoomViews.as_view(), name="room"),
    path('all', AllRooms.as_view(), name="all rooms")
]