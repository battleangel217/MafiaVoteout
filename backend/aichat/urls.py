from django.urls import path
from .views import AIAgent

urlpatterns = [
    path('', AIAgent.as_view(), name="Ai helper")
]