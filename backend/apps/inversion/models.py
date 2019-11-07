from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import date, datetime
from background_task import background
from .validators import *
from PIL import Image


class User(AbstractUser):
    saldo = models.PositiveIntegerField(
        default=0, 
        validators=[
            MinValueValidator(0),
        ]
    )
    imagen = models.ImageField( #redimensionar imagenes
        upload_to='imagenesUsuarios/', 
        default='imagenesUsuarios/usuario.png'
    )

    def __str__(self):
        full_name = self.first_name +" "+ self.last_name
        return full_name

    @classmethod
    def retirarDinero(cls, id, dinero):
        with transaction.atomic():
            UserAccount = (
                cls.objects
                .select_for_update()
                .get(id=id)
            )
            if UserAccount.saldo < dinero:
                raise ValidationError("No tiene saldo suficiente")
            UserAccount.saldo -= dinero
            UserAccount.save()
       
    @classmethod
    def recibirDinero(cls, id, dinero):
        with transaction.atomic():
            account = (
                cls.objects
                .select_for_update()
                .get(id=id)
            )
            account.saldo += dinero
            account.save()

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
        related_name='ideas',
        on_delete=models.CASCADE
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE
    )

    objects = models.Manager()
    publicas = PublicaManager()

    @property
    def tiempoRecaudo(self):    
        return self.fecha_limite - self.fecha_publicada

    @property
    def imagenUsuario(self):
        return "http://saulvega.pythonanywhere.com"+self.usuario.imagen.url

    def __str__(self):
        return self.nombre

    def revisarSiExitosa(self):
        if (self.monto_actual == self.monto_objetivo):
            self.estado = self.exitosa
    
    def revisarSiFallida(self):
        if (self.fecha_limite < date.today()):
            self.estado = self.fallida
            
    def revisarEstado(self):
        if (self.estado == self.exitosa):
            self.enviarInversionExitosa()
        elif ((self.estado == self.fallida or 
               self.estado == self.inactiva) and 
               self.monto_actual > 0): 
            self.enviarInversionFallida() #tambien si idea inactiva.
        else:
            pass
    
    def enviarInversionExitosa(self):
        with transaction.atomic():
            self.usuario.recibirDinero(
                    self.usuario.id, 
                    self.monto_actual,
                )
            self.monto_actual = 0 #solucion temporal??

    def enviarInversionFallida(self):
        inversiones = Inversion.objects.filter(idea=self)
        for inversion in inversiones: 
            inversion.devolucion()
        self.monto_actual = 0 #solucion temporal??

    def clean(self):
        validarFechas(self)
        validarMontoActual(self)


    def save(self, *args, **kwargs):
        self.clean()
        self.revisarSiExitosa()
        self.revisarEstado()
        
        super(Idea, self).save(*args, **kwargs)
        #redimensionarImagen(obj, height, width)
        img = Image.open(self.imagen.path) #Abrir imagen
        if img.height > 300 or img.width > 300:
            dimensionMaxima = (300, 300)
            img.thumbnail(dimensionMaxima) #Redimensión
            img.save(self.imagen.path)


    @classmethod
    def recibirMonto(cls, id, monto):
        with transaction.atomic():
            account = (
                cls.objects
                .select_for_update()
                .get(id=id)
            )
            if monto > account.monto_objetivo - account.monto_actual:
                raise ValidationError(
                    "La inversión no puede ser mayor a lo que falta para el objetivo."
                )
            account.monto_actual += monto
            account.save()
        return account

    @classmethod  #no usado por ahora
    def retirarMonto(cls, id, monto):
        with transaction.atomic():
            account = (
                cls.objects
                .select_for_update()
                .get(id=id)
            )
            account.monto_actual -= monto
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
        return round(
            self.monto_invertido + (self.monto_invertido * (self.idea.intereses/100))
        )
    
    @property
    def estadoIdea(self):
        return self.idea.estado

    def __str__(self):
        return str(self.id)
    
    def transferir(self):
        with transaction.atomic():
            self.usuario.retirarDinero(
                self.usuario.id, 
                self.monto_invertido,
            )
            self.idea.recibirMonto(
                self.idea.id,
                self.monto_invertido,
            )

    def devolucion(self):
       with transaction.atomic():
            self.usuario.recibirDinero(
                self.usuario.id, 
                self.monto_invertido,
            )
            self.idea.retirarMonto(
                self.idea.id,
                self.monto_invertido,
            )
            self.delete()
     
    def clean(self):
        validarEstadoIdea(self)
        validarUsuarioInversor(self)
        validarMontoInvertido(self)
        
    def save(self, *args, **kwargs):
        self.clean()
        self.transferir()
        super(Inversion, self).save(*args, **kwargs)

    class Meta:
        db_table = "Inversion"  