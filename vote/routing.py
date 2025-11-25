from django.urls import re_path
from .consumers import VotingConsumer

# Match the path used by the frontend: /ws/voting/<code>/
websocket_urlpatterns = [
    re_path(r'ws/voting/(?P<code>\w+)/$', VotingConsumer.as_asgi())
]