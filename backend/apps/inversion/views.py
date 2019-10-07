from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models
from . import serializers
from . import services

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

class IdeaView(viewsets.ModelViewSet):
    queryset = services.getIdeas()
    serializer_class = serializers.IdeaSerializer

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