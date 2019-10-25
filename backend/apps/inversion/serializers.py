from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from . import models

class UserSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = models.User
        fields = (
            'id',
            'password',
            'username',
            'first_name',
            'last_name',
            'email',
            'saldo',
            'imagen'
        )


class CategoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Categoria
        fields = (
            'id',
            'nombre'
        )


class IdeaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Idea
        fields = (
            'id',
            'nombre',
            'descripcion',
            'monto_objetivo',
            'monto_actual',
            'intereses',
            'fecha_publicada',
            'fecha_limite',
            'fecha_reembolso',
            'estado',
            'imagen',
            'usuario',
            'categoria',
        )

    def validate(self, data):
        instance = models.Idea(**data)
        instance.clean()
        return data


class InversionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Inversion
        fields = (
            'id',
            'fecha_inversion',
            'monto_invertido',
            'usuario',
            'idea',
        )  

    def validate(self, data):
        instance = models.Inversion(**data)
        instance.clean()
        return data