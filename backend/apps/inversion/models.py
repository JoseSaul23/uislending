from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    saldo = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='imagenesUsuarios/', default='imagenesUsuarios/usuario.png')
    def __str__(self):
        full_name = self.first_name +" "+ self.last_name
        return full_name
    class Meta:
        db_table = "User"

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre
    class Meta:
        db_table = "Categoria"

class Idea(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(max_length=120)
    monto_objetivo = models.PositiveIntegerField(validators=[MinValueValidator(100000)])
    monto_actual = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    intereses = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)])
    fecha_publicada = models.DateField(auto_now_add=True)
    fecha_limite = models.DateField()
    fecha_reembolso = models.DateField()
    estado = models.CharField(max_length=20)
    imagen = models.ImageField(upload_to='imagenesIdeas/')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre
    class Meta:
        db_table = "Idea"
    #definir calculo de tiempo activo

class Inversion(models.Model):
    fecha_inversion = models.DateField(auto_now_add=True)
    monto_invertido = models.IntegerField(validators=[MinValueValidator(1)])
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    def __str__(self):
        return self.idea,self.fecha_inversion
    class Meta:
        db_table = "Inversion"  
    #definir monto mas intereses