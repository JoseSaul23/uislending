from .models import *
from datetime import date, datetime
from background_task import background
from background_task.models import Task

fechaInicio = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, hour=6, minute=1)

@background(schedule=fechaInicio)
def recorrerIdeas():
    ideasPublicas = Idea.publicas.all()
    for ideaPublica in ideasPublicas:
        ideaPublica.revisarSiFallida()
        ideaPublica.save()          