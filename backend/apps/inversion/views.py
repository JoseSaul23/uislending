from django.shortcuts import render
from rest_framework import viewsets, generics, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser import utils
from djoser.serializers import TokenCreateSerializer
from .models import *
from . import serializers
from djoser.conf import settings
from background_task.models import Task
from .dailytask import recorrerIdeas

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    #Listar ideas publicadas por un usuario    
    @action(detail=True, methods=['GET'], name='Ideas publicadas')
    def ideas(self, request, *args, **kwargs):
        usuario = self.get_object()
        queryset = Idea.objects.filter(usuario=usuario)
        serializer = serializers.IdeaSerializer(queryset, many=True)
        return Response(serializer.data)

    #Listar inversiones realizadas por un usuario 
    @action(detail=True, methods=['GET'], name='Inversiones realizadas')
    def inversiones(self, request, *args, **kwargs):
        usuario = self.get_object()
        queryset = Inversion.objects.filter(usuario=usuario)
        serializer = serializers.InversionSerializer(queryset, many=True)
        return Response(serializer.data)     


class CategoriaView(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = serializers.CategoriaSerializer

    #Listar ideas por categoria    
    @action(detail=True, methods=['GET'], name='Ideas de categoria')
    def ideas(self, request, *args, **kwargs):
        categoria = self.get_object()
        queryset = Idea.objects.filter(categoria=categoria)
        serializer = serializers.IdeaSerializer(queryset, many=True)
        return Response(serializer.data)


class IdeaPagination(pagination.PageNumberPagination):
    page_size = 10

#listar todas las ideas para poder cambiar estado cuando no son publicas, no listar por accion si no por lista.
class IdeaView(viewsets.ModelViewSet):
    queryset = Idea.publicas.all()
    serializer_class = serializers.IdeaSerializer
    pagination_class = IdeaPagination
    
    if not Task.objects.filter(verbose_name="Recorrer Ideas").exists():
        recorrerIdeas(verbose_name="Recorrer Ideas", repeat=86400)
    
    #Listar inversiones hechas a una idea
    @action(detail=True, methods=['GET'], name='Inversiones de la idea')
    def inversiones(self, request, *args, **kwargs):
        idea = self.get_object()
        queryset = Inversion.objects.filter(idea=idea)
        serializer = serializers.InversionSerializer(queryset, many=True)
        return Response(serializer.data)


class InversionView(viewsets.ModelViewSet):
    queryset = Inversion.objects.all()
    serializer_class = serializers.InversionSerializer


class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    serializer_class = TokenCreateSerializer
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        content = {
            'token': token_serializer_class(token).data["auth_token"],
            'id': serializer.user.id,
            'imagen': 'http://saulvega.pythonanywhere.com'+serializer.user.imagen.url,
        }
        return Response(data=content,status=status.HTTP_200_OK,)