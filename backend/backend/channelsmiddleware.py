from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.db import close_old_connections
from django.contrib.auth.models import AnonymousUser

class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        close_old_connections()
        query = dict((x.split('=') for x in scope['query_string'].decode().split("&")))
        token = query['token']
        try:
            token = Token.objects.get(key=token)
        except Token.DoesNotExist as e:
            print(e)
            return None
        else:
            scope['user'] = token.user

        return self.inner(scope)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))

