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
        if data['fecha_limite'] > data['fecha_reembolso']:
            raise serializers.ValidationError("La fecha limite no puede estar después de la fecha de reembolso")
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
        if data['monto_invertido'] > data['usuario'].saldo:
            raise serializers.ValidationError("No tiene saldo suficiente")

        if data['monto_invertido'] > data['idea'].monto_objetivo - data['idea'].monto_actual:
            raise serializers.ValidationError("La inversión no puede ser mayor a lo que falta para el límite.")
        
        if data['usuario'] == data['idea'].usuario:
            raise serializers.ValidationError("No puede invertir en su propia idea.")
        
        if data['idea'].estado != "publica":
            raise serializers.ValidationError("No se puede invertir en la idea.")

        return data