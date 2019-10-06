from django.shortcuts import render
from rest_framework import viewsets
from . import models
from . import serializers

class UserView(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

class CategoriaView(viewsets.ModelViewSet):
    queryset = models.Categoria.objects.all()
    serializer_class = serializers.CategoriaSerializer

class IdeaView(viewsets.ModelViewSet):
    queryset = models.Idea.objects.all()
    serializer_class = serializers.IdeaSerializer

class InversionView(viewsets.ModelViewSet):
    queryset = models.Inversion.objects.all()
    serializer_class = serializers.InversionSerializer