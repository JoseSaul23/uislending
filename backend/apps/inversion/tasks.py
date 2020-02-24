from datetime import date, datetime
from celery import shared_task
from django.apps import apps 

@shared_task
def revisarSiFallida(cls, id): #renombrar ideaTarea y llamar revisarSiFallida como metodo del modelo.
    modeloIdea = apps.get_model('inversion.{}'.format(cls))
    objetoIdea = modeloIdea.objects.get(id=id)
    objetoIdea.estado = 'F'
    objetoIdea.save()
       