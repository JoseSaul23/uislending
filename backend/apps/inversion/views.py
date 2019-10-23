from django.shortcuts import render
from rest_framework import viewsets, generics, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser import utils
from djoser.serializers import TokenCreateSerializer
from . import models
from . import serializers
from . import services
from djoser.conf import settings

class UserView(viewsets.ModelViewSet):
    queryset = services.getUsuarios()
    serializer_class = serializers.UserSerializer

    #Listar ideas publicadas por un usuario    
    @action(detail=True, methods=['GET'], name='Ideas publicadas')
    def ideas(self, request, *args, **kwargs):
        usuario = self.get_object()
        #queryset = models.Idea.objects.all().filter(usuario=usuario)
        queryset = services.getIdeas(usuario=usuario)
        serializer = serializers.IdeaSerializer(queryset, many=True)
        return Response(serializer.data)

    #Listar inversiones realizadas por un usuario 
    @action(detail=True, methods=['GET'], name='Inversiones realizadas')
    def inversiones(self, request, *args, **kwargs):
        usuario = self.get_object()
        queryset = services.getInversiones(usuario=usuario)
        serializer = serializers.InversionSerializer(queryset, many=True)
        return Response(serializer.data)     

class CategoriaView(viewsets.ModelViewSet):
    queryset = services.getCategorias()
    serializer_class = serializers.CategoriaSerializer

    #Listar ideas por categoria    
    @action(detail=True, methods=['GET'], name='Ideas de categoria')
    def ideas(self, request, *args, **kwargs):
        categoria = self.get_object()
        queryset = services.getIdeas(categoria=categoria)
        serializer = serializers.IdeaSerializer(queryset, many=True)
        return Response(serializer.data)

class IdeaPagination(pagination.PageNumberPagination):
    page_size = 4

class IdeaView(viewsets.ModelViewSet):
    queryset = services.getIdeas()
    serializer_class = serializers.IdeaSerializer
    pagination_class = IdeaPagination

    #Listar inversiones hechas a una idea
    @action(detail=True, methods=['GET'], name='Inversiones de la idea')
    def inversiones(self, request, *args, **kwargs):
        idea = self.get_object()
        queryset = services.getInversiones(idea=idea)
        serializer = serializers.InversionSerializer(queryset, many=True)
        return Response(serializer.data)

class InversionView(viewsets.ModelViewSet):
    queryset = services.getInversiones()
    serializer_class = serializers.InversionSerializer

class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    serializer_class = TokenCreateSerializer
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        content = {
            'token': token_serializer_class(token).data["auth_token"],
            'id': serializer.user.id
        }
        return Response(data=content,status=status.HTTP_200_OK,)