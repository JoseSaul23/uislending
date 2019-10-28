from celery import Celery
from .models import *
app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def setEstadoFallida(id):
    instance = Idea.publicas.get(id=id)
    instance.estado = 'F'
    instance.save()