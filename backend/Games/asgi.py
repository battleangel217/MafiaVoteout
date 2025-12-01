"""
ASGI config for Games project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# ...existing code...
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import lobby.routing
import vote.routing
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Games.settings')

# Combine websocket URL patterns from lobby and vote into a single router.
# Use getattr to avoid AttributeError if a module doesn't define websocket_urlpatterns.
websocket_urlpatterns = (
    getattr(lobby.routing, 'websocket_urlpatterns', [])
    + getattr(vote.routing, 'websocket_urlpatterns', [])
)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
# ...existing code...
