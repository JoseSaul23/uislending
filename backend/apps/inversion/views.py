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
from rest_framework import permissions
   

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


class IdeaView(viewsets.ModelViewSet):
    serializer_class = serializers.IdeaSerializer
    pagination_class = IdeaPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    #para que solo alguien autenticado pueda editar sus ideas.
    #readonly; mostrar cuando no este autenticado
    #IsAuth; mostrar y dejar editar ideas cuando este autenticado
    http_method_names = ['get', 'post', 'put', 'head','options']
    
    if not Task.objects.filter(verbose_name="Recorrer Ideas").exists():
        recorrerIdeas(verbose_name="Recorrer Ideas", repeat=86400)
    
    def get_queryset(self):
        """
        Esta vista deberia de regresar las ideas publicas
        si no hay un usuario en la peticion, con un usuario
        regresa solo las ideas del usuario.
        """
        queryset = Idea.publicas.all() #publicas; mostrar publicas cuando no este autenticado
        user = self.request.user
        if user.id is not None:
            return Idea.objects.filter(usuario=user) #usuario; mostrar las ideas del usuario autenticado
        return queryset

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    #Listar inversiones hechas a una idea
    @action(detail=True, methods=['GET'], name='Inversiones de la idea')
    def inversiones(self, request, *args, **kwargs):
        idea = self.get_object()
        queryset = Inversion.objects.filter(idea=idea)
        serializer = serializers.InversionSerializer(queryset, many=True)
        return Response(serializer.data)


class InversionView(viewsets.ModelViewSet):
    serializer_class = serializers.InversionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head','options']

    def get_queryset(self):
        """
        Regresa las inversiones hechas por el usuario
        que realiza la petición.
        """
        user = self.request.user
        return Inversion.objects.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    serializer_class = TokenCreateSerializer
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        content = {
            'token': token_serializer_class(token).data["auth_token"],
            'imagen': 'http://saulvega.pythonanywhere.com'+serializer.user.imagen.url,
        }
        return Response(data=content,status=status.HTTP_200_OK,)