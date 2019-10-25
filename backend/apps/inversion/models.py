from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from datetime import date
from django.core.exceptions import ValidationError
from django.db.transaction import atomic

class User(AbstractUser):
    saldo = models.PositiveIntegerField(
        default=0, 
        validators=[
            MinValueValidator(0),
        ]
    )
    imagen = models.ImageField(
        upload_to='imagenesUsuarios/', 
        default='imagenesUsuarios/usuario.png'
    )

    def __str__(self):
        full_name = self.first_name +" "+ self.last_name
        return full_name

    @classmethod
    def realizarInversion(self, id, monto):
        with atomic():
            account = (
                self.objects
                .select_for_update()
                .get(id=id)
            )
            account.saldo -= monto
            account.save()
        return account


    class Meta:
        db_table = "User"


class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "Categoria"


class PublicaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(estado='P')


class Idea(models.Model):
    fallida = 'F'
    exitosa = 'E'
    publica = 'P'
    inactiva = 'I'
    estadoOpciones = [
        (fallida, 'Fallida'),
        (exitosa, 'Exitosa'),
        (publica, 'Publica'),
        (inactiva, 'Inactiva'),
    ]

    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(
        validators=[
            MaxLengthValidator(150)
        ]
    )
    monto_objetivo = models.PositiveIntegerField(
        validators=[
            MinValueValidator(100000)
        ]
    )
    monto_actual = models.PositiveIntegerField(
        validators = [
            MinValueValidator(0),
        ],
        default=0,
    )
    intereses = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1), 
            MaxValueValidator(50),
        ]
    )
    fecha_publicada = models.DateField(auto_now_add=True)
    fecha_limite = models.DateField()
    fecha_reembolso = models.DateField()
    estado = models.CharField(
        max_length=1,
        choices=estadoOpciones,
        default=publica,
    )
    imagen = models.ImageField(upload_to='imagenesIdeas/')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE
    )

    objects = models.Manager()
    publicas = PublicaManager()

    def __str__(self):
        return self.nombre

    def clean(self):
        self.validarFechas()
        self.validarMontoActual()
        
    def save(self, *args, **kwargs):
        self.clean()
        self.setEstadoExitosa()
        super(Idea, self).save(*args, **kwargs)

    #def setEstadoFallida(self):
    #    if date.today() > self.fecha_limite:
    #        self.estado = 'F'
    #        return 'F'

    def setEstadoExitosa(self):
        if self.monto_actual == self.monto_objetivo:
            self.estado = self.exitosa

    def validarFechas(self):
        if self.fecha_limite > self.fecha_reembolso:
            raise ValidationError(
                "La fecha limite no puede estar después de la fecha de reembolso"
            )

    def validarMontoActual(self):
        if self.monto_actual > self.monto_objetivo:
           raise ValidationError(
                "El monto actual no puede ser mayor al monto objetivo"
            ) 

    @property
    def tiempoRecaudo(self):    
        return self.fecha_limite - self.fecha_publicada

    @classmethod
    def setMontoActual(self, id, monto):
        with atomic():
            account = (
                self.objects
                .select_for_update()
                .get(id=id)
            )
            account.monto_actual += monto
            account.save()
        return account

    class Meta:
        db_table = "Idea"


class Inversion(models.Model):
    fecha_inversion = models.DateField(auto_now_add=True)
    monto_invertido = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    idea = models.ForeignKey(
        Idea, 
        on_delete=models.CASCADE
    )

    @property
    def reembolso(self):
        return round(self.monto_invertido + (self.monto_invertido * (self.idea.intereses / 100)))

    def __str__(self):
        return str(self.id)

    def clean(self):
        self.validarMontoInvertido()
        self.validarUsuario()
        self.validarIdeaEstado()
        
    def save(self, *args, **kwargs):
        self.clean()
        self.transaccion()
        super(Inversion, self).save(*args, **kwargs)

    def validarMontoInvertido(self):
        if self.monto_invertido > self.usuario.saldo:
            raise ValidationError("No tiene saldo suficiente")
        if self.monto_invertido > self.idea.monto_objetivo - self.idea.monto_actual:
            raise ValidationError(
                "La inversión no puede ser mayor a lo que falta para el objetivo."
            )

    def validarUsuario(self):
        if self.usuario == self.idea.usuario:
            raise ValidationError(
                "No puede invertir en su propia idea."
            )
    
    def validarIdeaEstado(self):
        if self.idea.estado != "P":
            raise ValidationError(
                "No se puede invertir en una idea no publicada."
            )

    def transaccion(self):
        self.idea.setMontoActual(self.idea.id, self.monto_invertido)
        self.usuario.realizarInversion(self.usuario.id, self.monto_invertido)

    class Meta:
        db_table = "Inversion"  