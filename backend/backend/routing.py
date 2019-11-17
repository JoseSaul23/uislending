from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from apps.inversion import consumers
from channels.auth import AuthMiddlewareStack
from backend.channelsmiddleware import TokenAuthMiddlewareStack

websockets = URLRouter([
    path(
        "ws/notificaciones/",
        consumers.NotifacionConsumer,
        name="ws_notificaciones",
    ),
])

application = ProtocolTypeRouter({
    "websocket": TokenAuthMiddlewareStack(websockets),
})