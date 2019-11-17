from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from .validators import *
from PIL import Image
from .tasks import revisarSiFallida
from gdstorage.storage import GoogleDriveStorage
from asgiref.sync import async_to_sync
from . import notificaciones

gd_storage = GoogleDriveStorage()

class User(AbstractUser):
    saldo = models.PositiveIntegerField(
        default=0, 
        validators=[
            MinValueValidator(0),
        ]
    )
    imagen = models.ImageField(
        upload_to='imagenesUsuarios/', 
        default='imagenesUsuarios/usuario.png',
        storage=gd_storage,
    )

    @property
    def nombreGrupo(self):
        """
        Returns a group name based on the user's id to be used by Django Channels.
        Example usage:
        user = User.objects.get(pk=1)
        group_name = user.group_name
        """
        return "user_%s" % self.id

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

        # img = Image.open(self.imagen.url) #Abrir imagen
        # if img.height > 150 or img.width > 150:
        #     dimensionMaxima = (150, 150)
        #     img.thumbnail(dimensionMaxima) #Redimensión
        #     img.save(self.imagen.path)

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

    def __str__(self):
        return self.username

    class Meta:
        db_table = "User"


class Notificacion(models.Model):
    nombre = models.CharField(max_length=25)
    texto = models.CharField(max_length=100)
    visto = models.BooleanField(default=False)
    fecha_envio = models.DateField(auto_now_add=True)
    receptor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )

    @classmethod
    def agregarNotificacion(cls, nombre, texto, receptor):
        nuevaNotificacion = cls(
            nombre=nombre,
            texto=texto,
            receptor=receptor,
        )
        nuevaNotificacion.save()


    def __str__(self):
        return self.texto

    class Meta:
        db_table = "Notificacion"


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
        validators=[
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
    imagen = models.ImageField(
        upload_to='imagenesIdeas/',
        storage=gd_storage,
    )
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

    @property ##no iria aqui??
    def tiempoRecaudo(self):    
        return self.fecha_limite - self.fecha_publicada

    # @property 
    # def probabilidadExito(self):    
    #     #llamar funcion con el .predict que me retorne la probabilidad de la idea.

    @property
    def imagenUsuario(self):
        return self.usuario.imagen.url

    def revisarSiExitosa(self):
        if (self.monto_actual == self.monto_objetivo):
            self.estado = self.exitosa
            
    def revisarEstado(self):
        if (self.estado == self.exitosa):
            self.enviarInversionExitosa()
            textoNotificacion = 'Su idea ha sido exitosa y ha recibido las inversiones.'
            async_to_sync(notificaciones.notificacion)(self.usuario, textoNotificacion)
            Notificacion.agregarNotificacion( 
                'Idea Exitosa',
                textoNotificacion,
                self.usuario
            )
        elif ((self.estado == self.fallida or 
               self.estado == self.inactiva) and 
               self.monto_actual > 0): 
            self.enviarInversionFallida() #llamar en variable y en la funcion retornar true o false
            
            if(self.estado == self.fallida):
                textoNotificacion = 'Su idea ha vencido y se han devuelto las inversiones.'
                async_to_sync(notificaciones.notificacion)(self.usuario, textoNotificacion)
                Notificacion.agregarNotificacion( 
                    'Idea Fallida',
                    textoNotificacion,
                    self.usuario
                )
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

        # img = Image.open(self.imagen.path) #Abrir imagen
        # if ((img.height > 300) or (img.width > 300)):
        #     dimensionMaxima = (300, 300)
        #     img.thumbnail(dimensionMaxima) #Redimensión
        #     img.save(self.imagen.path)
        
        crearTarea = False
        if (self.estado == self.publica): #Crear la tarea solo cuando la idea es publicada 
            crearTarea = True #poner la condicion despues del super save para que no se repita

        if (crearTarea):
            revisarSiFallida.apply_async(
                args=[
                    self.__class__.__name__, 
                    self.id
                ], 
                eta=self.fecha_limite
            ) 

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

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "Idea"
        #ordering = "probabilidadExito"


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
        
    def save(self, *args, **kwargs):
        self.clean()
        self.transferir()

        super(Inversion, self).save(*args, **kwargs)
        
        #Validaciones cuando la idea ha sido guardada con el usuario a validar.
        validarUsuarioInversor(self)
        validarMontoInvertido(self)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "Inversion"  