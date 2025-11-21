from django.urls import path
from .views import *

urlpatterns = [
    path('', PlayerViews.as_view(), name="player")
]