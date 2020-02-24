from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from . import models


class UserSerializer(UserCreateSerializer):
    imagen = Base64ImageField(default='imagenesUsuarios/usuario.png')

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
            'imagen',
        )


class NotificacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Notificacion
        fields = '__all__'


class IdeaSerializer(serializers.ModelSerializer):
    imagen = Base64ImageField()

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
            'estado',  #Poner como read only y agregar campo is_activa por separado
            'imagen',
            'usuario',
            'categoria',
            'imagenUsuario',
            'usuario'
        )
        read_only_fields = ['monto_actual','imagenUsuario','usuario', 'imagen']

    def validate(self, data):
        instance = models.Idea(**data)
        instance.clean()
        return data


class CategoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Categoria
        fields = (
            'id',
            'nombre'
        )


class InversionSerializer(serializers.ModelSerializer):
    reembolso = serializers.ReadOnlyField()
    estadoIdea = serializers.ReadOnlyField()
    usuario = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = models.Inversion
        fields = (
            'id',
            'fecha_inversion',
            'monto_invertido',
            'reembolso',
            'usuario',
            'idea',
            'estadoIdea'
        )  

    def validate(self, data):
        instance = models.Inversion(**data)
        instance.clean()
        return data