from channels.layers import get_channel_layer
#from .serializers import FooSerializer

async def notificacion(usuario, texto):
    group_name = usuario.nombreGrupo
    channel_layer = get_channel_layer()
    content = {
        'notificacion': texto
    }
    await channel_layer.group_send(group_name, {
        # This "type" defines which handler on the Consumer gets
        # called.
        "type": "notificar",
        "content": content,
    })