from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
import logging
logger = logging.getLogger(__name__)

class NotifacionConsumer(AsyncJsonWebsocketConsumer):
    """
    This Notification consumer handles websocket connections for clients.
    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async.
    """
    # WebSocket event handlers
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        user = self.scope["user"]
        group_name = user.nombreGrupo
        await self.channel_layer.group_add( 
                group_name,
                self.channel_name,
            )
        await self.accept()
 ########################################
    async def notificar(self, event):
        """
        This handles calls elsewhere in this codebase that look
        like:

            channel_layer.group_send(group_name, {
                'type': 'notify',  # This routes it to this handler.
                'content': json_message,
            })

        Don't try to directly use send_json or anything; this
        decoupling will help you as things grow.
        """
        await self.send_json(event["content"])
##########################################
    async def disconnect(self, code):
        """
        Called when the websocket closes for any reason.
        Leave all the rooms we are still in.
        """
        try:
            user = self.scope["user"]

            # Get the group from which user is to be kicked.
            group_name = user.nombreGrupo

            # kick this channel from the group.
            await self.channel_layer.group_discard(group_name, self.channel_name)
        except Exception as e:
            logger.error(e)