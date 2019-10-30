from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import date

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

    def validarFechas(self):
        if self.fecha_limite > self.fecha_reembolso:
            raise ValidationError(
                "La fecha limite no puede estar después de la fecha de reembolso"
            )
        if self.id is None and self.fecha_limite < date.today(): #None, para que solo lo  haga cuando
            raise ValidationError(                               #se inserta por primera vez.
                "La fecha limite no puede estar antes de la fecha de hoy"
            )

    def validarMontoActual(self):
        if self.monto_actual > self.monto_objetivo:
           raise ValidationError(
                "El monto actual no puede ser mayor al monto objetivo"
            ) 

    def enviarInversionExitosa(self):
        self.usuario.recibirDinero(
                self.usuario.id, 
                self.monto_actual,
            )
        self.monto_actual = 0 #solucion temporal??

    def revisarSiExitosa(self):
        if self.monto_actual == self.monto_objetivo:
            self.estado = self.exitosa
    
    # def revisarSiFallida(self):
    #     ideas = Idea.publicas.all()
    #     for idea in ideas:
    #         if idea.fecha_limite < date.today():
    #             idea.estado = 'F'
    #             idea.save()
            
    def revisarEstado(self):
        if self.estado == self.exitosa:
            self.enviarInversionExitosa()
        elif self.estado == self.fallida and self.monto_actual > 0: 
            inversiones = Inversion.objects.filter(idea=self)
            for inversion in inversiones: 
                inversion.devolucion()
            self.monto_actual = 0  #solucion temporal??
            pass
        else:
            pass

    def clean(self):
        self.validarFechas()
        self.validarMontoActual() #solo se puede borrar una idea si esta inactiva,fallida o exitosa
        
    def save(self, *args, **kwargs):
        self.clean()
        self.revisarSiExitosa()
        self.revisarEstado()

        # create_task = False
        # if self.id is None and self.estado == self.publica:
        #     # quitar condicion para que sea tambien en caso de modificacion
        #     create_task = True # set the variable 

        super(Idea, self).save(*args, **kwargs)

        # create_task = True
        # if create_task: 
        #     setEstadoFallida.apply_async(args=[self.id], eta=self.fecha_limite)

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
            self.monto_invertido+(self.monto_invertido*(self.idea.intereses/100))
        )

    def __str__(self):
        return str(self.id)

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
    
    def validarEstadoIdea(self):
        if self.idea.estado != "P":
            raise ValidationError(
                "No se puede invertir en una idea no publicada."
            )

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
            ) #borrar inversion una vez hecha la devolucion, volver a pagare?
            
    def clean(self):
        self.validarEstadoIdea()
        self.validarUsuario()
        self.validarMontoInvertido()
        
    def save(self, *args, **kwargs):
        self.clean()
        self.transferir()
        super(Inversion, self).save(*args, **kwargs)

    class Meta:
        db_table = "Inversion"  